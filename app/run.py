import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.main import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

    