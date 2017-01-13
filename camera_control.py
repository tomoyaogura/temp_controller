import pygame
import pygame.camera
from pygame.locals import *
import time
import subprocess
pygame.init()
pygame.camera.init()
def camera_capture():
    cam = pygame.camera.Camera("/dev/video0", (640,480))
    cam.start()
    pygame.image.save(cam.get_image(), "image.jpg")
    cam.stop()
    return "image.jpg"

