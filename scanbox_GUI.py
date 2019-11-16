import json
import os

import eel
from ScanBox import ScanBox
from Singletons import Inputs

eel.init("web")


my_options = {
    'mode': "chrome-app",  # or "chrome-app",
    'host': 'localhost',
    'port': 8080
}


@eel.expose
def save_ips(content: str):
    try:
        fd = open("scanbox/inputs/ips.txt", "w+")
        fd.write(content)
        fd.close()
    except IOError:
        print("Unable to save input ips")


@eel.expose
def init():
    json_inputs = "{}"
    ips_input = ""
    try:
        fd = open("scanbox/inputs/inputs.json", "r")
        json_inputs: str = fd.read()
        fd.close()
    except IOError:
        pass

    try:
        fd = open("scanbox/inputs/ips.txt", "r")
        ips_input: str = fd.read()
        fd.close()
    except IOError:
        pass

    eel.fillInFields(json_inputs, ips_input)


@eel.expose
def start(inputs_json):
    Inputs.inputs = json.loads(inputs_json)
    scanbox = ScanBox()
    scanbox.start()


@eel.expose
def configure(inputs_json):
    fd = open("scanbox/inputs/inputs.json", "w+")
    fd.write(inputs_json)
    fd.close()


if not os.path.exists("scanbox"):
    os.mkdir("scanbox")

if not os.path.exists("scanbox/inputs"):
    os.mkdir("scanbox/inputs")

if not os.path.exists("scanbox/output"):
    os.mkdir("scanbox/output")

if not os.path.exists("scanbox/results"):
    os.mkdir("scanbox/results")

eel.start('index.html', options=my_options)

