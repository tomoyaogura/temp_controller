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

measurement_interval = 5        # Temparature Measurement interval (seconds) for set command

monitor_interval = 60           # Keeps interval minutes for monitoring home
innermost_loop_count = 22       # Innnermost 22 loops for about 1 minutes 
motor_outlet_number = "2"       # Water pomp outlet number for bathtub circulation
target_temp = 0.0               # Keeps the target temparature for bathtub
fire_warning = 80               # Threshold to judge fire when monitoring home

fire_alarm = "119"              # Sound number for fire alarm

estimate_message_sent = [False, False, False, False]
estimate_message_sound = ["900", "901", "902", "903"]
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
    target_temp = set_temp
    if(set_flag):
        message.reply("Now target temparature is set to {} degrees".format(set_temp))
    else:
        finish_in_minutes = 0.0             # estimate remaining time in minutes
        previous_temp = 0.0
        current_temp = 0.0
        increment = 0.0
        sample_count = 0                    # number of sample for the avarage
        average_increment = 0.0             # avarage increment for 1 minute
        set_flag = True
        message.reply("O.K., I'll let you know when the temparature reaches to {} degrees".format(target_temp))
        motor_on = False
        previous_time = time.time()        # record set start time
        while True:
            current_temp = read_device_file()
            if current_temp > float(target_temp):
                break
            time.sleep(measurement_interval)
            if motor_on:
                turn_off(motor_outlet_number)
            else:
                turn_on(motor_outlet_number)
            motor_on = not motor_on
            current_time = time.time()
            if estimation_started:                                  # estimation started
                if int(current_time - previous_time) >= 120:                                # update avarage increase every 2 minutes
                    previous_time = current_time
                    if sample_count >= 1:                               # can calculate increment
                        increment = (current_temp - previous_temp) /2   # increment for 1 minute
                        average_increment = (average_increment * (sample_count - 1) + increment )/sample_count
##                        print "Average updated: ", sample_count, increment, average_increment
                    previous_temp = current_temp
                    sample_count += 1
                if average_increment > 0:                           # eastimete finish if average increase exists
                    finish_in_minutes = (float(target_temp) - current_temp) / average_increment
##                    print target_temp, current_temp, average_increment, finish_in_minutes
                    if finish_in_minutes < 5.0:
                      estimate_message(0, message)
                    elif finish_in_minutes < 10.0:
                        estimate_message(1, message)
                    elif finish_in_minutes < 15.0:
                        estimate_message(2, message)
                    elif finish_in_minutes < 20.0:
                        estimate_message(3, message)
                    else:
                        skip_first_message = False
            else:
                if int(current_time - previous_time) >= 300:         # Wait for 5 minutes increase to be stable
                    estimation_started = True
##                    print "Estimation start"
                    previous_time = current_time
        message.reply("{} The temparature reached to {} degrees".format(time.strftime(
        '%H:%M'), target_temp))
        set_flag = False
        sound_player.play_bath_sound()
        turn_off(motor_outlet_number)

@respond_to("play (\d+)", re.IGNORECASE)
def sound_play(message, mp3_id):
    message.reply(sound_player.play_id_sound(mp3_id))

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
            while True:
                capture = True
                minutes = 0
                while True:
                    for i in range(1, innermost_loop_count):   # This loop would takle about 1 minutes
                        if(new_interval):
                        # New interval time is set
                            if(monitor_interval == 0):
                                # 0 -> Cancel monitoring
                                monitor_flag = False
                                break
                        # Non 0 -> continue monitoring with new interval time
                            else:
                                new_interval = False
                                capture = True  # forse to capture when interval is changed
                                i = 1           # Reset counter
                                message.reply("Monitoring interval is set to {} minutes".format(monitor_interval))
                        if(read_device_file() > fire_warning):
                            message.reply("#### EMERGENCY EMERGENCY TEMPARATURE REACHED {} ####".format(fire_warning))
                            sound_player.play_id_sound(fire_alarm)
                            capture = True  # forse to capture in case of fire
                        if(capture):
                            capture = False
                            fpath = camera_capture()
                            message.channel.upload_file(fpath, fpath)
                        time.sleep(2)
                    if(not monitor_flag):
                        break
                    minutes += 1
                    if(minutes >= monitor_interval):
                        break
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

def estimate_message(id, message):
    global skip_first_message

    if(not estimate_message_sent[id]):
        estimate_message_sent[id] = True
        if not skip_first_message:
            message.reply("{} Estimate {} minutes".format(time.strftime('%H:%M'), estimate_message_minutes[id]))
            sound_player.play_id_sound(estimate_message_sound[id])
        else:
            skip_first_message = False

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
