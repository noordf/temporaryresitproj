#audio is recorded and certain terms that are needed are recognized and passed to the player class
import speech_recognition as spch

class audio_recognition:

    def __init__(self):
        self.spch = spch.Recognizer()                               #initialize speech recognitoin
        self.terms_needed = ["up", "down", "left", "right"]         #the terms that should trigger a reaction
        self.recognized_list = []                                   #keep track of the needed terms that are called

    def audiorecording(self):
        with spch.Microphone() as source:
            audio = self.spch.listen(source)                        #define the audio

            try:
                text = self.spch.recognize_google(audio)            #link it to google speech recognition
                if format(text) in self.terms_needed:               #check if the spoken text equals one of the terms
                    self.recognized_list.append(format(text))       #if it is, put it in the recognized text list
                    return (self.recognized_list)                           #return the word that was heard
                else:
                    print("try again")
            except:
                    print("could you repeat that?")

