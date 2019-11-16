import json
from datetime import datetime

from DataClasses.DNSEntry import DNSEntry
from DataClasses.IPEntry import IPEntry
from DataClasses.ScanResult import ScanResult


class JSONOutput:
    """
    Manages the output of the ScanResults to the JSON file for persitency of the results
    """

    def __init__(self):
        now = datetime.now()

        self.storage = "scanbox/results/{year}{month}{day}{hours}{minutes}{seconds}.json" \
            .format(
                year='%04d' % now.year,
                month='%02d' % now.month,
                day='%02d' % now.day,
                hours='%02d' % now.hour,
                minutes='%02d' % now.minute,
                seconds='%02d' % now.second
            )

        self.dictionary = {}
        self.results = {}
        self.file_descriptor = open(self.storage, "w+")
        self.file_descriptor.write("{}")
        self.file_descriptor.close()

    def write(self, what):
        if isinstance(what, ScanResult) and isinstance(what.get_entry(), DNSEntry):
            self.results[what.get_entry().get_name() + what.get_entry().get_type()] = what
            self.dictionary[what.get_entry().get_name() + what.get_entry().get_type()] = what.to_dict()
        elif isinstance(what, ScanResult) and isinstance(what.get_entry(), IPEntry):
            self.results[what.get_entry().get_ip()] = what
            self.dictionary[what.get_entry().get_ip()] = what.to_dict()

    def persist(self):
        self.file_descriptor = open(self.storage, "w")
        self.file_descriptor.write(json.dumps(self.dictionary))
        self.file_descriptor.close()

    def get_results(self):
        return self.results
