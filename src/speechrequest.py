import json
from src.kokorovoices import KokoroVoiceMap
import os
from urllib import request

class SpeechRequest:
    def __init__(self, voice="af"):
        self.select_voice(voice)

    # change the default voice
    def select_voice(self, name):
        if name in KokoroVoiceMap:
            self.selected_voice = KokoroVoiceMap[name]
        else:
            self.selected_voice = None
    
    def generate_payload(self, text_prompt=""):
        data = None
        with open('./workflows/audio.json', 'r') as file:
            data = json.load(file)

        if data is None:
            return None
        
        data["2"]["inputs"]["voice"] = self.selected_voice
        data["2"]["inputs"]["text"] = text_prompt

        return data
    
    def request_audio_for(self, text_prompt=""):
        payload = self.generate_payload(text_prompt)
        p = {"prompt": payload}
        data = json.dumps(p).encode('utf-8')
        req =  request.Request("http://spongebob.trailoff.net:8188/prompt", data=data)
        request.urlopen(req)
