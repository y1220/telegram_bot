from dotenv import load_dotenv
import os

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
#print(os.getenv("TELEGRAM_TOKEN"))

#%%
import requests

def download_and_save_voice_file(update, cnt):
    file_id = update['message']['voice']['file_id']
    message_id = update['message']['message_id']
    username = update['message']['from']['username']
    print(f"file_id: {file_id}, update_id: {message_id}, username: {username}")

    # Step 2: Get file path
    get_file_url = f"{base_url}/getFile"
    file_params = {"file_id": file_id}
    file_resp = requests.get(get_file_url, params=file_params)
    file_path = file_resp.json()['result']['file_path']

    # Step 3: Download the file
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
    voice_file = requests.get(file_url)

    # Save the file
    output = 'voice_' + str(cnt) + '_' + str(message_id) + '_' + username + '.ogg'
    with open(output, 'wb') as f:
        f.write(voice_file.content)

    print("Voice message downloaded successfully.")
    return output
def download_voice_messages():
    # Step 1: Get updates and extract file_id for voice messages
    get_updates_url = f"{base_url}/getUpdates"
    parameters = {"offset": "100"}
    resp = requests.get(get_updates_url, params=parameters)
    updates = resp.json()

    # Iterate through updates to find voice messages
    cnt = 0
    for update in updates['result']:
        if 'voice' in update['message']:
            file_name = download_and_save_voice_file(update, cnt)
            cnt += 1
            process_voice_file(file_name)

#%%
import subprocess
import requests
import os


def process_voice_file(file_name):
    if os.path.exists(file_name):
        parts = file_name.split('_')
        last_part = parts[-1]
        message_id = parts[-2]
        username = last_part.split('.')[0]
        content = transcribe_audio(file_name)
        send_message_to_telegram(content, username, message_id)
    else:
        print(f"File {file_name} does not exist.")


def transcribe_audio(ogg_file):
    # Generate the .txt file using whisper
    txt_file = ogg_file.replace('.ogg', '.txt')
    subprocess.run(['whisper', ogg_file, '--model', 'tiny', '--language', 'en'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Read and print the content of the generated .txt file
    with open(txt_file, 'r') as file:
        content = file.read()
        print(content)
    return content

def send_message_to_telegram(message, username, message_id):
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    send_message_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": username + ': ' + message, "reply_to_message_id": message_id}
    requests.get(send_message_url, params=params)
#%%
download_voice_messages()
