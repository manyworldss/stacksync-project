from flask import Flask, request, jsonify
import io
import contextlib
import json

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/execute', methods=['POST'])
def execute_script():
    try:
        # Get the script from the request
        data = request.get_json()
        if not data or 'script' not in data:
            return jsonify({"error": "No script provided"}), 400

        script = data['script']
        
        # Check if script contains a main function
        if 'def main(' not in script:
            return jsonify({"error": "Script must contain a 'main()' function"}), 400

        # Create a new output buffer
        output_buffer = io.StringIO()
        
        # Execute the script in a new namespace
        namespace = {}
        
        # Redirect stdout to our buffer
        with contextlib.redirect_stdout(output_buffer):
            try:
                # Execute the script
                exec(script, namespace)
                
                # Check if main function exists and call it
                if 'main' not in namespace or not callable(namespace['main']):
                    return jsonify({"error": "No callable 'main()' function found"}), 400
                
                # Call the main function and get the result
                result = namespace['main']()
                
                # Convert the result to JSON
                try:
                    json.dumps(result)  # Test if result is JSON serializable
                    return jsonify({
                        "result": result,
                        "stdout": output_buffer.getvalue()
                    })
                except (TypeError, OverflowError):
                    return jsonify({
                        "error": "main() must return a JSON-serializable object",
                        "stdout": output_buffer.getvalue()
                    }), 400
                    
            except Exception as e:
                return jsonify({
                    "error": str(e),
                    "stdout": output_buffer.getvalue()
                }), 400
                
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)