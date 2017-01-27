from os import listdir
from os.path import isfile, join
import pygame
import random
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(10, GPIO.OUT)

mp3_dir = 'mp3'
first_choice = 'mp3/j'
second_choice = 'mp3/e'

list_txt = 'soundlist.txt'
pygame.init()
pygame.mixer.init()
bath_songs = ["sound_900.mp3", "sound_901.mp3", "sound_902.mp3", "sound_903.mp3"]


"""
Sound player for music
"""
def play_bath_sound():
    # Plays random music from bath_soungs in mp3 folder
    files = [join(mp3_dir, f) for f in listdir(mp3_dir) if isfile(join(mp3_dir, f)) and f.endswith('mp3') and f in bath_songs]
    file = random.choice(files)
    pygame.mixer.music.load(file)
    
    GPIO.output(10, 1)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.5)
    GPIO.output(10, 0)

def play_id_sound(id):
    global first_choice
    global second_choice
# Plays a specific music given ID sound_<ID>.mp3 from mp3/E or mp3/J folder search for preferred language folder first
    file = 'sound_{}.mp3'.format(id)
    if not isfile(join(first_choice, file)):
        if not isfile(join(second_choice, file)):
            if not isfile(join(mp3_dir, file)):
                return "Could not find file {}".format(file)
            else:
                target_folder = mp3_dir
        else:
            target_folder = second_choice
    else:
        target_folder = first_choice
    pygame.mixer.music.load(join(target_folder,file))
    GPIO.output(10, 1)
    pygame.mixer.music.play()
    while(pygame.mixer.music.get_busy()):
        time.sleep(0.5)
    GPIO.output(10, 0)
    return "Play {}".format(file)

def sound_language_preference(Language):
    global first_choice
    global second_choice
# Set language preference "E" or "J"
    if Language == "E" or Language == "e":
        first_choice = 'mp3/e'
        second_choice = 'mp3/j'
        return "English is selected"
    elif Language == "J" or Language == "j":
        first_choice = 'mp3/j'
        second_choice = 'mp3/e'
        return "Japanese is selected"
    else:
        return "Specify E or J"

def list_sound():
    file = open(join(mp3_dir, list_txt))
    text = file.read()
    file.close()
    return text
