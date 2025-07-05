# Python Code Execution Service

This project is a Python Code Execution Service that allows users to execute Python scripts securely in a sandboxed environment.

## Deployment

The service has been deployed on Fly.io. You can access it at - https://stacksync-project.fly.dev/

## Running Locally

To run the service locally:

1. Ensure Python 3.11 is installed.
2. Create and activate a virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Run the service with `python app.py`.

## API Endpoints

- `GET /health`: Check service health.
- `POST /execute`: Execute Python code.

## Testing

Use `test_simple.py` to run tests against the service.




Thank you for reviewing the project!

This project is a simple Flask API that runs Python scripts safely using nsjail sandboxing.

## How to Run Locally

1. Build the Docker image:
```bash
docker build -t python-execution-service .
```

2. Run the Docker container:
```bash
docker run -p 8080:8080 python-execution-service
```

3. Access the service at `http://localhost:8080`.

## API Endpoints

- `GET /health`: Check if the service is running.
- `POST /execute`: Send a JSON body with a Python script containing a `main()` function.

Example request body:
```json
{
  "script": "def main():\n    return {\"message\": \"Hello World\"}"
}
```

Example cURL command:
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"script": "def main():\n    return {\"message\": \"Hello World\"}"}'
```

## Notes

- The `main()` function must return a JSON-serializable object.
- Print statements output will be captured separately.
- The service uses nsjail for security and resource limits.
- Only basic libraries like os, pandas, and numpy are available.

## Deployment

You can deploy this Docker image to Google Cloud Run or any container platform.

## Testing

Use the provided `test_simple.py` script to test the API endpoints.

This README is simplified for easier understanding and use.
