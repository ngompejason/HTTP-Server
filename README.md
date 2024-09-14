# Multithreaded HTTP Server

Yo, this is a simple, multithreaded HTTP server implemented from scratch in Python. It's capable of handling multiple client connections concurrently and serving static files.

## Features

- **Multithreaded:** Handles multiple client connections simultaneously.
- **Supports GET Requests:** Processes HTTP GET requests.
- **Serves Static Files:** Delivers HTML, images, and other static content.
- **Basic Error Handling:** Includes responses for 404 Not Found, 501 Not Implemented, 403 Forbidden, and 500 Internal Server Error.
- **Content-Type Detection:** Automatically determines content type based on file extensions.
- **GZIP Compression:** Compresses responses for certain file types to improve performance.

## Requirements

- Python 3.x

## Usage

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/ngompejason/HTTP-Server.git && cd HTTP-Server
   ```
2. **Run the Server:**

   ```bash
   python server/multithreaded_http_server.py
   ```
3. Access the Server:

By default, the server will start on 127.0.0.1:8080. You can modify the host and port in the __main__ section of the script if needed. Access the server through a web browser or HTTP client at http://127.0.0.1:8080.

## Structure
The server is composed of several classes:

- `TCPServer`: Base class for TCP socket operations.
- `HTTPServer`: Extends `TCPServer` to handle HTTP-specific operations.
- `HTTPRequest`: Parses incoming HTTP requests.

## Limitations

Only Supports GET Requests: POST, PUT, DELETE, etc. are not implemented.
No HTTPS Support: The server does not handle HTTPS.
Limited Error Handling and Logging: Basic error handling is implemented.
No Built-In Security Features: Basic security features are not included.

## Contributing
Contributions, issues, and feature requests are welcome.
