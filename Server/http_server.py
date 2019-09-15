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
        self.send_response(404)
        # Send headers
        self.end_headers()
        return

    # POST (image, audio)
    def do_POST(self):
        self.send_response(204)
        self.end_headers()
        return

    def do_PUT(self):
        """Save a file following a HTTP PUT request"""
        filename = os.path.basename(self.path)
        file_length = int(self.headers['Content-Length'])

        if filename[-4:] == ".jpg":
            with open(filename, 'wb') as output_file:
                output_file.write(self.rfile.read(file_length))
            self.send_response(200, 'Awaiting audio')
            self.end_headers()
            return

        elif filename[-4:] == ".wav":
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
