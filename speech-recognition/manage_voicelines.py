from datetime import datetime, timedelta
from text_lines import english_voice_lines, german_voice_lines
import random

#Segments the day into a few option to create fitting greetings
def determine_time_of_day():
    current_time = datetime.now()
    if 5 <= current_time.hour < 9:
        return "EarlyMorning"
    elif 9 <= current_time.hour < 12:
        return "Morning"
    elif 12 <= current_time.hour < 14:
        return "Noon"
    elif 14 <= current_time.hour < 17:
        return "Afternoon"
    elif 17 <= current_time.hour < 20:
        return "Evening"
    else:
        return "Night"
    


        

class Voiceline_Manager:
    #Loads voiceline lists depending on the language. TODO Better system for more languages. Actual localization.
    def __init__(self, language = 'english'):
        self.language = language
        if language == 'english':
            self.greetings = english_voice_lines.greeting_lists
            self.time_phrases = english_voice_lines.time_phrases
            self.voicelines = english_voice_lines.voicelines
        else:
            self.greetings = german_voice_lines.greeting_lists
            self.time_phrases = german_voice_lines.time_phrases
            self.voicelines = german_voice_lines.voicelines


    #Reloads voiceline lists on language change.
    def change_language(self, language = 'English'):
        self.language = language
        if language == 'English':
            self.greetings = english_voice_lines.greeting_lists
            self.time_phrases = english_voice_lines.time_phrases
            self.voicelines = english_voice_lines.voicelines
        else:
            self.greetings = german_voice_lines.greeting_lists
            self.time_phrases = german_voice_lines.time_phrases
            self.voicelines = german_voice_lines.voicelines


        
    #Creates a greeting fitting for the time of day.
    def time_sensitive_greeting(self):
        time_slot = determine_time_of_day()
        if time_slot == 'EarlyMorning' or time_slot == 'Morning':
            return random.choice(self.greetings['morning_greetings'])
        elif time_slot == 'Noon':
            return random.choice(self.greetings['morning_greetings'])
        elif time_slot == 'Afternoon':
            return random.choice(self.greetings['morning_greetings'])
        elif time_slot == 'Evening':
            return random.choice(self.greetings['morning_greetings'])
        else:
            return 'What are you doing here at this time, [title] [name]?'
        

    #Adds a part to the greeting to note the time since the last interation(long time no see)
    def time_passed_aknowledgement(self, time_difference = timedelta(0)):
        few_hours_interval = timedelta(hours=10)
        one_day_interval = timedelta(days=1)
        multiple_days_interval = timedelta(weeks=1)

        # Choose the appropriate set of phrases based on the time difference
        if time_difference < few_hours_interval:
            return random.choice(self.time_phrases['after_few_hours_phrases'])
        elif time_difference < one_day_interval:
            return random.choice(self.time_phrases['next_day_phrases'])
        elif time_difference < multiple_days_interval:
            return random.choice(self.time_phrases['multiple_days_phrases'])
        else:
            return random.choice(self.time_phrases['after_weeks_phrases'])
        

    #combines the greeting parts and adds name and title where appropriate
    def create_greeting(self, name = 'Visitor', title = '', last_seen = timedelta(0)):
        if name == 'Visitor':
            return self.greetings['visitor'][0]
        time_sensitive_greeting = self.time_sensitive_greeting()
        time_passed_acknowledgement = self.time_passed_aknowledgement(last_seen)
        time_sensitive_greeting = time_sensitive_greeting.replace("[name]", name)
        time_sensitive_greeting = time_sensitive_greeting.replace("[title]", title)
        return time_sensitive_greeting + time_passed_acknowledgement
    
    def create_profile_voicelines(self, line):
        return self.voicelines[line]