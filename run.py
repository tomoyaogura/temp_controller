import time
import threading
import re

from slackbot.bot import Bot, respond_to, default_reply
from temp_reader import read_device_file

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
    while (read_device_file() < float(target_temp)):
	time.sleep(2)
    message.reply("The temparature reached to {} degrees".format(read_device_file()))


@default_reply
def my_default_handler(message):
    message.reply('"Temp" returns current temparature and "Set XX" set the target temparature for notification')


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
