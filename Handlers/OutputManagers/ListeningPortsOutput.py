import eel

from Singletons import Ports


class ListeningPortsOutput:
    """
    Manages the output of the listenning ports for the GUI (sends the Data to the javascript part)
    """

    @staticmethod
    def write(what):
        eel.addScannedIP(what.__str__(), Ports.ports)
