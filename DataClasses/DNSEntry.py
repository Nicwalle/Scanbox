from typing import List

from DataClasses.Entry import Entry
from Singletons import Inputs


class DNSEntry(Entry):
    """
    Represents a DNS Entry from the DNS input file
    """
    __line: int
    __ttl: int
    __name: str
    __record_class: str
    __record_type: str
    __data: str

    def __init__(self):
        self.__name = ""
        self.__record_class = ""
        self.__record_type = ""
        self.__data = ""
        self.__ttl = 0

    def set_name(self, name: str):
        self.__name = name

    def get_name(self):
        return self.__name

    def set_class(self, record_class: str):
        self.__record_class = record_class

    def get_class(self):
        return self.__record_class

    def set_type(self, record_type: str):
        self.__record_type = record_type

    def get_type(self):
        return self.__record_type

    def set_data(self, data: str):
        self.__data = data

    def get_data(self):
        return self.__data

    def set_ttl(self, ttl: int):
        self.__ttl = ttl

    def get_ttl(self):
        return self.__ttl

    def get_ports(self) -> List[int]:
        return [int(port) for port in Inputs.inputs.get("ports")]

    def get_ip(self) -> str or None:
        if self.get_type() == "A":
            return self.get_data()
        else:
            return None

    def to_dict(self):
        return {
            "name": self.get_name(),
            "record_class": self.get_class(),
            "record_type": self.get_type(),
            "ttl": self.get_ttl(),
            "data": self.get_data(),
            "line": self.get_line()
        }

    def set_line(self, line_number):
        self.__line = line_number

    def get_line(self):
        return self.__line

    def __str__(self):
        return self.get_name() + " " + self.get_data()

    @staticmethod
    def from_dict(dictionary: dict):
        dns_entry = DNSEntry()
        dns_entry.set_name(dictionary.get("name"))
        dns_entry.set_class(dictionary.get("record_class", "IN"))
        dns_entry.set_type(dictionary.get("record_type", "A"))
        dns_entry.set_ttl(dictionary.get("ttl", 0))
        dns_entry.set_data(dictionary.get("data"))
        dns_entry.set_line(dictionary.get("line"))
        return dns_entry

    def __eq__(self, other):
        """
        :type other: DNSEntry
        """
        return self.get_name() == other.get_name() and \
               self.get_class() == other.get_class() and \
               self.get_type() == other.get_type() and \
               self.get_data() == other.get_data()
