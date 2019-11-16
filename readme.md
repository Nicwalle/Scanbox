# Scanbox
The Scanbox is a program which as for aim to scan ports on IP addresses to find out which are accessible or not from a certain computer.

It has been developped using python and the [`eel`](https://github.com/ChrisKnott/Eel) library to interact with a web-based user interface.

The program is delivered in 2 versions:
* Executable (recommended, ready to use)
* Python

## Requirements
In order to install the Scanbox, you will need the following:
* Google chrome (for the UI)

If you don't aim to use the executable:
* Python 3.* (with `pip`)

## Installation (if aimed to be used with python)
You might have to create a virtual environment and install some packages in it. 

**SKIP THIS PART IF YOU ALREADY HAVE THE `venv` DIRECTORY OR IF YOU ARE WILLING TO RUN THE EXECUTABLE VERSION**

To do so: 
1. Create a virtual environment called `venv` in the root folder of the project by running the command `python -m venv ./venv`.
2. Move to the virtual environment. (Linux: `source venv/bin/activate` and Windows: `.\venv\Scripts\activate`)
3. Then you can install the following packages
    * EEL: for the UI (`pip install eel`)
    * Requests: to perform http(s) requests (`pip install requests`)
    * PySNMP: to test the SNMP port 161 (`pip install pysnmp`)

You are done...

## Running the program
There are 2 ways to perform a scan.
1. Using the GUI
2. Using command line and input files
   *Note: the UI allows you to automatically fill in those files and should be used before performing a command line analysis*

### Graphical User Interface
To launch the GUI, run the `scanbox_GUI.exe` executable or, if you wish to use python, run: 
```
python scanbox_GUI.py
```
This will start a server on `localhost:8080` and open a chrome window at this page.

On this page, you can manage the different input settings which will be used when clicking `Scan` on the GUI or when launching the Scanbox in command line.

### Command line
To run a scan in command line, you must have saved the inputs using the GUI or created the appropriate files.

Then, launch the `scanbox_NOGUI.exe` executable or run the following python command if you wish to use it with python: 
```
python scanbox_NOGUI.py
```

Files needed to perform a scan:
* **Mandatory:** `scanbox/inputs/inputs.json`.
  
  The `inputs.json` file contains all the information to execute the scan and alert if needed. Here is its structure:
  ```
    {
        "ports": [
            // List of ports to scan on each entry of the  specified (if specified) dns-input-file
        ],
        "check-links": true,    // Check the links on the domains reachable on port 80 or 443 
        "timeout": 2,           // Response timeout for the DNS entries
        "dns-input-file": "C:/PATH/TO/DNS/FILE/dnsfile.txt",
        "UI": false,            // Scan launched from the UI/Command line
        "alert-triggers": {
            "new-entry": false,
            "changed-dns-record": false,
            "different-open-ports": true,
            "new-warnings-only": true,
            "all-warnings": false,
            "unexpected-state": true
        },
        "email-address": "contact@server.com",  // Email to send the report to
        "mail-server": "mail.server.com",       // Mailserver to use
        "mail-server-port": "25",               // SMTP port
        "mail-server-auth":"auth@server.com",
        "mail-server-pass":"password"
    }
  ```
  If the `"dns-input-file"` and the `"ports"` are defined and not empty, you need to have a well formatted and accessible for reading DNS file at the location specified.
* `scanbox/inputs/ips.txt`. If you wish to scan specific IP addresses, those must be stored in this file (if empty or not existing, this part will be ignored). Each line must respect that format: `IP-RANGES/PORT-RANGES/TIMEOUT/EXPECTED-PORT-STATE`.
  * IP ranges must respect the IPv4 format and can contain numbers, periods, dashes and semicolons. Dashes determine a range of numbers in a class and semicolons determine multiple IPs. Here are some examples:
    * 192.168.1;2.1-255 will scan all IPs starting by 192.168.1.* and 192.168.2.*
    * 192.168.1.1-10;90-100 will scan the IPs starting by 192.168.1. and going form 1 to 10 and 90 to 100
  * Port ranges can follow the same pattern as IP classes:
    * 80;443 will scan port 80 and 443
    * 1000-1099 will scan ports from 1000 to 1099
    * 80;443;20-25 will scan ports 80, 443 and from 20 to 25
  * Timeout is defined in seconds
  * Expected port state can be OPEN, CLOSE or NONE if there is no expected response.
