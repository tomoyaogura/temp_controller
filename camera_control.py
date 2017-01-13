import pygame
import pygame.camera
from pygame.locals import *

pygame.init()
pygame.camera.init()
cam = pygame.camera.Camera("/dev/video0", (640,480))
cam.start()

def camera_capture():
    pygame.image.save(cam.get_image(), "image.jpg")
    return "image.jpg"

