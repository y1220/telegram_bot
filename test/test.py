#%%
# Install ffmpeg using conda
#!conda install -c conda-forge ffmpeg -y
#!pip install git+https://github.com/openai/whisper.git
# Install ffmpeg without sudo
#!apt update && apt install -y ffmpeg
#%%
#!pip install python-dotenv
#%%
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Print the TELEGRAM_TOKEN to verify it's loaded correctly
print(os.getenv("TELEGRAM_TOKEN"))
#%%
import requests
def download_voice_messages():
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    print(TELEGRAM_TOKEN)
    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

    # Step 1: Get updates and extract file_id for voice messages
    get_updates_url = f"{base_url}/getUpdates"
    parameters = {"offset": "100"}
    resp = requests.get(get_updates_url, params=parameters)
    updates = resp.json()

    # Iterate through updates to find voice messages
    cnt = 0
    for update in updates['result']:
        if 'voice' in update['message']:
            file_id = update['message']['voice']['file_id']
            print(f"file_id: {file_id}")

            # Step 2: Get file path
            get_file_url = f"{base_url}/getFile"
            file_params = {"file_id": file_id}
            file_resp = requests.get(get_file_url, params=file_params)
            file_path = file_resp.json()['result']['file_path']

            # Step 3: Download the file
            file_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
            voice_file = requests.get(file_url)

            # Save the file
            output = 'voice_' + str(cnt) + '.ogg'
            with open(output, 'wb') as f:
                f.write(voice_file.content)

            cnt += 1
            print("Voice message downloaded successfully.")
#%%
import subprocess
import requests
import os

def process_voice_messages():
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

    # Step 1: Get updates
    get_updates_url = f"{base_url}/getUpdates"
    parameters = {"offset": "100"}
    resp = requests.get(get_updates_url, params=parameters)
    updates = resp.json()

    # Step 2: Count voice messages
    voice_count = 0
    for update in updates['result']:
        if 'voice' in update['message']:
            voice_count += 1

    print(f"Number of voice messages: {voice_count}")

    # Transcribe all voice_cnt.ogg files
    for cnt in range(voice_count):  # Replace voice_count with the actual number of voice files
        file_name = f'voice_{cnt}.ogg'
        if os.path.exists(file_name):
            transcribe_audio(file_name)
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
#%%
download_voice_messages()
process_voice_messages()