#some functionality to detect keywords during conversation to trigger certain functionality.


change_profile_keywords = [["change", "customize", "adjust", "änder", "pass", "stell"], ["preferenc", "profile", "greet", "language", "einstellung", "präferenz", "gruß", "sprache"]]

give_directions_keywords = [["where is", "find", "room", "wo ist", "wie finde", "raum"]]

end_conv = [["exit", "quit", "bye", "goodbye"]]

def find_keywords(text, keyword_lists):
    for keywords in keyword_lists:
        if not any(keyword.lower() in text.lower() for keyword in keywords):
            return False
    return True

def analyze_response(response):
    if find_keywords(response, give_directions_keywords):
        return 'give_directions'
    elif find_keywords(response, change_profile_keywords):
        return 'customize_profile'
    elif find_keywords(response, end_conv):
        return 'exit'
    else:
        return 'no_matches'
