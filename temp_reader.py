import os
import glob
import random

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

use_fake_data = False
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')

if len(device_folder) != 1:
    print("Could not find sensor... creating fake data")
    use_fake_data = True
else:
    device_file = device_folder[0] + '/w1_slave'

def read_device_file():
    if not use_fake_data:
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
	index = lines[1].find('t=')
        return round(float(lines[1][index+2:])/1000, 1)
    else:
        return random.randint(20,32)
