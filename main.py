# Alexa Personal Assitant for Raspberry Pi
# Coded by Simon Beal and Matthew Timmons-Brown for "The Raspberry Pi Guy" YouTube channel
# Built upon the work of Sam Machin, (c)2016
# Feel free to look through the code, try to understand it & modify as you wish!
# The installer MUST be run before this code.

#!/usr/bin/python
import sys
import time
import os
import alsaaudio
import wave
import numpy
import copy
from evdev import InputDevice, list_devices, ecodes
import RPi.GPIO as GPIO

import alexa_helper # Import the web functions of Alexa, held in a separate program in this directory

print "Welcome to Alexa. I will help you in anyway I can.\n  Press Ctrl-C to quit"

# Initialise audio buffer
audio = ""
inp = None

#Settings
button = 25 #GPIO Pin with button connected


# We're British and we spell "colour" correctly :) Colour code for RAINBOWZ!!
colours = [[255, 0, 0], [255, 0, 0], [255, 105, 0], [255, 223, 0], [170, 255, 0], [52, 255, 0], [0, 255, 66], [0, 255, 183]]

# Loudness for highest bar of RGB display
max_loud = 1024

# When button is released, audio recording finishes and sent to Amazon's Alexa service
def release_button():
    print "released!"
    global audio, inp
    #sense.set_pixels([[0,0,0]]*64)
    w = wave.open(path+'recording.wav', 'w') # This and following lines saves voice to .wav file
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(16000)
    w.writeframes(audio)
    w.close()
    #sense.show_letter("?") # Convert to question mark on display
    alexa_helper.alexa() # Call upon alexa_helper program (in this directory)
    #sense.clear() # Clear display
    inp = None
    audio = ""

# When button is pressed, start recording
def press_button():
    print "pressed!"
    global audio, inp
    try:
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, alexa_helper.device)
    except alsaaudio.ALSAAudioError:
        print('Audio device not found - is your microphone connected? Please rerun program')
        sys.exit()
    inp.setchannels(1)
    inp.setrate(16000)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(1024)
    audio = ""
    l, data = inp.read()
    if l:
        audio += data

# Whilst button is being pressed, continue recording and set "loudness"
def continue_pressed():
    print("still pressed!")
    global audio, inp
    l, data = inp.read()
    if l:
        audio += data
        a = numpy.fromstring(data, dtype='int16') # Converts audio data to a list of integers
        highest_loud = 0
        loudness = int(numpy.abs(a).mean()) # Loudness is mean of amplitude of sound wave - average "loudness"
        #set_display(loudness) # Set the display to show this "loudness"

# Event handler for button
def handle_enter(pressed):
    handlers = [release_button, press_button, continue_pressed] # 0=released, 1=pressed, 2=held
    handlers[pressed]()

def event_loop_button():
    GPIO.add_event_detect(button, GPIO.BOTH, callback=testcallback)
    try:
        while True:
            pass
    finally:
        GPIO.cleanup()
        
def testcallback(button):
    if GPIO.input(button):
        print("Down!")
        handle_enter(1)
        while GPIO.input(button):
            handle_enter(2)
    else:
        print("Up!")
        handle_enter(0)
    
if __name__ == "__main__": # Run when program is called (won't run if you decide to import this program)

    GPIO.setwarnings(False)
    GPIO.cleanup()
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(button, GPIO.IN)
	
    while alexa_helper.internet_on() == False:
        print "."
    token = alexa_helper.gettoken()
    path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))
    os.system('mpg123 -q {}hello.mp3'.format(path, path)) # Say hello!
    event_loop_button()
    print "\nYou have exited Alexa. I hope that I was useful. To talk to me again just type: python main.py"
