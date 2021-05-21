import playsound
import multiprocessing

def play():
    while True:
        playsound.playsound('audio/Bubbles_and_Submarines.mp3')

class AudioGameTheme:

    def __init__(self):
        self.process = multiprocessing.Process(target=play)
        self.process.start()

    def stop(self):
        self.process.terminate()
