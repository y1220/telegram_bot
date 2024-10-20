from VoiceMessageFactory import VoiceMessageFactory

if __name__ == '__main__':
    voice_message_workflow = VoiceMessageFactory.create_voice_message_workflow()
    voice_message_workflow.download_voice_messages()
