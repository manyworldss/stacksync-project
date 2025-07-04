# Python Execution Service

A secure service that executes Python code in a sandboxed environment.

## Features

- Execute Python code in a secure environment
- Returns the result of the `main()` function
- Includes stdout in the response
- Containerized with Docker

## Prerequisites

- Docker
- Python 3.9+

## Local Development

1. Build the Docker image:
   ```bash
   docker build -t python-execution-service .
   ```

2. Run the container:
   ```bash
   docker run -p 8080:8080 python-execution-service
   ```

3. Test the service:
   ```bash
   curl http://localhost:8080/health
   ```

## API Endpoints

### POST /execute
Execute a Python script.

**Request Body:**
```json
{
    "script": "def main():\n    return {'hello': 'world'}"
}
```

**Response:**
```json
{
    "result": {"hello": "world"},
    "stdout": ""
}
```

## Deployment

Deploy to Google Cloud Run using the provided Dockerfile.
