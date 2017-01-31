import subprocess
import config
import time
import random

outlet_status = [0, 0, 0, 0, 0]             # 0:Off, 1:on, 2:random mode now off, 3:random mode now on
sunset_hours = [16, 17, 18, 19, 19, 20, 20, 19, 19, 18, 17, 16]
sunrise_hours = [7, 6, 6, 5, 5, 4, 4, 5, 5, 6, 6, 7]
on_min = 10
on_max = 30
off_min = 30
off_max = 240
sense_interval = 5                                     # check every 5 seconds

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

def random_on_off(outlet_id):
    global  outlet_status
    status_index = int(outlet_id)-1
    if(outlet_id in config.CODES):
        if outlet_status[status_index] >= 2:            # Already random -> do nothing
            return "Outlet {} is already set random".format(outlet_id)
        outlet_status[status_index] = 2                 # Set random status
        previous_time = time.time()
        trigger_seconds = 0                             # Turn on immediately at start
        while True:
            if outlet_status[status_index] < 2:         # Status is set to not random
                break
            current_time = time.time()
            if current_time - previous_time > trigger_seconds:
                if outlet_status[status_index] == 2:     # Now off -> turn on
                    trigger_seconds = random.randint(on_min, on_max) * 60
                    now = time.localtime()
                    if now.tm_hour < sunrise_hours[now.tm_mon-1] or now.tm_hour > sunset_hours[now.tm_mon-1]:
                        _send_pulse(config.CODES[outlet_id][0])
                        outlet_status[status_index] = 3     # change status to random on
                else:
                    _send_pulse(config.CODES[outlet_id][1])
                    trigger_seconds = random.randint(off_min, off_max) * 60
                    outlet_status[status_index] = 2
                previous_time = current_time
            time.sleep(sense_interval)
        return "Random on/off outlet {} terminated".format(outlet_id)
    else:
        return "No outlet {} in the database".format(outlet_id)

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

