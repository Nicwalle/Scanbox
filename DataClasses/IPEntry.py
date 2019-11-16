import json
from typing import List

from DataClasses.Entry import Entry


class IPEntry(Entry):
    """
    Represents an IP Entry from the ips input
    """
    def __init__(self, ip: str, ports=None, responses=None, timeouts=None):
        if timeouts is None:
            timeouts = {}
        if responses is None:
            responses = {}
        if ports is None:
            ports = {}
        self.ip = ip
        self.ports = ports
        self.expected_responses = responses
        self.timeouts = timeouts

    def add_ports(self, ports, responses, timeouts):
        for port in ports:
            if port not in self.ports:
                self.ports.append(port)
                self.expected_responses[str(port)] = responses[str(port)]
                self.timeouts[str(port)] = timeouts[str(port)]

    def get_ports(self) -> List[int]:
        return self.ports

    def get_ip(self):
        return self.ip

    def get_timeout(self, port=None):
        return self.timeouts.get(str(port), "?")

    def get_expected_value(self, port):
        return self.expected_responses.get(str(port), "-")

    def __str__(self):
        return json.dumps(self.to_dict())

    def __repr__(self):
        return self.__str__()

    def to_dict(self):
        return {
            "ip": self.get_ip(),
            "ports": self.get_ports(),
            "responses": self.expected_responses,
            "timeouts": self.timeouts
        }

    def __eq__(self, other):
        """
        :type other: IPEntry
        """
        return self.get_ip() == other.get_ip()

    @staticmethod
    def from_dict(dictionary: dict):
        ip_entry = IPEntry(
            dictionary.get("ip"),
            dictionary.get("ports"),
            dictionary.get("responses"),
            dictionary.get("timeouts")
        )
        return ip_entry
