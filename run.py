from slackbot.bot import Bot, respond_to
from temp_reader import read_device_file

@respond_to("hi")
def hi(message):
    message.reply('Hello world')

@respond_to("temperature")
def return_temp(message):
    message.reply('Temperature is {} degrees'.format(read_device_file()))

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
