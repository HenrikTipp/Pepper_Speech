import qi
import datetime
import paramiko
from scp import SCPClient
import os
from time import sleep
import wave

import signal
#This is a script to be executed in a subprocess in python 2.7. Its purpose is to interface with the 2.7 naoqi library to send text to the robots tts module.

#IP and port for the pepper robot.
ip_address = "10.0.0.117"
port = 9559

#This opens a connection to the pepper robot without using a predefined proxy but still using the python package for pepper.
session = qi.Session()
session.connect("tcp://{0}:{1}".format(ip_address, port))

#This opens an ssh connection to the pepper robot to download audio files from the robot.
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()
ssh.connect(hostname=ip_address, username="nao", password="nao")


scp = SCPClient(ssh.get_transport())

#Using the connection to pepper with the qi.Session 2 services are started.
#"ALSpeechRecognition" Is used to disable expressions. This may also be used to detect when a user starts talking TODO 
speech_service = session.service("ALSpeechRecognition")
#Disabling expressions should reduce noise but may not work because of different settings on the robot.
speech_service.setAudioExpression(False)
speech_service.setVisualExpression(False)
#"ALAudioRecorder" is used to record the speech.
audio_recorder = session.service("ALAudioRecorder")

start_time = datetime.datetime.now()

#The microphone is reset in case it was already running
audio_recorder.stopMicrophonesRecording()

#A new recording is started. 48000 is the frequency using all microphones, for details see http://doc.aldebaran.com/2-5/naoqi/audio/alaudiodevice.html#alaudiodevice
audio_recorder.startMicrophonesRecording("/home/nao/speech.wav", "wav", 48000, (0, 0, 1, 0))

audio = []
first = True

#Stops the microphone on program exit.
def signal_handler(signum, frame):
    audio_recorder.stopMicrophonesRecording()
    exit(0)

signal.signal(signal.SIGTERM, signal_handler)

while True:
    #Records .5 second speech segments. too small segments lose some audio because the microphone is reset for each segment, too large segments make speech recognition unresponsive.
    sleep(0.5)
    audio_recorder.stopMicrophonesRecording()
    if first:
        #for the first segment speech.wav, the collection of file for all audio segments is initialized with the first segment, downloaded from the robot.
        scp.get("speech.wav", local_path = os.getcwd())
        #The microphone is enabled for the next segment. File location is changed to speech_segment.
        audio_recorder.startMicrophonesRecording("/home/nao/speech_segment.wav", "wav", 48000, (0, 0, 1, 0))
        #In addition to the audiofile the audio is also saven in the audio variable where the segments are appended.
        w = wave.open("speech.wav", 'rb')
        audio.append(  [w.getparams(),  w.readframes(w.getnframes())])
        w.close()
        #The next segment should not reset speech.wav so first is set to false. For new speech instances this entire script will be rerun so audio.wav will be overwritten whenever the user starts speaking again after a system response.
        first = False
    else:
        #The next speech_segment is downloaded.
        scp.get("speech_segment.wav", local_path = os.getcwd())
        #The microphone is enabled for the next segment.
        audio_recorder.startMicrophonesRecording("/home/nao/speech_segment.wav", "wav", 48000, (0, 0, 1, 0))
        #The segment is appended to the full recording.
        w = wave.open("speech_segment.wav", 'rb')
        audio.append(  [w.getparams(),  w.readframes(w.getnframes())])
        w.close()

        #The combined segments are saved in one file.
        output = wave.open("speech.wav", 'wb')
        output.setparams(audio[0][0])

        for j in range(len(audio)):
            output.writeframes(audio[j][1])
        output.close()
