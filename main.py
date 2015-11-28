#
# This file is part of The Principles of Modern Game AI.
# Copyright (c) 2015, AiGameDev.com KG.
#

import vispy  # Main application support.
import window  # Terminal input and display.
import nltk.chat
import win32com.client
from win32com.client import constants

AGENT_RESPONSES = [
    (r'You are (worrying|scary|disturbing)',  # Pattern 1.
     ['Yes, I am %1.',  # Response 1a.
      'Oh, sooo %1.']),

    (r'Are you ([\w\s]+)\?',  # Pattern 2.
     ["Why would you think I am %1?",  # Response 2a.
      "Would you like me to be %1?"]),

    (r'',  # Pattern 3. (default)
     ["Is everything OK?",  # Response 3a.
      "Can you still communicate?"])
]


class HAL9000(object):
    def __init__(self, terminal):
        """Constructor for the agent, stores references to systems and initializes internal memory.
        """
        self.terminal = terminal
        self.location = 'unknown'
        self.thing = ''
        self.greet = False

        self.chatbot = nltk.chat.Chat(AGENT_RESPONSES, nltk.chat.util.reflections)
        self.voice = win32com.client.gencache.EnsureDispatch("SAPI.SpVoice")

    def on_input(self, evt):
        """Called when user types anything in the terminal, connected via event.
        """
        if not self.greet:
            self.terminal.log("Hello Human. This is HAL.", align='right', color='#00805A')
            self.greet = True

            self.voice.Speak("Hello Human. This is HAL.", constants.SVSFlagsAsync)

        elif evt.text == 'Where am I?':
            self.terminal.log('You are in the {}, Human.'.format(self.location), align='right', color='#00805A')
            self.voice.Speak('You are in the {}, Human.'.format(self.location), constants.SVSFlagsAsync)

        else:
            # self.terminal.log("Can you still communicate?", align='right', color='#00805A')
            resp = self.chatbot.respond(evt.text)
            self.terminal.log(resp, align='right', color='#00805A')

            self.voice.Speak(resp, constants.SVSFlagsAsync)

    def on_command(self, evt):
        """Called when user types a command starting with `/` also done via events.
        """
        if evt.text == 'quit':
            vispy.app.quit()

        elif evt.text.startswith('relocate'):
            self.location = evt.text[9:]
            self.terminal.log('', align='center', color='#404040')
            self.terminal.log('\u2014 Now in the {}. \u2014'.format(self.location), align='center', color='#404040')

            self.voice.Speak('\u2014 Now in the {}. \u2014'.format(self.location), constants.SVSFlagsAsync)

        elif evt.text.startswith('use'):
            self.thing = evt.text[4:]
            self.terminal.log("What do you think to do with that {}, Human?".format(self.thing),
                              align='right', color='#00805A')

            self.voice.Speak("What do you think to do with that {}, Human?".format(self.thing), constants.SVSFlagsAsync)

        else:
            self.terminal.log('Command `{}` unknown.'.format(evt.text), align='left', color='#ff3000')
            self.terminal.log("I'm afraid I can't do that.", align='right', color='#00805A')

    def update(self, _):
        """Main update called once per second via the timer.
        """
        pass


class Application(object):
    def __init__(self):
        # Create and open the window for user interaction.
        self.window = window.TerminalWindow()

        # Print some default lines in the terminal as hints.
        self.window.log('Operator started the chat.', align='left', color='#808080')
        self.window.log('HAL9000 joined.', align='right', color='#808080')

        # Construct and initialize the agent for this simulation.
        self.agent = HAL9000(self.window)

        # Connect the terminal's existing events.
        self.window.events.user_input.connect(self.agent.on_input)
        self.window.events.user_command.connect(self.agent.on_command)

    def run(self):
        timer = vispy.app.Timer(interval=1.0)
        timer.connect(self.agent.update)
        timer.start()

        vispy.app.run()


if __name__ == "__main__":
    vispy.set_log_level('WARNING')
    vispy.use(app='glfw')

    app = Application()
    app.run()
