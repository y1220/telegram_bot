import os
import requests
import subprocess
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

class VoiceMessageWorkflow:
    def download_and_save_voice_file(self, update, cnt):
        file_id = update['message']['voice']['file_id']
        message_id = update['message']['message_id']
        username = update['message']['from']['username']
        print(f"file_id: {file_id}, update_id: {message_id}, username: {username}")

        file_path = self.get_file_path(file_id)
        voice_file = self.download_file(file_path)
        output = self.save_file(cnt, message_id, username, voice_file)
        return output

    def get_file_path(self, file_id):
        get_file_url = f"{BASE_URL}/getFile"
        file_params = {"file_id": file_id}
        file_resp = requests.get(get_file_url, params=file_params)
        return file_resp.json()['result']['file_path']

    def download_file(self, file_path):
        file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        return requests.get(file_url)

    def save_file(self, cnt, message_id, username, voice_file):
        output = f'voice_{cnt}_{message_id}_{username}.ogg'
        with open(output, 'wb') as f:
            f.write(voice_file.content)
        print("Voice message downloaded successfully.")
        return output

    def process_voice_file(self, file_name):
        if os.path.exists(file_name):
            parts = file_name.split('_')
            message_id = parts[-2]
            username = parts[-1].split('.')[0]
            content = self.transcribe_audio(file_name)
            self.send_message_to_telegram(content, username, message_id)
        else:
            print(f"File {file_name} does not exist.")

    def transcribe_audio(self, ogg_file):
        txt_file = ogg_file.replace('.ogg', '.txt')
        subprocess.run(['whisper', ogg_file, '--model', 'tiny', '--language', 'en'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        with open(txt_file, 'r') as file:
            content = file.read()
        return content

    def send_message_to_telegram(self, message, username, message_id):
        send_message_url = f"{BASE_URL}/sendMessage"
        params = {"chat_id": CHAT_ID, "text": f"{username}: {message}", "reply_to_message_id": message_id}
        requests.get(send_message_url, params=params)

    def handle_updates(self, updates):
        cnt = 0
        for update in updates['result']:
            if 'voice' in update['message']:
                file_name = self.download_and_save_voice_file(update, cnt)
                cnt += 1
                self.process_voice_file(file_name)

    def download_voice_messages(self):
        get_updates_url = f"{BASE_URL}/getUpdates"
        parameters = {"offset": "100"}
        resp = requests.get(get_updates_url, params=parameters)
        updates = resp.json()
        self.handle_updates(updates)
