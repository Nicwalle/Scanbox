import eel


class UIErrorOutput:
    """
    Manages the UI errors output by sending the error object to the javascript for display on the GUI
    """

    @staticmethod
    def write(what):
        eel.addError(what.to_json())
