from os import listdir
from os.path import isfile, join
import pygame
import random

mp3_dir = 'mp3'
pygame.init()
pygame.mixer.init()

"""
Sound player for music
"""
def play_random_music():
    # Plays random music from list of mp3 files in mp3 subdirectory
    files = [join(mp3_dir, f) for f in listdir(mp3_dir) if isfile(join(mp3_dir, f)) and f.endswith('mp3')]
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
