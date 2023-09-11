# Ball Tracking Server-Client Application

This project comprises two server-client applications. Both accomplish the same functionality: the server streams a video of a bouncing ball to the client, which then processes the video to detect the ball's position and sends the coordinates back to the server. One version utilizes `asyncio` for an open connection, while the other utilizes a TCP socket connection with `aiortc`.

## Directory Structure

### Server & Client Files:
- `server_asyncio.py`: Server using `asyncio` for open connection.
- `client_asyncio.py`: Client corresponding to the `asyncio` server.
- `server_socket.py`: Server using TCP socket connection with `aiortc`.
- `client_socket.py`: Client corresponding to the socket server.

### Docker:
- `/docker`: Contains the Dockerfile to containerize the server-client applications.

### Kubernetes:
- `kubernetes-deployment.yml`: Kubernetes deployment configurations.

### Virtual Environment:
- `/nimble`: A Python virtual environment (`venv`) using Python 3.10.

### Dependencies:
- `requirements.txt`: Lists the Python packages required to run the applications.

### Miscellaneous:
- `video.mp4`: A video showcasing the deliverables in action.
- `candidate.txt`: Contains details about the developer.
- `pytest.py`: Contains unit tests for the applications.

## Setup & Running

### Docker
- To build a Docker image for the applications:
```bash
cd docker
docker build -t ball-tracking-app .
```

## Python Environment
- To set up the Python virtual environment:
```bash
source nimble/bin/activate
pip install -r requirements.txt
```

# Server-client asyncio
```bash
python server_asyncio.py
python client_asyncio.py
```

# Server-client aiortc
```bash
python server_aiortc.py
python client_aiortc.py
```

## Kubernetes deployment
- kubectl apply -f kubernetes-deployment.yml

## Running tests (Mock tests written for the asyncio version of server-client pair)
```bash
pytest pytest_server.py
pytest pytest_client.py
```



