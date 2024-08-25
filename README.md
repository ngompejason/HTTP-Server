# Multithreaded HTTP Server

Yo, this is a simple, multithreaded HTTP server implemented from Scratch in Python. It's capable of handling multiple client connections concurrently and serving static files.

## Features

- Multithreaded: Can handle multiple client connections simultaneously
- Supports GET requests
- Serves static files (HTML, images, etc.)
- Basic error handling (404 Not Found, 501 Not Implemented)
- Content-Type detection based on file extensions

## Requirements

- Python 3.x

## Usage

1. Clone the repository or download the `multithreaded_http_server.py` file.

2. Run the server:
   ```python
   python multithreaded_http_server.py
   ```
3. By default, the server will start on `127.0.0.1:8080`. You can modify the host and port in the `__main__` section of the script if needed.

4. Access the server through a web browser or HTTP client at `http://127.0.0.1:8080`

## Structure

The server is composed of several classes:

- `TCPServer`: Base class for TCP socket operations
- `HTTPServer`: Extends `TCPServer` to handle HTTP-specific operations
- `HTTPRequest`: Parses incoming HTTP requests

## Limitations

- Only supports GET requests (POST, PUT, DELETE, etc. are not implemented)
- No support for HTTPS
- Limited error handling and logging
- No built-in security features

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check [issues page](https://github.com/ngompejason/HTTP-Server/issues) if you want to contribute.
