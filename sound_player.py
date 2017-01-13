from os import listdir
from os.path import isfile, join
import pygame
import random

mp3_dir = 'mp3'
list_txt = 'soundlist.txt'
pygame.init()
pygame.mixer.init()
bath_songs = ["bath_1.mp3", "bath_2.mp3", "bath_3.mp3", "bath_4.mp3"]


"""
Sound player for music
"""
def play_random_music():
    # Plays random music from specified range of mp3 files in mp3 subdirectory
    files = [join(mp3_dir, f) for f in listdir(mp3_dir) if isfile(join(mp3_dir, f)) and f.endswith('mp3') and f in bath_songs]
    file = random.choice(files)
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

def play_id_music(id):
    # Plays a specific music given ID bath_<ID>.mp3 from mp3 subdirectory 
    file = 'bath_{}.mp3'.format(id)
    if not isfile(join(mp3_dir, file)):
        print("Could not find file {}".format(file))
        return
    pygame.mixer.music.load(join(mp3_dir,file))
    pygame.mixer.music.play()

def list_music():
    file = open(join(mp3_dir, list_txt))
    text = file.read()
    file.close()
    return text
