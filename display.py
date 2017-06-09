import time
import threading

from Adafruit_LED_Backpack import SevenSegment
import RPi.GPIO as GPIO

from temp_reader import read_device_file

BUTTON_PIN = 26
LED_PIN = 16
GPIO.setmode(GPIO.BCM)

class Temp_Display():
    def __init__(self, change_dur):
        self.display = SevenSegment.SevenSegment()
        self.display.begin()
        self.set_mode = False
        self.target_temp = 40.0
        self.change_dur = change_dur

        # Button + LED Setup
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=self.set_button, bouncetime=300)
        GPIO.setup(LED_PIN, GPIO.OUT)

        display_thread = threading.Thread(target=self.main_loop)
        display_thread.start()

    def set_temp(self, temp):
        GPIO.output(LED_PIN, GPIO.HIGH)
        self.set_mode = True
        self.target_temp = temp

    def unset_temp(self):
        GPIO.output(LED_PIN, GPIO.LOW)
        self.set_mode = False

    def display_target_temp(self):
        self.display.clear()
        self.display.print_float(self.target_temp, decimal_digits=1)
        self.display.write_display()

    def display_time_until_done(self):
        self.display.clear()
        self.display.print_number_str("1200")
        self.display.set_colon(True)
        self.display.write_display()

    def display_time(self):
        self.display.clear()
        self.display.print_number_str("1200")
        self.display.set_colon(True)
        self.display.write_display()

    def display_temp(self):
        self.display.clear()
        self.display.print_float(read_device_file(), decimal_digits=1)
        self.display.write_display()

    def main_loop(self):
        while(1):
            if self.set_mode:
                self.display_temp()
                time.sleep(self.change_dur)
                self.display_target_temp()
                time.sleep(self.change_dur)
                self.display_time_until_done()
                time.sleep(self.change_dur)
            else:
                self.display_time()
                time.sleep(self.change_dur)
                self.display_temp()
                time.sleep(self.change_dur)

    def set_button(self, channel):
        if self.set_mode:
            if (self.target_temp >= 45.0):
                self.unset_temp()
            else:
                self.set_temp(self.target_temp + 1)
        else:
            self.set_temp(float(40.0))

