import re
from typing import List
from DataClasses.DNSEntry import DNSEntry
from Handlers.Scanners.HTTPScanner import HTTPScanner

from Handlers.OutputManagers.OutputDispatcher import OutputDispatcher
from DataClasses.ScanMessage import ScanMessage
from DataClasses.ScanResult import ScanResult
from Handlers.Scanners.Scanner import Scanner
from Singletons import Inputs


class RecordScanner(Scanner):
    """
    Scans a DNSEntry coming from a DNS input file (not the IPs input)
    """
    ports: List[int]

    def __init__(self, entry: DNSEntry, output_dispatcher: OutputDispatcher, scanned_urls=None, scan_results=None,
                 name_to_ip=None):
        super().__init__(entry, output_dispatcher, scan_results, ScanResult(entry))

        if name_to_ip is None:
            name_to_ip = {}

        if scanned_urls is None:
            scanned_urls = []

        self.name_to_ip = name_to_ip
        self.scanned_urls = scanned_urls

    def scan(self):

        if self.entry.get_type() == "A":
            self.scan_ip()
            self.scan_http()
            self.output_results()
        elif self.entry.get_type() == "MX":
            regex = r"([\w\.\-]+)\.tango\.lu."
            matches = re.search(regex, self.entry.get_data())

            if matches is not None and not self.is_cname_in_dns(matches.group(1)):
                scan_message = ScanMessage(
                    title=f"MX record &nbsp; <span class='inline-code'>{self.entry.get_name()}</span> &nbsp; has no "
                          f"corresponding IP address",
                    message=f"No matching A record found for rule <span class='inline-code'>{self.entry.get_name()}"
                            f"&nbsp; IN &nbsp; MX {self.entry.get_data()}</span> "
                )
                self.scan_result.add_message(scan_message)

                self.output_dispatcher.write(where="MSG", what=scan_message)

        elif self.entry.get_type() == "CNAME":
            regex = r"([\w\.\-]+)\.tango\.lu."
            matches = re.search(regex, self.entry.get_data())

            if matches is not None and not self.is_cname_in_dns(matches.group(1)):
                scan_message = ScanMessage(
                    title=f"CNAME alias &nbsp; <span class='inline-code'>{self.entry.get_name()}</span> &nbsp; has no "
                          f"corresponding IP address",
                    message=f"No matching A record found for rule <span class='inline-code'>{self.entry.get_name()}"
                            f"&nbsp; IN &nbsp; CNAME {self.entry.get_ip()}</span> "
                )
                self.scan_result.add_message(scan_message)

                self.output_dispatcher.write(where="MSG", what=scan_message)

        self.output_dispatcher.write(where="JSON", what=self.scan_result)

    def scan_http(self):
        for port in [80, 443]:
            if port not in self.entry.get_ports():
                continue
            if Inputs.inputs.get("check-links") and self.scan_result.get_port_result(port) != -1 and \
                    (port == 80 or port == 443) and self.entry.get_name()[0] != "*" and self.entry.get_name()[0] != "@":
                http_scanner = HTTPScanner(
                    subdomain=self.entry.get_name(),
                    scanned_urls=self.scanned_urls,
                    port=port,
                    scan_result=self.scan_result,
                    ip=self.entry.get_ip(),
                    output_dispatcher=self.output_dispatcher
                )
                http_scanner.scan()

    def is_cname_in_dns(self, cname: str):
        if cname not in self.name_to_ip:
            data_list = cname.split(".")
            while len(data_list) > 1:
                data_list = data_list[1:]
                if "*." + ".".join(data_list) in self.name_to_ip:
                    return True
            return False
        else:
            return True
