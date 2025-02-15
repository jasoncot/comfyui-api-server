from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from src.speechrequest import SpeechRequest
from urllib import error

class MyServer(BaseHTTPRequestHandler):
    def do_POST(self):
        self.switch_route()

    def do_GET(self):
        self.switch_route()

    def switch_route(self):
        path = self.path
        if path == "/v1/audio/speech":
            self.do_speech_action()
        else:
            # it's a 404
            self.do_404_action()

    def get_audio_for_prompt(self, voice="am_adam", prompt_text="Your request was not properly formed.  Check the API and try again."):
        speech = SpeechRequest(voice)
        result = None
        result, err = speech.request_audio_for(prompt_text)

        if err is not None:
            self.send_response(500)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            mesg = "HTTP 500 server error\n" + f"err {err=}"
            self.wfile.write(bytes(mesg.encode(encoding='utf_8')))
            return

        if result is None:
            self.send_response(400)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes("invalid content type").encode(encoding="utf_8"))
            return

        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.end_headers()
        self.wfile.write(bytes(result))
        return

    def do_speech_action(self):
        if self.command == "GET":
            speech = SpeechRequest("am_adam")

            try:
                return self.get_audio_for_prompt(
                    "am_adam",
                    "This is default text for testing, which is actually now a longer text so that I can try to catch the payload in the queue for testing"
                )
            
            except error.HTTPError as err:
                self.send_response(500)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                mesg = "HTTP 500 server error\n" + f"err {err=}"
                self.wfile.write(bytes(mesg.encode(encoding='utf_8')))
                return

        if self.command == "POST":
            content_type = self.headers.get_content_type()

            if content_type != "application/json":
                self.send_response(400)
                self.send_header("Content-Type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes("invalid content type".encode(encoding='utf_8')))
                return
        
        content_len = int(self.headers.get('Content-Length'))
        post_body = self.rfile.read(content_len)
        my_dict = json.loads(post_body)

        return self.get_audio_for_prompt(my_dict["voice"], my_dict["input"])

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
