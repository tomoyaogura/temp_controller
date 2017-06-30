import time
import threading
import sound_player
from Remote_Outlet.control import turn_on, turn_off

from Adafruit_LED_Backpack import SevenSegment
import RPi.GPIO as GPIO

from temp_reader import read_device_file

# BUTTON_PIN = 26
LED_PIN = 16
GPIO.setmode(GPIO.BCM)

DISPLAY_INTERVAL = 2
START_TEMP = 40.0
MAX_TEMP = 45.0

HEATER_1_OUTLET = "4"
HEATER_2_OUTLET = "5"

estimate_message_sent = [False, False, False, False]
estimate_message_sound = ["800", "801", "802", "803"]
estimate_message_minutes = ["5", "10", "15" , "20"]

class Temp_Monitor():
    def __init__(self):

        self.display = SevenSegment.SevenSegment()
        self.display.begin()
        self.is_heating = False
        self.previous_target = 0.0
        self.target_temp = 0.0
        self.display_duration = DISPLAY_INTERVAL
        self.loop_counter = 0

        self.skip_first_message = True
        self.finish_in_minutes = 0.0
        self.message = 0

        # Button + LED Setup
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)

        monitor_thread = threading.Thread(target = self.start_monitoring)
        monitor_thread.start()

    def start_monitoring(self):
        while True:
            if(self.previous_target <> self.target_temp):
                if(self.target_temp <> 0.0):
                    self.respond("Now target temparature is set to {} degrees".format(self.target_temp))
                else:
                    self.respond("Temparature monitoring stopped")
                self.previous_target = self.target_temp
            if(self.target_temp > 0.0):             # heating process started
                estimation_started = False
                measurement_started = False
                GPIO.output(LED_PIN, GPIO.HIGH)     # Turn on LED lamp for temo monitoring mode
                skip_message = True                 # skip first message because it may be unreliable
                self.finish_in_minutes = 0.0        # estimate remaining time in minutes
                average = 0.0                       # avarage increment for 1 minute
                self.is_heating = True
                self.respond("O.K., I'll let you know when the temparature reaches to {} degrees".format(self.target_temp))
                previous_time = time.time()
                current_temp = read_device_file()
                average_period = 5
                while True:
                    previous_temp = current_temp
                    if(self.loop_counter % 3 == 0):
                        self.display_temp()
                    elif(self.loop_counter % 3 == 1):
                        self.display_target_temp()
                    else:
                        self.display_time_until_done()
                    self.loop_counter = self.loop_counter + 1
                    time.sleep(self.display_duration)
                    current_time = time.time()
                    current_temp = read_device_file()
                    if current_temp > float(self.target_temp):
                        break
                    if not estimation_started:
                        if int(current_time - previous_time) >= 180:             # wait for 3 minutes to be stable
                            estimation_started = True
                            previous_time = current_time
                            initial_time = current_time
                            initial_temp = current_temp
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
                                    average_increment_lap = (current_temp - start_temp) * 60 / (current_time - initial_time)
                                    average_increment_total = (current_temp - initial_temp) * 60 / (current_time - initial_time)    # increment for 1 minutes from estimation start time
                                    average = (average_increment_lap + average_increment_total)/2
                                    print "[{}] Lap average: {} - {} -> {} degree increment in {} seconds".format(time.strftime('%H:%M:%S'), average_increment_lap, start_temp, current_temp, int(current_time - start_time))
                                    print "Total average: {} New average {}".format(average_increment_total, average)
                        if average > 0.0:            # eastimete if average increase is positive
                            self.finish_in_minutes = (float(self.target_temp) - current_temp) / average
                            if self.finish_in_minutes < 5.0:
                                self.estimate_message(0, current_temp)
                            elif self.finish_in_minutes < 10.0:
                                self.estimate_message(1, current_temp)
                            elif self.finish_in_minutes < 15.0:
                                self.estimate_message(2, current_temp)
                            elif self.finish_in_minutes < 20.0:
                                self.estimate_message(3, current_temp)
                            else:
                                self.skip_first_message = False
                if(self.target_temp <> 0):
                    self.respond("[{}] The temparature reached to {} degrees".format(time.strftime('%H:%M:%S'), self.target_temp))
                self.is_heating = False
                self.finish_in_minutes = 0.0
                GPIO.output(LED_PIN, GPIO.LOW)
                turn_off(HEATER_1_OUTLET)
                turn_off(HEATER_2_OUTLET)
                if(self.target_temp >= START_TEMP):
                    sound_player.play_bath_sound()
                self.target_temp = 0
            else:
                if(self.loop_counter % 2 == 0):
                    self.display_time()
                else:
                    self.display_temp()
                self.loop_counter = self.loop_counter + 1
                time.sleep(self.display_duration)
   
    def display_target_temp(self):
        self.display.clear()
        self.display.print_float(self.target_temp, decimal_digits=1)
        self.display.write_display()

    def display_time_until_done(self):
        self.display.clear()
        if(self.finish_in_minutes > 0.0 and self.finish_in_minutes < 60.0):
            minutes = int(self.finish_in_minutes)
            seconds = int(self.finish_in_minutes * 60.0 - minutes*60)
            self.display.print_number_str("%d%02d" % (minutes, seconds))
            self.display.set_colon(True)
        else:
            self.display.print_number_str("----")
        self.display.write_display()


    def display_time(self):
        self.display.clear()
        self.display.print_number_str(time.strftime('%H%M'))
        self.display.set_colon(True)
        self.display.write_display()

    def display_temp(self):
        self.display.clear()
        self.display.print_float(read_device_file(), decimal_digits=1)
        self.display.write_display()

    def respond(self, text):
        if(self.message):
            self.message.reply(text)
        
    def estimate_message(self, id, temp):
        if(not estimate_message_sent[id]):
            estimate_message_sent[id] = True
            if not self.skip_first_message:
                self.respond("[{}] {} degrees - {} more minutes".format(time.strftime('%H:%M:%S'), temp, estimate_message_minutes[id]))
                sound_player.play_id_sound(estimate_message_sound[id])
            else:
                self.skip_first_message = False
