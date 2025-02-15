from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from src.speechrequest import SpeechRequest

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.switch_route()

        # self.send_response(200)
        # self.send_header("Content-type", "text/html")
        # self.end_headers()
        # self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        # self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        # self.wfile.write(bytes("<body>", "utf-8"))
        # self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        # self.wfile.write(bytes("</body></html>", "utf-8"))

    def switch_route(self):
        path = self.path
        if path == "/v1/audio/speech":
            self.do_speech_action()
        else:
            # it's a 404
            self.do_404_action()

    def do_speech_action(self):
        if self.command == "GET":
            speech = SpeechRequest("am_adam")
            result = speech.request_audio_for("This is default text for testing")
            print(result)
            print(self.request)
            # parse request
            # read json file
            # proxy request to get speech
            # return speech mp3 ?
            print("do_speech_action")
            self.send_response(400)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes("invalid content type").encode(encoding="utf_8"))
            return


        if self.headers.get_content_type != "application/json":
            self.send_response(400)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes("invalid content type"))
            return
        
        speech = SpeechRequest("am_adam")
        result = speech.request_audio_for("This is default text for testing")
        print(result)
        print(self.request)
        # parse request
        # read json file
        # proxy request to get speech
        # return speech mp3 ?
        print("do_speech_action")

    def do_404_action(self):
        file_obj = open("./templates/page.tmpl")
        template = file_obj.read()
        file_obj.close()

        file_obj = open("./templates/404.html")
        content = file_obj.read()
        file_obj.close()

        template = template.replace("{{CONTENT}}", content).replace("{{PAGE_TITLE}}", "404 Not Found")

        self.send_response(404)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(template.encode(encoding='utf_8')))
