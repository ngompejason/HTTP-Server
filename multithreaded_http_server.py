import socket
import http.client
import os
import threading
import mimetypes


class TCPServer:
    def __init__(self, host='127.0.0.1', port=8080):
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
            server_socket.listen(5)
            #print the addr of the server (ip addr and port)
            print("Listening at", server_socket.getsockname())

            while True:
                client_socket, client_addr = server_socket.accept()
                print("Connected by", client_addr)
                client_thread = threading.Thread(target = self.handle_client, args=(client_socket,))
                client_thread.start()

    def handle_client(self, socket):
            with socket:
                data = socket.recv(1024)
                if data:
                    response = self.handle_request(data)
                    socket.sendall(response)

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
        elif request.method == "POST":
            pass
        else:
            response = self.handle_501_HTTP(request)
        
        response
        return response
    
    def handle_501_HTTP(self, request):
        "Handle request that have not yet been implemented"

        response_line = self.response_line(status_code=501)

        headers_reponse = self.header_lines()

        blank_line = b"\r\n"

        response_body = b"""<h1> NOt IMpleMenTeD YeT<h1>"""

        return b"".join([response_line, headers_reponse, blank_line, response_body])

    def handle_GET(self, request):
        """Handle the GET request and send a response depending on the uri"""
        filename = request.uri.strip("/")
        if filename == "":
            filename = "index.html"

        if os.path.exists(filename):
            with open(file=filename, mode="rb") as file:
                response_body = file.read()

            content_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            file_size = len(response_body)
            
            response_line = self.response_line(status_code=200)
            extra_headers = {
                'Content-Type': content_type,
                'Content-Length': file_size,
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

    def response_line(self, status_code):
        """"Returns the response line of the HTTP response"""
        #get the reason phrase of the given status_code
        reason_phrase = http.client.responses.get(status_code, "Unknown Status Code")
        #construst the response line
        line = f"HTTP/1.1 {status_code} {reason_phrase}"

        return line.encode()#encode it to byte
    
    def header_lines(self, extra_headers=None):
        """Returns headers
        The `extra_headers` can be a dict for sending 
        extra headers for the current response
        """
        headers_copy = self.headers.copy() # make a local copy of headers

        if extra_headers:
            headers_copy.update(extra_headers)

        headers = ""

        for h in headers_copy:
            headers += f"{h}: {headers_copy[h]}\r\n" 

        return headers.encode() # call encode to convert str to bytes

class HTTPRequest:
    def __init__(self, data):
        self.method = None
        self.uri = None
        self.http_version = "1.1" # default to HTTP/1.1 if request doesn't provide a version

        # call self.parse() method to parse the request data
        self.parse(data)

    def parse(self, data):
        lines = data.split(b"\r\n")

        request_line = lines[0]
        
        words = request_line.split(b" ")

        self.method = words[0].decode() # call decode to convert bytes to str

        if len(words) > 1:
            # we put this in an if-block because sometimes 
            # browsers don't send uri for homepage
            self.uri = words[1].decode() # call decode to convert bytes to str

        if len(words) > 2:
            self.http_version = words[2]



if __name__ == "__main__":

    server = HTTPServer()
    server.run_forever()