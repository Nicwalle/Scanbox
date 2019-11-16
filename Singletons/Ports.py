"""
File and thus variable accessible to every other file of the project and initialised at the beginning of the program.
Contains all the ports defined for a DNS scan. To those ports will be appended the ports to be scanned on a "per-ip"
address
"""
from Singletons import Inputs

ports = Inputs.inputs.get("ports", [])
