from speech_recognition import Speech_Recognition
from employee_registry import Employee_Register
from subprocess import Popen, PIPE
from manage_voicelines import Voiceline_Manager
from transformers import pipeline
from language_model import Language_Model
import re
from datetime import datetime
from response_analysis import analyze_response
import queue
from listener import InputListener

#Pattern used for regex to extract
pattern = r'\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|null|eins|zwei|drei|vier|fünf|sechs|sieben|acht|neun|zehn|elf|zwölf|dreizehn)\b'

#to translate numbers in the speech recognition to numbers. Larger numbers are already transcribed numerically.
word_to_digit = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, 'eleven': 11, "twelve": 12, "thirteen": 13, 
    "null": 0, "eins": 1, "zwei": 2, "drei": 3, "vier": 4,
    "fünf": 5, "sechs": 6, "sieben": 7, "acht": 8, "neun": 9,
    "zehn": 10, "elf": 11, "zwölf": 12, "dreizehn": 13
}


#The main class of this project, organizing the program flow.
class Pepper_Speech():
    def __init__(self):
        #Time after which the speech recognition assumes no answer will be given. 
        self.wait_time_seconds = 10

        #Load whisper for realtime audio transcription
        self.speech_transcriber = Speech_Recognition(filename = "speech.wav")

        #Initializes the conversational model for smalltalk
        self.conversational_model = Language_Model()

        #loads a basic sentiment analysis model used to chack whether users agree or disagree without just looking for yes or no answers. TODO add keyword search or better models to improve non english performance.
        self.sentiment_analysis = pipeline("sentiment-analysis")

        #load the database of employees that are already known
        self.employee_registry = Employee_Register()

        #Language is english by default because there is only a single language or all language setting for whisper speech recognition.
        self.language = "English"

    def naoqi_tts(self, text):
        """
        Opens a proxy to pepper in a python2 subprocess, sends a message and then terminates the subprocess.
        Args:
            text: the text to be said by pepper.
        """
        bridge = Popen(['python2', 'text_to_speech.py'], stdin=PIPE)
        print("speaking: ", text)
        #If a different language is chosen then the tts module can be set to that language.
        if not self.language == "English":
            bridge.stdin.write((self.language + '\n').encode("utf-8"))
            #Sends the message and then terminates the subprocess, waiting for it to finish.
        bridge.communicate((text + '\n').encode("utf-8"))
        print("done")



    def start_conversation(self, id):
        """
        Initializes everything required for a conversation.
        Args:
            id: The ID corresponding to the conversation partner. Should be determined by face recognition, should be consistent with ID´s saved in employee_register.csv. New guests can get any ID not currently in use.
        """
        self.conversation_id = id
        #Determines whether the ID corresponds to a known employee
        conversation_partner_known = self.employee_registry.known_employee(self.conversation_id)
        if conversation_partner_known:
            #For known employees information is pulled from the registry to personalize the greeting
            name = self.employee_registry.get_name(self.conversation_id)
            title = self.employee_registry.get_title(self.conversation_id)
            language = self.employee_registry.get_language(self.conversation_id)
            #Predefined lines are available in english and german.
            self.voiceline_manager = Voiceline_Manager(language)
            #The whisper model is set to either english or all languages.
            self.speech_transcriber.change_language(language)
            #A greeting is made for the employee if the last interaction is sufficiently long ago.
            self.employee_greeting(name, title)
        else:
            #Guests are greeted generically
            self.voiceline_manager = Voiceline_Manager()
            self.guest_greeting()
            


    def guest_greeting(self):
        #Guests are greeted and asked to save preferences
        self.naoqi_tts(self.voiceline_manager.create_greeting())
        self.naoqi_tts("I do not know you yet, would you like me to remember you? This includes saving images for facial recognition.")

        #Sentiment analysis is used to check agreement or disagreement
        choice = self.speech_transcriber.transcribe_audio(self.wait_time_seconds)
        #Checks whether the response sounds positive or negative to a basic sentiment analysis. Works well in englis but poorly in german.
        choice = self.sentiment_analysis(choice)[0]['label']
        if choice == 'POSITIVE':
            self.create_profile()
        else:
            #Since no profile has been created this can only be english and doesnt need to be adjusted for language
            self.naoqi_tts('If you wish to create a profile later please ask me to do so at any time.')
        self.smalltalk()



    def employee_greeting(self, name, title):
        #timepassed and timepreference are timedeltas describing how often the person wishes to be greeted and how long it has been
        time_passed, time_preference = self.employee_registry.user_time(self.conversation_id)

        if time_passed > time_preference:
            #A greeting is created based o the employees preferences(like name and title), time and time since last meeting.
            self.naoqi_tts(self.voiceline_manager.create_greeting(name, title, time_passed) )

            #Checks whether this employee has already customized their preferences(or refused to)
            preferences_already_customized = self.employee_registry.user_ask_preferences(self.conversation_id)
            if not preferences_already_customized:
                self.naoqi_tts('Your Profile has not yet been customized, would you like to change that?')
                choice = self.speech_transcriber.transcribe_audio(self.wait_time_seconds)

                #Checks whether the response sounds positive or negative to a basic sentiment analysis. Works well in englis but poorly in german.
                choice = self.sentiment_analysis(choice)[0]['label']
                if choice == 'POSITIVE':
                    self.create_profile()
                else:
                    self.naoqi_tts('If you wish to create a profile later please ask me to do so at any time.')
        #After greeting and custoomization beginns smalltalk.
        self.smalltalk()


        
        


    def create_profile(self):
        language = 'english'
        #The audiotranscriber is currently set to english only by default because it is more accurate. Therefore if a user answers with 'Deutsch' this may cause issues.
        self.naoqi_tts('Would you like me to speek english or german? Please say german for german.')
        language = self.speech_transcriber.transcribe_audio(self.wait_time_seconds)
        #Only English and German lines so it checks for german and otherwise chooses english as default.
        if re.search('german', language, re.IGNORECASE):
            self.language= "German"
            self.naoqi_tts('Ich bin momentan eingeschränkt auf deutsch, meine spracherkennung ist schlechter und ich kann keine guten freiform gespräche führen. Möchten sie dennoch lieber deutsch reden?')
            self.speech_transcriber.change_language('german')
            choice = self.speech_transcriber.transcribe_audio(self.wait_time_seconds)
            choice = self.sentiment_analysis(choice)[0]['label']
            if choice == 'NEGATIVE':
                self.language = "English"
                self.naoqi_tts('Thank you, continuing in english.')
        else:
            self.language = 'English'

        self.voiceline_manager.change_language(self.language)

        #Pepper asks for a name using voicelines from the voiceline manager(englsh/german)
        name = '_'
        self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('ask_name'))
        name = self.speech_transcriber.transcribe_audio(self.wait_time_seconds)

        #Pepper asks to confirm that it understood the name correctly. This should show users that everything they say after a prompt is taken as a response.
        #This is also necessary sincce name recognition is unreliable in speech transcription.
        self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('name_confirm') + name )
        choice = self.speech_transcriber.transcribe_audio(self.wait_time_seconds)
        choice_sentiment = self.sentiment_analysis(choice)[0]['label']
        if choice_sentiment == 'NEGATIVE':
            #If the name was not understood correctly it is replaced with a placeholder. If the user wants to correct it they would have to redo the customization. TODO better loop to correct name.
            self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('misunderstood'))
            name = '_'


        title = '_'
        #Pepper first asks whether a title is desired. Titles are easier than names so they offer an option for people whose names were misunderstood to still be correctly addressed.
        self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('use_title'))
        choice = self.speech_transcriber.transcribe_audio(self.wait_time_seconds)
        choice_sentiment = self.sentiment_analysis(choice)[0]['label']
        if choice_sentiment == 'Positive':
            #If the user wants to be clled by title it is recorded and saved.
            self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('ask_title'))
            title = self.speech_transcriber.transcribe_audio(self.wait_time_seconds)

        #The user is asked how often they want to be greeted(in hours). This is to prevent pepper from annoying frequent visitors.
        self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('time_preference'))
        preference = self.speech_transcriber.transcribe_audio(self.wait_time_seconds)
        #In order to extract any numbers that were transcribed both numerical and text numbers are extracted, the latter using a regex for everything from 0 to thirteen. Larger numbers should get transcribed numerically
        hours_num = [int(s) for s in re.findall(r'\b\d+\b', preference)]
        hours = re.findall(pattern, preference, flags=re.IGNORECASE)
        hours = [word_to_digit[word.lower()] for word in hours]
        hours = hours_num +  hours
        #if one or more numbers were extracted from the text, the first is picked. If none were wound four hours are used as the default, allowing 2 greetings in a working day.
        if len(hours) > 0:
            hours = hours[0]
        else:
            hours = 4

        #The time of this interaction is saved to start counting for the next greeting.
        last_interaction = datetime.utcnow()

        #The user is asked to confirm that all choices are saved correctly.
        self.naoqi_tts(title+ " " + name + ". " + str(hours) + self.voiceline_manager.create_profile_voicelines('final_confirm') )
        choice = self.speech_transcriber.transcribe_audio(self.wait_time_seconds)
        choice_sentiment = self.sentiment_analysis(choice)[0]['label']
        if choice_sentiment == 'NEGATIVE' or not any(c.isalnum() for c in choice):
            #If the choices were not saved correctly customization is aborted.
            self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('discarding_preferences'))
            return

        #checks whether current conversation partner is an empoyee or guest to save the new preferencess with this information. 
        employee = self.employee_registry.known_employee(self.conversation_id)

        new_employee = {'id':self.conversation_id, 'name':name, 'title': title, 'customized_bool':True, 'time_preference': hours, 'last_interaction': last_interaction, 'language': language, 'employee': employee}
        self.employee_registry.add_employee(new_employee)
        #If this programm is executed from within the facial recognition program this print could be detected and prompt the camera to save an image for a guest.
        print('[save_face]')

    

    def smalltalk(self):
        #A thread is set up to listen to stdin in case the superprocess has commands. Specifically this checks for the [door] command which can be used to indicate that the robot should ask help with the door
        commands = queue.Queue()
        input_listener = InputListener(commands)
        input_listener.daemon = True
        input_listener.start()

        #The counter will end a conversation if the transcription times out without text multiple times.
        counter = 0
        while True:
            #checking for commands to ask for help with the door
            if commands.qsize() > 0:
                command = commands.get()
                if command == '[door]':
                    self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('door') )


            #transcribing voice inputs
            prompt = self.speech_transcriber.transcribe_audio(self.wait_time_seconds)

            #If nothing is said after two timeouts the robot offers assistance
            if not any(c.isalnum() for c in prompt):
                counter = counter + 1
                #If nothing is asked after three the programm ends the conversation
                if counter == 2:
                    self.employee_registry.store_register()
                    return
                self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('help') )
                continue

            #the audio transcription is analyzed for keywords that could indicate that a user wants to use a specific function. currently asking for directions or changing their greeting/profile.
            analysis = analyze_response(prompt)
            if analysis == 'give_directions':
                self.give_directions(prompt)
                continue
            elif analysis == 'customize_profile':
                self.create_profile()
                continue
            elif analysis == 'exit':
                self.naoqi_tts('goodbye')
                self.employee_registry.store_register()
                return


            response = self.conversational_model.generate_response(prompt)
            self.naoqi_tts(response)



    def give_directions(self, prompt):
        #If the response analysis determines that a user is asking for directions to a room the room numberis extracted from the prompt.
        room_num = [int(s) for s in re.findall(r'\b\d+\b', prompt)]
        room = re.findall(pattern, prompt, flags=re.IGNORECASE)
        room = [word_to_digit[word.lower()] for word in room]
        room = room_num +  room
        if len(room) > 0:
            room = room[0]
        else:
            #If no room number can be extracted the user is asked to provide one.
            self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('ask_room'))
            return
        #If a number could be exracted a response is given depending on the quarter of the floor the room is at assuming the robot is at the elevators. TODO assign responses to correct room numberss.
        if 0 <= room < 10:
            self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('direction_1'))
        elif 10 <= room < 20:
            self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('direction_2'))
        elif 20 <= room < 30:
            self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('direction_3'))
        elif 30 <= room < 40:
            self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('direction_4') )
        else:
            self.naoqi_tts(self.voiceline_manager.create_profile_voicelines('wrong_floor') )

            







def main():
    pepper_speech = Pepper_Speech()
    #Note: this can be done from the facial recognition system calling the speech module in a subprocess by writing to stdin. I am working with id's which could correspond to index in facial recognition.
    id = int(input("Please enter the Id for the person starting the conversation"))
    #TODO To actually use this in the way it is intended this should be a loop which can start new conversations if a new ID is given but the exact implementation depends on the environment(how does facial recognition sttart conversations)
    pepper_speech.start_conversation(id)



if __name__ == '__main__':
    main()