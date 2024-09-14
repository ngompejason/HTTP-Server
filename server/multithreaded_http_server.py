import socket
import http.client
import os
import threading
import mimetypes
import logging
import gzip
from config import WEB_ROOT, HOST, PORT, MAX_CONNECTIONS, LOG_FILE, LOG_LEVEL

logging.basicConfig(
    filename=LOG_FILE,
    level=getattr(logging, LOG_LEVEL.upper(), logging.INFO),
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class TCPServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port



    def run_forever(self):
        #create the socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            #allows the socket to reuse a local address port after the socket has benn closed
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #bind the socket to an IP addr and port
            server_socket.bind((self.host, self.port))
            #put the socket in listening mode for any new connection
            server_socket.listen(MAX_CONNECTIONS)
            #print the addr of the server (ip addr and port)
            logging.info(f"Server started on {self.host}:{self.port}")

            while True:
                client_socket, client_addr = server_socket.accept()
                logging.info(f"Connection from {client_addr}")
                client_thread = threading.Thread(target = self.handle_client, args=(client_socket,))
                client_thread.start()


    def handle_client(self, client_socket):
        """Handle each client request."""
        with client_socket:
            try:
                data = client_socket.recv(1024)
                if data:
                    response = self.handle_request(data)
                    client_socket.sendall(response)
                    logging.info(f"Request handled successfully")
            except Exception as e:
                logging.error(f"Error handling request: {e}")

    def handle_request(self, data):
        """Handles incoming data and returns a response.
        Override this in subclass.
        """
        return data
    
class HTTPServer(TCPServer):
    
    headers = {
        'Server': '3x7Server',
        'Content-Type': 'text/html',
    }

    def handle_request(self, data):
        """Handles the incoming request. Compiles and returns the response"""
        request = HTTPRequest(data)

        if request.method == "GET":
            response = self.handle_GET(request)
        elif request.method == "POST": # Not implemented
            response = self.handle_405_method_not_allowed(request)  
        else:
            response = self.handle_501_HTTP(request)
        
        logging.info(f"Handled {request.method} request for {request.uri}")
        return response
    
    def handle_405_method_not_allowed(self, request):
        logging.warning(f"405 Method Not Allowed: {request.method} for {request.uri}")
        response_line = self.response_line(status_code=405)
        headers_response = self.header_lines({'Allow': 'GET'})
        blank_line = b"\r\n"
        response_body = b"<h1>405 Method NOt Allowed</h1>"
        return b"".join([response_line, headers_response, blank_line, response_body])

    
    def handle_501_HTTP(self, request):
        "Handle request that have not yet been implemented"
        logging.warning(f"501 Not Implemented: {request.method} for {request.uri}")
        response_line = self.response_line(status_code=501)
        headers_reponse = self.header_lines()
        blank_line = b"\r\n"
        response_body = b"""<h1>501 NOt Implemented Yet<h1>"""
        return b"".join([response_line, headers_reponse, blank_line, response_body])

    def handle_GET(self, request):
        """Handle the GET request and send a response depending on the uri"""
        filename = request.uri.strip("/")
        if filename == "":
            filename = "index.html"

        # Restrict access to files only within the public directory
        # Ensure the requested file is within the WEB_ROOT directory
        file_path = os.path.join(WEB_ROOT, filename)
        normalized_path = os.path.normpath(file_path)
        
        logging.info(f"Requested file: {normalized_path}")
        
        if not normalized_path.startswith(WEB_ROOT):
            logging.warning(f"403 Forbidden: Attempted access to {normalized_path}")
            return self.handle_403_forbidden()
        
        if os.path.exists(normalized_path) and os.path.isfile(normalized_path):
            try:
                with open(normalized_path, mode="rb") as file:
                    response_body = file.read()
                    logging.info(f"Successfully read file: {normalized_path}")
            except IOError as e:
                logging.error(f"Error reading file: {e}")
                return self.handle_500_internal_server_error()
            
            response_line = self.response_line(status_code=200)
            
            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            
            
            # Compress the response if it's compressible
            if self.is_compressible(content_type):
                response_body = gzip.compress(response_body)
                extra_headers = {
                    'Content-Encoding': 'gzip'
                }
                logging.info(f"Compressed response for {filename}")
            else:
                extra_headers = {}

            extra_headers = {
                'Content-Type': content_type,
                'Content-Length': len(response_body),
                'Connection': 'close'
            }
            header_response = self.header_lines(extra_headers)
        else:
            response_line = self.response_line(status_code=404)
            response_body = b"<h1>404 Page Not Found</h1>"
            extra_headers = {
                'Content-Type': 'text/html',
                'Content-Length': len(response_body),
                'Connection': 'close'
            }
            header_response = self.header_lines(extra_headers)
        blank_line = b"\r\n"
        return b"".join([response_line, header_response, blank_line, response_body])

    def handle_404_not_found(self):
        response_line = self.response_line(status_code=404)
        response_body = b"<h1>404 Page Not Found</h1>"
        extra_headers = {
            'Content-Type': 'text/html',
            'Content-Length': len(response_body),
            'Connection': 'close'
        }
        header_response = self.header_lines(extra_headers)
        blank_line = b"\r\n"
        return b"".join([response_line, header_response, blank_line, response_body])

    def handle_403_forbidden(self):
        response_line = self.response_line(status_code=403)
        response_body = b"<h1>403 Forbidden</h1>"
        extra_headers = {
            'Content-Type': 'text/html',
            'Content-Length': len(response_body),
            'Connection': 'close'
        }
        header_response = self.header_lines(extra_headers)
        blank_line = b"\r\n"
        return b"".join([response_line, header_response, blank_line, response_body])


    def handle_500_internal_server_error(self):
        logging.error("500 Internal Server Error")
        response_line = self.response_line(status_code=500)
        response_body = b"<h1>500 Internal Server Error</h1>"
        extra_headers = {
            'Content-Type': 'text/html',
            'Content-Length': len(response_body),
            'Connection': 'close'
        }
        header_response = self.header_lines(extra_headers)
        blank_line = b"\r\n"
        return b"".join([response_line, header_response, blank_line, response_body])


    def response_line(self, status_code):
        """"Returns the response line of the HTTP response"""
        #get the reason phrase of the given status_code
        reason_phrase = http.client.responses.get(status_code, "Unknown Status Code")
        #construst the response line
        line = f"HTTP/1.1 {status_code} {reason_phrase}"
        #encode it to byte
        return line.encode()
    
    def header_lines(self, extra_headers=None):
        """Returns headers. The `extra_headers` is a dict for sending extra headers for the current response
        """
        # make a local copy of headers
        headers_copy = self.headers.copy()
        if extra_headers:
            headers_copy.update(extra_headers)
        headers = ""
        for h in headers_copy:
            headers += f"{h}: {headers_copy[h]}\r\n" 
        return headers.encode() # call encode to convert str to bytes

    def is_compressible(self, content_type):
        compressible_types = ['text/', 'application/javascript', 'application/json', 'application/xml']
        return any(content_type.startswith(t) for t in compressible_types)


class HTTPRequest:
    def __init__(self, data):
        self.method = None
        self.uri = None
        # default to HTTP/1.1 if request doesn't provide a version
        self.http_version = "1.1" 
        # call self.parse() method to parse the request data
        self.parse(data)

    def parse(self, data):
        lines = data.split(b"\r\n")
        request_line = lines[0]
        words = request_line.split(b" ")
        # call decode to convert bytes to str
        self.method = words[0].decode() 
        if len(words) > 1:
            # we put this in an if-block because sometimes 
            # browsers don't send uri for homepage
            self.uri = words[1].decode() # call decode to convert bytes to str
        if len(words) > 2:
            self.http_version = words[2].decode()
        logging.info(f"Parsed request: Method={self.method}, URI={self.uri}, HTTP Version={self.http_version}")



if __name__ == "__main__":
    logging.info("Starting HTTP Server")
    server = HTTPServer()
    server.run_forever()