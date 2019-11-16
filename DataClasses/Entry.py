from typing import List

from Singletons import Inputs


class Entry:
    """
    Represents a general Entry (acts like an interface in other programming languages. Easier for type hinting)
    """
    def get_ip(self) -> str or None:
        return None

    def get_ports(self) -> List[int]:
        return []

    def to_dict(self) -> dict:
        return {
            "ip": self.get_ip(),
            "ports": self.get_ports()
        }

    def get_timeout(self, port=None):
        return Inputs.inputs.get("timeout", 2)
