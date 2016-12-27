from slackbot.bot import Bot, respond_to

@respond_to("hi")
def hi(message):
    message.reply('Hello world')

@respond_to("temperature")
def hi(message):
    message.reply('Temperature is 32 degrees')

def main():
    bot = Bot()
    bot.run()

if __name__ == "__main__":
    main()
