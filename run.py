import time
import re
import sound_player
import camera_control
import Remote_Outlet.control
import RPi.GPIO as GPIO

BUTTON_PIN = 26
GPIO.setmode(GPIO.BCM)

from slackbot.bot import Bot, respond_to, default_reply
from temp_reader import read_device_file
from camera_control import camera_capture
from display import Temp_Monitor
from Remote_Outlet.control import turn_on, turn_off, random_on_off
              
command_help_file = 'command.txt'

FIRE_WARNING = 70               # Threshold to judge fire when monitoring home
FIRE_ALARM = "119"              # Sound number for fire alarm
THEFT_ALARM = "110"             # Sound number for theft alarm

START_TEMP = 40.0
MAX_TEMP = 45.0

temp_monitor = Temp_Monitor()

def set_button(channel):
    print("Button is pressed")
    if temp_monitor.is_heating:
        if (temp_monitor.target_temp >= MAX_TEMP):
            temp_monitor.target_temp = 0.0
        else:
            temp_monitor.target_temp = temp_monitor.target_temp + 1
    else:
        temp_monitor.target_temp = START_TEMP

# Button Setup
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=set_button, bouncetime=300)

monitor_flag = False
monitor_interval = 60
new_interval = False

@respond_to("hi", re.IGNORECASE)
def hi(message):
    message.reply('Hello world')

@respond_to("temp", re.IGNORECASE)
def return_temp(message):
    message.reply('Temperature is {} degrees'.format(read_device_file()))

@respond_to("set (\d+\.?\d*)", re.IGNORECASE)
def set_temp(message, set_temp):
    temp_monitor.message = message
    temp_monitor.target_temp = float(set_temp)

@respond_to("play (\d+)", re.IGNORECASE)
def sound_play(message, mp3_id):
    message.reply(sound_player.play_id_sound(mp3_id))

@respond_to("lang ([EeJj])", re.IGNORECASE)
def language_set(message, lang):
    message.reply(sound_player.sound_language_preference(lang))

@respond_to("list", re.IGNORECASE)
def print_list(message):
    message.reply(sound_player.list_sound())

@respond_to("on (\d+)", re.IGNORECASE)
def outlet_on(message, switch_id):
    message.reply(turn_on(switch_id))

@respond_to("off (\d+)", re.IGNORECASE)
def outlet_off(message, switch_id):
    message.reply(turn_off(switch_id))

@respond_to("random (\d+)", re.IGNORECASE)
def outlet_random(message, switch_id):
    message.reply(random_on_off(switch_id, 0))

@respond_to("solar (\d+)", re.IGNORECASE)
def outlet_solar(message, switch_id):
    message.reply(random_on_off(switch_id, 1))

@respond_to("solart (\d+)", re.IGNORECASE)
def outlet_solar(message, switch_id):
    message.reply(random_on_off(switch_id, 2))

@respond_to("view", re.IGNORECASE)
def return_capture(message):
    fpath = camera_capture()
    message.channel.upload_file(fpath, fpath)

@respond_to("monitor (\d+)", re.IGNORECASE)
def monitor_home(message, interval):
    global monitor_flag
    global monitor_interval
    global new_interval

    new_interval = True

    monitor_interval = int(interval)

    if(not monitor_flag):
        if(monitor_interval > 0):
            # Monitoring start
            monitor_flag = True
            while True:         # Loop infinitely until monitoring is cancelled
                capture = True
                previous_time = time.time()
                while True:     # Loop for monitor interval
                    if(new_interval):
                        # New interval time is set
                        if(monitor_interval == 0):
                            # 0 -> Cancel monitoring
                            monitor_flag = False
                            break
                        # Non 0 -> continue monitoring with new interval time
                        else:
                            new_interval = False
                            capture = True      # forse to capture when interval is changed
                            previous_time = time.time()        # Timer reset
                            message.reply("Monitoring interval is set to {} minutes".format(monitor_interval))
                    current_temp = read_device_file()
                    if current_temp > FIRE_WARNING:
                        message.reply("#### EMERGENCY EMERGENCY TEMPARATURE REACHED {} ####".format(FIRE_WARNING))
                        sound_player.play_id_sound(FIRE_ALARM)
                        capture = True  # forse to capture in case of fire
                    if(capture):
                        capture = False
                        fpath = camera_capture()
                        message.channel.upload_file("{}".format(current_temp), fpath)
                    time.sleep(2)       # check Monitor command interval change every 2 seconds
                    current_time = time.time()
                    if int(current_time - previous_time) >= monitor_interval * 60:
                        capture = True
                        previous_time = current_time
                if(not monitor_flag):
                    break
            message.reply("Monitoring cancelled")
        else:
            message.reply("Monitoring not started")

@default_reply
def my_default_handler(message):
    file = open(command_help_file)
    text = file.read()
    file.close()
    message.reply(text)

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
