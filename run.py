import time
import re
import sound_player
import camera_control
import Remote_Outlet.control

from slackbot.bot import Bot, respond_to, default_reply
from temp_reader import read_device_file
from camera_control import camera_capture
from Remote_Outlet.control import turn_on, turn_off

monitor_flag = False            # Monitoring or not
new_interval = False            # When monitor command is entered it turned to True
set_flag = False                # When set command is checking temparature, it's True

command_help_file = 'command.txt'

measurement_interval = 2        # Temparature Measurement interval (seconds) for set command
monitor_interval = 60           # Keeps interval minutes for monitoring home
target_temp = 0.0               # Keeps the target temparature for bathtub
fire_warning = 70               # Threshold to judge fire when monitoring home
heater_1_outlet_number = "4"
heater_2_outlet_number = "5"


fire_alarm = "119"              # Sound number for fire alarm
theft_alarm = "110"             # Sound number for theft alarm

estimate_message_sent = [False, False, False, False]
estimate_message_sound = ["800", "801", "802", "803"]
estimate_message_minutes = ["5", "10", "15", "20"]
skip_first_message = True       # First estimation message could be unrelyable

@respond_to("hi", re.IGNORECASE)
def hi(message):
    message.reply('Hello world')

@respond_to("temp", re.IGNORECASE)
def return_temp(message):
    message.reply('Temperature is {} degrees'.format(read_device_file()))

@respond_to("set (\d+\.?\d*)", re.IGNORECASE)
def set_temp(message, set_temp): 
    global set_flag
    global target_temp
    global skip_first_message
    
    estimation_started = False
    measurement_started = False
    target_temp = set_temp
    if(set_flag):
        message.reply("Now target temparature is set to {} degrees".format(set_temp))
    else:
        finish_in_minutes = 0.0             # estimate remaining time in minutes
        average_increment = 0.0             # avarage increment for 1 minute
        set_flag = True
        message.reply("O.K., I'll let you know when the temparature reaches to {} degrees".format(target_temp))
        previous_time = time.time()
        current_temp = read_device_file()
        if int(target_temp) - int(current_temp) < 8:      # Less than 30 minutes expected -> Short average period
            average_period = 5
        else:
            average_period - 10
        while True:
            previous_temp = current_temp
            time.sleep(measurement_interval)
            current_time = time.time()
            current_temp = read_device_file()
            if current_temp > float(target_temp):
                break
            if not estimation_started:
                if int(current_time - previous_time) >= 120:             # wait for 2 minutes to be stable
                    estimation_started = True
                    previous_time = current_time
            else:
                if not measurement_started:
                    if current_temp > previous_temp:                    # Start measurement at the timing of temparature increase
                        measurement_started = True
                        start_time = current_time
                        start_temp = current_temp
                else:
                    if int(current_time - previous_time) >= (average_period * 60):  # Calculate average for every average period minutes
                        if current_temp > previous_temp:   # Waiting for temparature increase timing
                            previous_time = current_time
                            measurement_started = False
                            average_increment = (current_temp - start_temp) * 60 / (current_time - start_time)  # increment for 1 minute
##                            print "[{}] Average updated: {} - {} -> {} degree increment in {} seconds".format(time.strftime('%H:%M:%S'), average_increment, start_temp, current_temp, int(current_time - start_time))
                if average_increment > 0:            # eastimete if average increase is positive
                    finish_in_minutes = (float(target_temp) - current_temp) / average_increment
                    if finish_in_minutes < 5.0:
                        estimate_message(0, current_temp, message)
                    elif finish_in_minutes < 10.0:
                        estimate_message(1, current_temp, message)
                    elif finish_in_minutes < 15.0:
                        estimate_message(2, current_temp, message)
                    elif finish_in_minutes < 20.0:
                        estimate_message(3, current_temp, message)
                    else:
                        skip_first_message = False
        message.reply("[{}] The temparature reached to {} degrees".format(time.strftime(
        '%H:%M:%S'), target_temp))
        set_flag = False
        sound_player.play_bath_sound()
        turn_off(heater_1_outlet_number)
        turn_off(heater_2_outlet_number)

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
                    if current_temp > fire_warning:
                        message.reply("#### EMERGENCY EMERGENCY TEMPARATURE REACHED {} ####".format(fire_warning))
                        sound_player.play_id_sound(fire_alarm)
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

def estimate_message(id, temp, message):
    global skip_first_message

    if(not estimate_message_sent[id]):
        estimate_message_sent[id] = True
        if not skip_first_message:
            message.reply("[{}] {} degrees - {} more minutes".format(time.strftime('%H:%M:%S'), temp, estimate_message_minutes[id]))
            sound_player.play_id_sound(estimate_message_sound[id])
        else:
            skip_first_message = False

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
