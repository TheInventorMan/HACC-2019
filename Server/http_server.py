#!/usr/bin/env python

from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
import shutil
import os
import main
# HTTPRequestHandler class
class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):

    # GET (audio)
    def do_GET(self):
        # Send response status code
        self.send_response(200)
        # Send headers
        self.send_header('Content-type', 'audio/wav')
        self.end_headers()
        # # Send message back to client
        # message = "Hello world!"
        # # Write content as utf-8 data
        # self.wfile.write(bytes(message, "utf8"))
        with open('chime.wav', 'rb') as content:
            shutil.copyfileobj(content, self.wfile)
        return

    # POST (image, audio)
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())
        return

    def do_PUT(self):
        """Save a file following a HTTP PUT request"""
        filename = os.path.basename(self.path)
        file_length = int(self.headers['Content-Length'])

        if filename == "image.jpg":
            with open(filename, 'wb') as output_file:
                output_file.write(self.rfile.read(file_length))
            self.send_response(200, 'Awaiting audio')
            self.end_headers()
            return

        elif filename == "command.wav":
            with open(filename, 'wb') as output_file:
                output_file.write(self.rfile.read(file_length))

            main.exec("command.wav", "image.jpg")

            self.send_response(201, 'Done')
            self.end_headers()
            with open('resp.wav', 'rb') as content:
                shutil.copyfileobj(content, self.wfile)
            return
        else:
            self.send_response(401, 'Invalid fname')
            self.end_headers()


def run():
    print('starting server...')
    # Server settings
    # Choose port 8080, for port 80, which is normally used for a http server, you need root access
    server_address = ('18.20.246.54', 8081)
    httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
    print('running server...')
    httpd.serve_forever()

run()
