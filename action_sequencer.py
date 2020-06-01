class action_sequencer:
    # retrieve the action sequence
    def __init__(self, actions):
        self.action_sequence = actions

    # run each action in the sequence sequentially
    def run(self):
        for bot_action in self.action_sequence:
            bot_action.run()
