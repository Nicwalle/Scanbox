import json

from ScanBox import ScanBox
from Singletons import Inputs


def init():
    try:
        Inputs.inputs = json.load(open("scanbox/inputs/inputs.json", "r"))
        Inputs.inputs["UI"] = False
    except IOError:
        print("Unable to open inputs file. Please, configure the inputs by running the python scanbox_GUI.py command")
    scanbox = ScanBox()
    scanbox.start()


if __name__ == "__main__":
    init()
