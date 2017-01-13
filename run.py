import time
import threading
import re
import sound_player
import camera_control
import Remote_Outlet.control

from slackbot.bot import Bot, respond_to, default_reply
from temp_reader import read_device_file
from camera_control import camera_capture
from Remote_Outlet.control import turn_on, turn_off


measurement_interval = 5
outlet_number = "304-2"
target_temp = 0.0

@respond_to("hi", re.IGNORECASE)
def hi(message):
    message.reply('Hello world')

@respond_to("temp", re.IGNORECASE)
def return_temp(message):
    message.reply('Temperature is {} degrees'.format(read_device_file()))

@respond_to("set (\d+\.?\d*)", re.IGNORECASE)
def set_temp(message, target_temp): 
    message.reply("O.K., I'll let you know when the temparature reaches to {} degrees".format(target_temp))
    motor_on = False
    while (read_device_file() < float(target_temp)):
        time.sleep(measurement_interval)
        if(motor_on):
            turn_off(outlet_number)
        else:
            turn_on(outlet_number)
        motor_on = not motor_on
    message.reply("The temparature reached to {} degrees".format(read_device_file()))
    sound_player.play_random_music()
    turn_off(outlet_number)
@respond_to("play (\d+)", re.IGNORECASE)
def sound_play(message, mp3_id):
    sound_player.play_id_music(mp3_id)

@respond_to("list", re.IGNORECASE)
def print_list(message):
    message.reply(sound_player.list_music())

@respond_to("view", re.IGNORECASE)
def return_capture(message):
    fpath = camera_capture()
    message.channel.upload_file(fpath, fpath)

@default_reply
def my_default_handler(message):
    message.reply('"Temp" returns current temparature\n"Set XX" sets the target temparature for notification\n"Play XX" plays sound')


def check_temp():
    threading.Timer(10.0, check_temp).start()
    if(read_device_file() >= target_temp):
	threading.end()
	message.reply('Reached to the target temparature')









def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
