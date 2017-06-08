import time
import threading

from Adafruit_LED_Backpack import SevenSegment

from temp_reader import read_device_file

class Temp_Display():
    def __init__(self, change_dur):
        self.display = SevenSegment.SevenSegment()
        self.display.begin()
        self.set_mode = False
        self.target_temp = 0.0
        self.change_dur = change_dur

        display_thread = threading.Thread(target=self.main_loop)
        display_thread.start()

    def set_temp(self, temp):
        self.set_mode = True
        self.target_temp = temp

    def unset_temp(self):
        self.set_mode = False

    def display_target_temp(self):
        self.display.clear()
        self.display.print_float(self.target_temp, decimal_digits=1)
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
                self.display_time()
                time.sleep(self.change_dur)
            else:
                self.display_time()
                time.sleep(self.change_dur)
                self.display_temp()
                time.sleep(self.change_dur)
