#!/usr/bin/env python3

from flask import Flask, request, jsonify
import subprocess
import json
import tempfile
import os
import logging
from pathlib import Path

# Initialize Flask application
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants
NSJAIL_PATH = "/usr/bin/nsjail"  # Path to nsjail binary for sandboxing
PYTHON_PATH = "/usr/bin/python3"  # Path to Python interpreter
TIMEOUT = 30  # Maximum execution time in seconds
MAX_OUTPUT_SIZE = 1024 * 1024  # Maximum output size (1MB)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify service status"""
    return jsonify({
        "status": "healthy",
        "message": "Python Code Execution Service is running"
    }), 200

@app.route('/execute', methods=['POST'])
def execute_script():
    """Endpoint to execute user-provided Python script in sandbox"""
    try:
        # Validate request content type
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        # Validate presence of 'script' field
        if not data or 'script' not in data:
            return jsonify({"error": "Missing 'script' field in request body"}), 400
        
        script = data['script']
        # Validate script type
        if not isinstance(script, str):
            return jsonify({"error": "'script' must be a string"}), 400
        
        # Limit script size to 100KB
        if len(script) > 100000:
            return jsonify({"error": "Script too large (max 100KB)"}), 400
        
        # Ensure script contains a main() function
        if 'def main(' not in script:
            return jsonify({"error": "Script must contain a 'main()' function"}), 400
        
        # Execute the script inside sandbox
        result = execute_in_sandbox(script)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def execute_in_sandbox(script):
    """Execute the given Python script securely using nsjail sandbox"""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Paths for user script and wrapper
        script_path = os.path.join(temp_dir, "user_script.py")
        wrapper_path = os.path.join(temp_dir, "wrapper.py")
        
        # Wrapper script to execute user script and capture output
        wrapper_script = f'''#!/usr/bin/env python3
import sys
import json
import io
import contextlib

# User provided script
{script}

# Execution wrapper
if __name__ == "__main__":
    try:
        # Capture stdout output
        stdout_buffer = io.StringIO()
        
        with contextlib.redirect_stdout(stdout_buffer):
            # Verify main() function exists and is callable
            if 'main' not in globals() or not callable(main):
                result = {{"error": "No callable 'main()' function found"}}
            else:
                # Call main() and capture result
                main_result = main()
                
                # Check if result is JSON serializable
                try:
                    json.dumps(main_result)
                    result = {{
                        "result": main_result,
                        "stdout": stdout_buffer.getvalue()
                    }}
                except (TypeError, ValueError):
                    result = {{
                        "error": "main() must return a JSON-serializable object",
                        "stdout": stdout_buffer.getvalue()
                    }}
        
        # Print JSON result
        print(json.dumps(result))
        
    except Exception as e:
        # Handle exceptions and include stdout
        error_result = {{
            "error": str(e),
            "stdout": stdout_buffer.getvalue() if 'stdout_buffer' in locals() else ""
        }}
        print(json.dumps(error_result))
        sys.exit(1)
'''
        
        # Write wrapper script to file
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_script)
        
        # Make wrapper executable
        os.chmod(wrapper_path, 0o755)
        
        # Prepare nsjail command for sandboxed execution
        nsjail_cmd = [
            NSJAIL_PATH,
            '--mode', 'o',  # Run once and exit
            '--chroot', '/',  # Root filesystem
            '--user', 'nobody',  # Drop privileges
            '--group', 'nogroup',
            '--time_limit', str(TIMEOUT),  # CPU time limit
            '--max_cpus', '1',  # Limit to 1 CPU
            '--rlimit_as', '128',  # Address space limit (128MB)
            '--rlimit_cpu', str(TIMEOUT),  # CPU time limit
            '--rlimit_nofile', '32',  # Max open files
            '--disable_proc',  # Disable /proc
            '--iface_no_lo',  # Disable loopback interface
            '--quiet',  # Suppress nsjail output
            '--bindmount', f'{temp_dir}:{temp_dir}',  # Bind temp dir
            '--bindmount', '/usr/lib:/usr/lib:ro',  # Read-only mounts
            '--bindmount', '/usr/bin/python3:/usr/bin/python3:ro',
            '--bindmount', '/lib:/lib:ro',
            '--bindmount', '/lib64:/lib64:ro',
            '--',
            PYTHON_PATH,
            wrapper_path
        ]
        
        try:
            # Run the sandboxed process
            process = subprocess.run(
                nsjail_cmd,
                capture_output=True,
                text=True,
                timeout=TIMEOUT + 5
            )
            
            if process.returncode == 0:
                # Parse and return JSON output
                try:
                    return json.loads(process.stdout.strip())
                except json.JSONDecodeError:
                    return {
                        "error": "Failed to parse execution result",
                        "stdout": process.stdout,
                        "stderr": process.stderr
                    }
            else:
                # Handle errors from execution
                try:
                    error_result = json.loads(process.stdout.strip())
                    return error_result
                except json.JSONDecodeError:
                    return {
                        "error": f"Script execution failed (exit code: {process.returncode})",
                        "stdout": process.stdout,
                        "stderr": process.stderr
                    }
        
        except subprocess.TimeoutExpired:
            return {"error": f"Script execution timed out after {TIMEOUT} seconds"}
        except Exception as e:
            return {"error": f"Sandbox execution failed: {str(e)}"}

if __name__ == '__main__':
    # Startup messages
    print("Starting Python Code Execution Service...")
    print("Server will be available at: http://0.0.0.0:8080")
    print("Health check: http://0.0.0.0:8080/health")
    print("Execute endpoint: POST http://0.0.0.0:8080/execute")
    # Run Flask app
    app.run(host='0.0.0.0', port=8080, debug=False)