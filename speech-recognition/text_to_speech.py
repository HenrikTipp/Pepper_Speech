from naoqi import ALProxy
from time import sleep
#This is a script to be executed in a subprocess in python 2.7. Its purpose is to interface with the 2.7 naoqi library to send text to the robots tts module.

#IP and port for the pepper robot.
IP = '10.0.0.117'
nao_port = 9559

#Initializes a connection to the robot through the python package for pepper, accessing the robots text to speech module.
tts = ALProxy("ALTextToSpeech", IP, nao_port)



while True:
    #Input is taken from stdin from the python3 process calling this script.
    try:
        text = raw_input()
    except EOFError:
        print "No input"
        sleep(0.5)

        continue
    #The language of the tts module is set if the corresponding prompt is received in stdin. This should not occur in a normal conversation but works through the same channel as speech prompts.
    if text == 'English':
        tts.setLanguage("English")
        continue
    if text == 'German':
        tts.setLanguage("German")
        continue
    #If no predefined prompt is detected the text from stdin is sent to the robot.
    tts.say(text)
    break
