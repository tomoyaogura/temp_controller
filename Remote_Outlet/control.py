import subprocess
from Remote_Outlet import config
import time
import random

from temp_reader import read_device_file

outlet_status = [0, 0, 0, 0, 0]             # 0:Off, 1:on, 2:random mode now off, 3:random mode now on
random_mode = [0, 0, 0, 0, 0]               # 0: random on/off, 1: solar mode
sunset_hours = [16, 16, 17, 18, 19, 20, 20, 19, 19, 18, 16, 16]
sunrise_hours = [7, 7, 6, 6, 6, 5, 5, 6, 6, 6, 7, 7]
on_min = 10
on_max = 30
off_min = 30
off_max = 240
sense_interval = 5                                  # check every 5 seconds

solar_run = 180                                     # run pump 180 seconds
solar_wait = 600                                    # with 10 minutes wait
temp_threshold1 = 0.2                               # if temparature gain is less than this, 3 X wait time 
temp_threshold2 = 0.4                               # if temparature gain is less than this, 2 X wait time

def turn_on(outlet_id):
    global  outlet_status
    if(outlet_id in config.CODES):
        _send_pulse(config.CODES[outlet_id][0])
        outlet_status[int(outlet_id)-1] = 1
        return "Outlet {} ON".format(outlet_id)
    else:
        return "No outlet {} in the database".format(outlet_id)

def turn_off(outlet_id):
    global  outlet_status
    if(outlet_id in config.CODES):
        _send_pulse(config.CODES[outlet_id][1])
        outlet_status[int(outlet_id)-1] = 0
        return "Outlet {} OFF".format(outlet_id)
    else:
        return "No outlet {} in the database".format(outlet_id)

def random_on_off(outlet_id, mode):
    global  outlet_status
    status_index = int(outlet_id)-1
    random_mode[status_index] = mode
    if(outlet_id in config.CODES):
        if outlet_status[status_index] >= 2:            # Already random -> do nothing
            return "Outlet {} is already set random or solar".format(outlet_id)
        outlet_status[status_index] = 2                 # Set random status
        previous_time = time.time()
        trigger_seconds = 0                             # Turn on immediately at start
        while True:
            if outlet_status[status_index] < 2:         # Status is set to not random
                break
            current_time = time.time()
            if current_time - previous_time > trigger_seconds:
                if outlet_status[status_index] == 2:     # Now off -> turn on
                    if(random_mode[status_index] == 0):
                        trigger_seconds = random.randint(on_min, on_max) * 60
                        now = time.localtime()
                        if now.tm_hour < sunrise_hours[now.tm_mon-1] or now.tm_hour > sunset_hours[now.tm_mon-1]:
                            _send_pulse(config.CODES[outlet_id][0])
                            outlet_status[status_index] = 3     # change status to random on
                    else:
                        trigger_seconds = solar_run
                        now = time.localtime()
                        if now.tm_hour >= sunrise_hours[now.tm_mon-1] + 3 and now.tm_hour <= sunset_hours[now.tm_mon-1] - 2:
                            _send_pulse(config.CODES[outlet_id][0])
                            outlet_status[status_index] = 3     # change status to random on
                            start_temp = read_device_file()
                            print("[{}] Pump starting at {} degrees".format(time.strftime('%H:%M'), start_temp))
                else:
                    if(random_mode[status_index] == 0):
                        trigger_seconds = random.randint(off_min, off_max) * 60
                    else:
                        trigger_seconds = solar_wait
                        if(random_mode[status_index] == 2):          # solar with temparature monitoring
                            end_temp = read_device_file()
                            temp_gain = end_temp - start_temp
                            print("[{}] {} --> {} Temparature gain is {}".format(time.strftime('%H:%M'), start_temp, end_temp, temp_gain))
                            if(temp_gain < 0):     # temparature gain is negative -> exit solar mode 
                                print("No temparature gain -> exit solar mode")
                                outlet_status[status_index] = 0
                                _send_pulse(config.CODES[outlet_id][1])
                                break
                            if(temp_gain < temp_threshold1):       # Very little temparature gain -> 3 X the wait time
                                trigger_seconds = solar_wait * 3
                                print("Very little temparature gain -> 3 X the wait time")
                            elif(temp_gain < temp_threshold2):     # Not enough temprature gain -> 2X the wait time
                                trigger_seconds = solar_wait * 2
                                print("Not enough tempararture gain -> 2 X wait time")
                    outlet_status[status_index] = 2
                    _send_pulse(config.CODES[outlet_id][1])
                previous_time = current_time
            time.sleep(sense_interval)
        return "Random or solar on/off outlet {} terminated".format(outlet_id)
    else:
        return "No outlet {} in the database".format(outlet_id)

def is_random():
    global outlet_status
    if(outlet_status[0] >= 2 or outlet_status[1] >= 2 or outlet_status[2] >= 2):
        return(True)
    return(False)

# Flickers outlet_id
def flicker(outlet_id, on_duration=1):
    import time
    turn_on(outlet_id)
    time.sleep(on_duration)
    turn_off(outlet_id)
    return("Flicker")
    
# Uses codesend to send_pulse
def _send_pulse(pulse_id):
    args = [config.CODESEND_DIR, '-l', str(config.PULSE), str(pulse_id)]
    subprocess.call(args)

