from main import app

import logging

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Starting Flask app...")
    try:
        app.run(host='0.0.0.0', port=8080, debug=True)
    except Exception as e:
        logging.error(f"Failed to start Flask app: {e}")

    