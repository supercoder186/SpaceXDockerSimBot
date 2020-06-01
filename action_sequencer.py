class action_sequencer:
    def __init__(self, actions):
        self.action_sequence = []
        for bot_action in actions:
            self.action_sequence.append(bot_action)

    def run(self):
        for bot_action in self.action_sequence:
            bot_action.run()
