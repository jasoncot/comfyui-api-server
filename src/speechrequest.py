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
        with open('./workflows/audio3.json', 'r') as file:
            data = json.load(file)

        if data is None:
            return None
        
        # my_md5 = generate_md5_path_name(f"{self.selected_voice}:{text_prompt}")
        # data["3"]["inputs"]["filename_prefix"] = f"audio/{my_md5}/api-request-"

        data["1"]["inputs"]["voice"] = self.selected_voice
        data["1"]["inputs"]["text"] = text_prompt

        return data
    
    def check_queue_for_task(self, task_id):
        req = request.Request(f"{ORIGIN}/api/queue", method='GET')
        response_body = None
        with request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')

        request_detail = json.loads(response_body)
        for queue_task in request_detail["queue_pending"]:
            if queue_task[1] == task_id:
                return True, "pending"
        
        for queue_task in request_detail["queue_running"]:
            if queue_task[1] == task_id:
                return True, "running"
            
        return False, None
    
    def get_task_history(self, task_id):
        url = f"{ORIGIN}/api/history/{task_id}"
        req = request.Request(url, method='GET')
        response_body = None

        with request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')

        return json.loads(response_body)[task_id]

    def get_task_history_status(self, task_history):
        return task_history["status"]["completed"], task_history["status"]["status_str"]

    def get_task_history_outputs(self, task_history):
        outputs = []

        for output_key in task_history["outputs"]:
            output = task_history["outputs"][output_key]
            if "audio" in output.keys():
                for item in output["audio"]:
                    filename = item["filename"]
                    subfolder = item["subfolder"]
                    type = item["type"]
                    headers = {
                        "Accept": "audio/webm,audio/ogg,audio/wav,audio/*,application/ogg,video/*"
                    }
                    url = f"{ORIGIN}/api/view?filename={filename}&subfolder={subfolder}&type={type}"

                    req = request.Request(url, headers=headers, method='GET')

                    prompt_id = task_history["prompt"][1]

                    with request.urlopen(req) as response:
                        flac_filename = f"/tmp/raw-audio/{prompt_id}.flac"
                        os.makedirs(os.path.dirname(flac_filename), exist_ok=True)
                        with open(flac_filename, "wb") as f:
                            f.write(response.read())

                        sound = AudioSegment.from_file(flac_filename, "flac")
                        mp3_filename = f"/tmp/mp3/{prompt_id}.mp3"
                        os.makedirs(os.path.dirname(mp3_filename), exist_ok=True)
                        fh = sound.export(mp3_filename, format="mp3", bitrate="128k")
                        outputs.append(fh.read())

        return outputs

    def request_audio_for(self, text_prompt=""):
        payload = self.generate_payload(text_prompt)
        p = {"prompt": payload}
        data = json.dumps(p).encode('utf-8')
        req =  request.Request(f"{ORIGIN}/api/prompt", data=data, method="POST")

        response_body = None
        with request.urlopen(req) as response:
            response_body = response.read().decode('utf-8')

        # pull the response into json to get the prompt_id
        request_detail = json.loads(response_body)
        if "prompt_id" not in request_detail.keys():
            return None, "Response did not have a prompt_id"
        
        prompt_id = request_detail["prompt_id"]

        while True:
            is_found, found_code = self.check_queue_for_task(prompt_id)
            if is_found == False:
                break

            if found_code == "running":
                # if the task is currently running, wait a second
                time.sleep(1)
            elif found_code == "pending":
                # if the task is pending, wait a bit longer, like 5 seconds
                time.sleep(5)
        
        # at this point we should have found that the task has completed
        task_history = self.get_task_history(prompt_id)

        outputs = self.get_task_history_outputs(task_history)

        return outputs[0], None
