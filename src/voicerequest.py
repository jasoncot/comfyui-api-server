import json
from src.kokorovoices import KokoroVoiceMap
import os
from urllib import request
import hashlib
import re
import time
from pydub import AudioSegment

# this function tries to sanitize the text and then create an md5 hash
# this is to be able to cache responses
def generate_md5_path_name(prompt_text):
    lowercase_text = prompt_text.lower().strip()
    whitespace_normalized = re.sub(r'\s{2,}', ' ', lowercase_text)
    return hashlib.md5(whitespace_normalized.encode('utf-8')).hexdigest()

ORIGIN = "http://spongebob.trailoff.net:8188"

class VoiceRequest:
    def __init__(self, workflow="audio3.json"):
        self.workflow = workflow
        self.data = None

    def read_workflow(self):
        with open(f"./workflows/{self.workflow}", 'r') as file:
            self.data = json.load(file)

        if self.data is None:
            return None, "File contained no data"
        
        return self.data, None

    def select_node_from_workflow(self, workflow):
        class_type = workflow["1"]["class_type"]
        req =  request.Request(f"{ORIGIN}/api/object_info/{class_type}", method="GET")

        response_body = None
        with request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')

        resp_obj = json.loads(response_body)
        voice_obj = resp_obj[class_type]["input"]["required"]["voice"]

        short_voices = []
        for voice in voice_obj[0]:
            short_voices.append(voice.split(" ")[-1])

        return short_voices

    def execute(self):
        workflow, err_msg = self.read_workflow()

        if err_msg is not None:
            return None, err_msg
        
        return self.select_node_from_workflow(workflow), None