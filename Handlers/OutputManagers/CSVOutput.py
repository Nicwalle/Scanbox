from datetime import datetime

import requests

from DataClasses.ScanResult import ScanResult
from Singletons import Inputs, Ports
from Utils.Utils import Utils


class CSVOutput:
    """
    Manages the CSV output of the listening ports
    """

    def __init__(self):
        self.ports = Ports.ports
        now = datetime.now()

        self.output_filename = "scanbox/output/scanbox-analysis-{year}-{month}-{day}-{hours}-{minutes}-{seconds}.csv" \
            .format(
                year=now.year,
                month='%02d' % now.month,
                day='%02d' % now.day,
                hours='%02d' % now.hour,
                minutes='%02d' % now.minute,
                seconds='%02d' % now.second
            )

        self.file_descriptor = open(self.output_filename, "w+")
        self.file_descriptor.write("DATE,TIME,IP,NAME,#OPEN-PORTS")
        for port in self.ports:
            self.file_descriptor.write(",{port},EXPECTED-{port}".format(
                port=("TCP" if int(port) != 53 and int(port) != 161 else "UDP") + "/" + str(port)
            ))
        self.file_descriptor.write("\n")
        self.file_descriptor.close()
        self.lines = []

    def write(self, scan_result: ScanResult or str):
        """
        Adds scan_result to the results list
        :param scan_result:
        """
        if type(scan_result) == str:
            try:
                self.file_descriptor = open(self.output_filename, "a")
                self.file_descriptor.write("SCANNED,FROM,{ip}".format(
                    ip=requests.get('https://api.ipify.org').text
                ))
                self.file_descriptor.close()
            except (IOError, ConnectionError):
                pass
        else:
            now = datetime.now()
            results = scan_result.get_ports_results()
            string = "{year}-{month}-{day},{hours}:{minutes}:{seconds},{ip},{url},{amount}".format(
                year=now.year,
                month='%02d' % now.month,
                day='%02d' % now.day,
                hours='%02d' % now.hour,
                minutes='%02d' % now.minute,
                seconds='%02d' % now.second,
                ip=scan_result.entry.get_ip(),
                url=scan_result.entry.get_name() + ".tango.lu" if scan_result.entry_type == "DNS" else "NONE",
                amount=self.get_amount_responding(results)
            )

            for port in self.ports:
                time = results.get(port, "NOT-SCANNED")
                if time == -1:
                    if scan_result.entry_type == "DNS":
                        time = "TIMEOUT({timeout}s)".format(timeout=Inputs.inputs.get("timeout"))
                    elif scan_result.entry_type == "IP":
                        time = "TIMEOUT({timeout}s)".format(timeout=scan_result.get_entry().get_timeout(port=port))

                expected = "-"
                if scan_result.entry_type == "IP":
                    expected = scan_result.get_entry().get_expected_value(port=port)

                string += ",{time},{expected}".format(time=time, expected=expected)
            string += "\n"

            self.file_descriptor = open(self.output_filename, "a")
            self.file_descriptor.write(string)
            self.file_descriptor.close()

    @staticmethod
    def get_amount_responding(ports):
        i = 0
        for port in ports:
            if Utils.is_positive_result(ports.get(port)):
                i += 1
        return i
