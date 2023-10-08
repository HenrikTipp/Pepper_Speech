import os
import whisper
import torch
import subprocess
import time
import os
import signal


from subprocess import Popen, PIPE



phrase_timeout = 1 #Time in seconds how long a pause you can make when talking until the model will determine you are finished.


class Speech_Recognition:
    #Initiaalizes a whisper speech recognition model for english audio. filename points to the location of the audio data, should be speech.wav.
    def __init__(self, filename):
        self.filename = filename
        model = "base.en"
        self.audio_model = whisper.load_model(model)

    #Changes language. Whisper only offers english or all, with english offering better accuracy.
    def change_language(self, language):
        if language == 'english':
            model = "base.en"
            self.audio_model = whisper.load_model(model)
        else:
            model = "base"
            self.audio_model = whisper.load_model(model)

    
    def transcribe_audio(self, timeout):
        """transcribes audio to text.
        Args:
            timeout : The amount of time before returning regardless of identities. Maximum wait time. For responsiveness in half seconds. This was tested on a slow computer where whisper took some time to transcribe.
        Returns:
            The text transcribed from audio.
        """
        #Starts python2 script to record audio
        naoqi_audio_capture = Popen(['python2', 'speech_recording.py'], stdin=PIPE)
        print("capturing Audio")
        prev_text = ''
        text = ''
        timer = 0
        ident_counter = 0
        while timer <= timeout:
            print(timer)
            time.sleep(0.5)
            #Audio from speech.wav is transcribed by the whisper model.
            result = self.audio_model.transcribe(self.filename, fp16=torch.cuda.is_available()) 
            #Text is extracted and whitespaces are removed.
            text = result['text'].strip()
            print(text)
            #Text is compared with previous text, If it is identical multiple times in a row the user is done talking and the transcription is returned before timeout.
            #TODO format text to remove punctuation, identity should only be for text to speed up responses.
            if text == prev_text:
                ident_counter = ident_counter + 1
                print ("repetition: " + str(ident_counter) + " out of " + str(phrase_timeout))
                if ident_counter >= phrase_timeout:
                    break
            else:
                ident_counter = 0
            prev_text = text
            timer = timer + 1
        print("no longer capturing Audio")
        #Subprocess is terminated to reset audio capture and prevent multiple write accesses to speech.wav.
        naoqi_audio_capture.send_signal(signal.SIGTERM)
        naoqi_audio_capture.wait()
        print("subprocess terminated")
        return text


def main():
    #main for testing purposes. Not used in program flow.
    capture = Speech_Recognition(filename = "speech.wav")
    text = capture.transcribe_audio(10)
    print("I heard: " + text)
    #naoqi_tts = Popen(['python2', 'text_to_speech.py'], stdin=PIPE)
    #naoqi_tts.stdin.write(("test successfull" + '\n').encode("utf-8"))


if __name__ == '__main__':
    main()
