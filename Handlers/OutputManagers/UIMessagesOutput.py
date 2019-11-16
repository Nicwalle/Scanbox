import eel


class UIMessagesOutput:
    """
    Manages the warning messages output by sending it to the javascript for display on the GUI
    """

    @staticmethod
    def write(what):
        eel.addMessage(what.to_json())
