from enum import Enum, auto
import discord
import re

class State(Enum):
    REPORT_START = auto()
    AWAITING_MESSAGE = auto()
    MESSAGE_IDENTIFIED = auto()
    REPORT_COMPLETE = auto()

class Report:
    START_KEYWORD = "report"
    CANCEL_KEYWORD = "cancel"
    HELP_KEYWORD = "help"

    def __init__(self, client):
        self.state = State.REPORT_START
        self.client = client
        self.message = None
    
    async def handle_message(self, message):
        '''
        This function makes up the meat of the user-side reporting flow. It defines how we transition between states and what 
        prompts to offer at each of those states. You're welcome to change anything you want; this skeleton is just here to
        get you started and give you a model for working with Discord. 
        '''

        if message.content == self.CANCEL_KEYWORD:
            self.state = State.REPORT_COMPLETE
            return ["Report cancelled."]
        
        if self.state == State.REPORT_START:
            reply =  "Thank you for starting the reporting process. "
            reply += "Say `help` at any time for more information.\n\n"
            reply += "Please copy paste the link to the message you want to report.\n"
            reply += "You can obtain this link by right-clicking the message and clicking `Copy Message Link`."
            self.state = State.AWAITING_MESSAGE
            return [reply]
        
        found_message = message

        if self.state == State.AWAITING_MESSAGE:
            # Parse out the three ID strings from the message link
            m = re.search('/(\d+)/(\d+)/(\d+)', message.content)
            if not m:
                return ["I'm sorry, I couldn't read that link. Please try again or say `cancel` to cancel."]
            guild = self.client.get_guild(int(m.group(1)))
            if not guild:
                return ["I cannot accept reports of messages from guilds that I'm not in. Please have the guild owner add me to the guild and try again."]
            channel = guild.get_channel(int(m.group(2)))
            if not channel:
                return ["It seems this channel was deleted or never existed. Please try again or say `cancel` to cancel."]
            try:
                found_message = await channel.fetch_message(int(m.group(3)))
            except discord.errors.NotFound:
                return ["It seems this message was deleted or never existed. Please try again or say `cancel` to cancel."]

            # Here we've found the message - it's up to you to decide what to do next!
            self.state = State.MESSAGE_IDENTIFIED
            await message.author.send("I found this message:")
            await message.author.send("```" + found_message.author.name + ": " + found_message.content + "```")
            reply = "Please select the reason for reporting this message:"
            await message.author.send(reply)

            options = ":one: Harassment/Bullying\n"
            options += ":two: False or Misleading Information\n"
            options += ":three: Violence/Graphic Imagery\n"
            options += ":four: Spam\n"
            options += ":five: Something Else\n"
            options_msg = await message.author.send(options)
            await options_msg.add_reaction('1️⃣')
            await options_msg.add_reaction('2️⃣')
            await options_msg.add_reaction('3️⃣')
            await options_msg.add_reaction('4️⃣')
            await options_msg.add_reaction('5️⃣')
        
        if self.state == State.MESSAGE_IDENTIFIED:
            return ["ORIGINAL", found_message.content, found_message.author.name, found_message]

        return []

    # def set_complete(self):
    #     self.state = State.REPORT_COMPLETE
    #     return ["Report Completed. To submit another report, paste a new message link."]

    def report_complete(self):
        return self.state == State.REPORT_COMPLETE