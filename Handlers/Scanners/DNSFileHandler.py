from DataClasses.DNSEntry import DNSEntry
import re

from DataClasses.UIErrorMessage import UIErrorMessage
from Handlers.OutputManagers.OutputDispatcher import OutputDispatcher
from Singletons import Inputs


class DNSFileHandler:
    """
    Scans a DNS structured file (examples given below) and generates a list of DNS entries which will then be scanned
    """

    filename: str
    dns_entries = []

    def __init__(self, filename: str, output_dispatcher: OutputDispatcher):
        self.output_dispatcher = output_dispatcher
        self.filename = filename

    def get_entries(self):
        if len(self.filename) == 0 or len(Inputs.inputs.get("ports", [])) == 0:
            return []
        self.scan_file(self.filename)
        return self.dns_entries

    def scan_file(self, filename: str):
        self.dns_entries = []
        try:
            file = open(filename, "r")
            i = 1
            for line in file:
                entry = self.scan_line(line, i)
                if entry is not None:
                    self.dns_entries.append(entry)
                i += 1

            file.close()

        except IOError:
            self.output_dispatcher.write(where="ERR", what=UIErrorMessage(
                type="file-error",
                message="File " + filename + " does not exist"
            ))

    @staticmethod
    def scan_line(line: str, line_number: int):
        if line[0] == ";":
            return None

        patterns = {
            # EXAMPLES :    security-test     3600      IN      A       212.66.75.60
            #               www                         IN      A       212.66.75.60
            "A": r"(\S+)\s+([0-9]+\s+)?(\S+)\s+(A)\s+([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})",

            # EXAMPLES :    webbilling2       3600      IN      CNAME   facture.tango.lu.
            #               mojito-security2-prod       IN      CNAME   security.tango.lu.
            "CNAME": r"(\S+)\s+([0-9]+\s+)?(\S+)\s+(CNAME)\s+(\S+)",

            # EXAMPLES :    teamitup           IN      MX      10        tangomail.tango.lu.
            #               pro                IN      MX      10        tangomail.tango.lu.
            "MX": r"(\S+)\s+([0-9]+\s+)?(\S+)\s+(MX\s+[0-9]+)\s+(\S+)"
        }

        for record_type, pattern in patterns.items():
            match = re.search(pattern, line)
            if match:
                entry = DNSEntry()
                entry.set_name(match.group(1))
                if match.group(2) is not None:
                    entry.set_ttl(int(match.group(2)))
                entry.set_class(match.group(3))
                entry.set_type(record_type)
                entry.set_data(match.group(5))
                entry.set_line(line_number)

                return entry
        return None
