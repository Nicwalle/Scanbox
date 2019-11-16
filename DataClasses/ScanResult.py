import json
from datetime import datetime
from typing import List, Any
from DataClasses.DNSEntry import DNSEntry
from DataClasses.Entry import Entry
from DataClasses.IPEntry import IPEntry
from DataClasses.ScanMessage import ScanMessage


class ScanResult:
    """
    Represents the result of the scan of a specific Entry. Its purpose is to keep track of the previous results in a
    formatted way in order to compare the different results automatically. Thos results will be stored in a JSON file in the
    results folder
    """

    messages: List[ScanMessage]

    def __init__(self, entry: Entry):
        self.entry = entry
        now = datetime.now()
        self.time = "{year}-{month}-{day} {hours}:{minutes}:{seconds}".format(
            year=now.year,
            month='%02d' % now.month,
            day='%02d' % now.day,
            hours='%02d' % now.hour,
            minutes='%02d' % now.minute,
            seconds='%02d' % now.second
        )
        self.ports = {}
        self.messages = []
        if isinstance(entry, DNSEntry):
            self.entry_type = "DNS"
        elif isinstance(entry, IPEntry):
            self.entry_type = "IP"

    def get_entry(self):
        return self.entry

    def add_port_result(self, port: int, result: Any):
        self.ports[port] = result

    def get_port_result(self, port: int) -> Any:
        return self.ports.get(port, None)

    def get_ports_results(self) -> dict:
        return self.ports

    def add_message(self, message: ScanMessage):
        self.messages.append(message)

    def get_messages(self) -> List[ScanMessage]:
        return self.messages

    def get_messages_dict(self) -> List[dict]:
        result = []
        for message in self.get_messages():
            result.append(message.to_dict())
        return result

    def get_time(self) -> str:
        return self.time

    def to_dict(self):
        return {
            "record": self.get_entry().to_dict(),
            "ports": self.get_ports_results(),
            "messages": self.get_messages_dict(),
            "time": self.get_time(),
            "type": self.entry_type
        }

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        json_structure = self.to_dict()
        return json.dumps(json_structure)

    @staticmethod
    def from_dict(dictionary: dict):
        if dictionary.get("type") == "DNS":
            scan_result = ScanResult(DNSEntry.from_dict(dictionary.get("record")))
        elif dictionary.get("type") == "IP":
            scan_result = ScanResult(IPEntry.from_dict(dictionary.get("record")))
        else:
            return None
        scan_result.ports = {}
        for str_port, value in dictionary.get("ports", {}).items():
            scan_result.ports[int(str_port)] = value
        scan_result.messages = []
        for message in dictionary.get("messages", []):
            scan_result.add_message(ScanMessage.from_dict(message))
        scan_result.time = dictionary.get("time")
        return scan_result
