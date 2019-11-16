import json
import os
from typing import List

import eel

from DataClasses.IPEntry import IPEntry
from DataClasses.ScanResult import ScanResult
from Handlers.AlertsManager import AlertsManager
from Handlers.Scanners.DNSFileHandler import DNSFileHandler
from Handlers.Scanners.IPScanner import IPScanner
from Handlers.Scanners.IPsFileHandler import IPsFileHandler
from Handlers.OutputManagers.OutputDispatcher import OutputDispatcher
from Handlers.Scanners.RecordScanner import RecordScanner
from Singletons import Inputs, Ports


class ScanBox:
    dns_file: str
    ports: List[int]

    def __init__(self):
        self.dns_file = Inputs.inputs.get("dns-input-file", "")
        self.output_dispatcher = OutputDispatcher()
        self.scan_results = {}

    def start(self):

        dns_file_handler = DNSFileHandler(filename=self.dns_file, output_dispatcher=self.output_dispatcher)
        dns_entries = dns_file_handler.get_entries()
        ips_file_handler = IPsFileHandler(self.output_dispatcher)
        ip_entries = ips_file_handler.parse_file()

        Ports.ports = self.get_all_ports(ip_entries)

        if Inputs.inputs["UI"]:
            eel.updateTotalIPs(len(dns_entries) + len(ip_entries))

        self.scan_dns(dns_entries)
        self.scan_ips(ip_entries)
        self.output_dispatcher.write(where="CSV", what="terminating")
        self.output_dispatcher.get_json_output().persist()

        previous_results = self.get_most_recent_results()
        alerts_manager = AlertsManager(
            previous_results=previous_results,
            current_results=self.output_dispatcher.get_json_output().get_results(),
            output_dispatcher=self.output_dispatcher
        )
        alerts_manager.check_for_alerts()
        alerts_manager.print_report()
        alerts_manager.send_report()

        self.terminate()

    def scan_dns(self, dns_entries):
        scanned_urls = []
        name_to_ip = {}

        for entry in dns_entries:
            if entry.get_type() == "A":
                name_to_ip[entry.get_name()] = entry.get_data()

        for entry in dns_entries:
            if Inputs.inputs.get("UI", False) and eel.isStopped()():
                break

            record_scanner = RecordScanner(
                entry=entry,
                output_dispatcher=self.output_dispatcher,
                scanned_urls=scanned_urls,
                scan_results=self.scan_results,
                name_to_ip=name_to_ip
            )
            record_scanner.scan()
            if Inputs.inputs.get("UI", False):
                eel.incrementScanned()

    def scan_ips(self, ip_entries):
        for entry in ip_entries.values():
            if Inputs.inputs.get("UI", False) and eel.isStopped()():
                break

            ip_scanner = IPScanner(
                entry=entry,
                output_dispatcher=self.output_dispatcher,
                scan_results=self.scan_results
            )
            ip_scanner.scan()
            if Inputs.inputs.get("UI", False):
                eel.incrementScanned()

    @staticmethod
    def terminate():
        if Inputs.inputs.get("UI", False):
            eel.terminate()

    @staticmethod
    def get_most_recent_results():
        all_results = [file.name for file in os.scandir("scanbox/results/")]
        all_results.sort(reverse=True)
        filename = all_results[1] if len(all_results) > 1 else None

        if filename is None:
            return None

        try:
            fd = open("scanbox/results/" + filename, "r")
            previous_results_dict = json.load(fd)
            fd.close()

            previous_results = {}
            for key, value in previous_results_dict.items():
                previous_results[key] = ScanResult.from_dict(value)
            return previous_results
        except IOError as err:
            return err

    @staticmethod
    def get_all_ports(ip_entries) -> List[int]:
        ports = Inputs.inputs.get("ports", []).copy()

        entry: IPEntry
        for entry in ip_entries.values():
            for port in entry.get_ports():
                if int(port) not in ports:
                    ports.append(int(port))

        return ports
