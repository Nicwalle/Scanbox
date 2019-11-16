import os
import socket
import subprocess
import threading
import time

from pysnmp.hlapi import getCmd, SnmpEngine, CommunityData, UdpTransportTarget, ContextData, ObjectType, ObjectIdentity

from DataClasses import ScanResult
from DataClasses.Entry import Entry
from Singletons import Inputs


class Scanner:
    """
    General Scanner used by the RecordScanner and the IPScanner.
    If the port to scan is not 53 or 161, tries to open a TCP socket with the server on the specified port. If the
    server does not respond before the timeout, the port is considered as being closed
    """
    def __init__(self,
                 entry: Entry,
                 output_dispatcher,
                 scan_results=None,
                 scan_result: ScanResult = None
                 ):
        self.scan_results = scan_results
        self.output_dispatcher = output_dispatcher
        self.entry: Entry = entry
        self.scan_result: ScanResult = scan_result

    def scan_ip(self):
        threads = {}
        for port in self.entry.get_ports():
            thread = threading.Thread(target=self.thread_port_scan, args=(port,))
            threads[port] = thread
            thread.start()

        for port, thread in threads.items():
            thread.join()

    def thread_port_scan(self, port):
        if port == 53:
            if self.entry.get_ip() in self.scan_results and self.scan_results[self.entry.get_ip()].get_port_result(port) is not None:
                port_result = self.scan_results[self.entry.get_ip()]
                self.scan_result.add_port_result(port, port_result.get_port_result(port))
            else:
                self.scan_result.add_port_result(port, self.dns_connect())
        elif port == 161:
            if self.entry.get_ip() in self.scan_results and self.scan_results[self.entry.get_ip()].get_port_result(port) is not None:
                port_result = self.scan_results[self.entry.get_ip()]
                self.scan_result.add_port_result(port, port_result.get_port_result(port))
            else:
                self.scan_result.add_port_result(port, self.snmp_connect())
        else:
            if self.entry.get_ip() in self.scan_results and self.scan_results[self.entry.get_ip()].get_port_result(port) is not None:
                port_result = self.scan_results[self.entry.get_ip()]
                result = port_result.get_port_result(port)
                self.scan_result.add_port_result(port, result)
            else:
                result = self.tcp_connect(port)
                self.scan_result.add_port_result(port, result)

    def output_results(self):
        self.output_dispatcher.write(where="PORTS", what=self.scan_result)
        self.output_dispatcher.write(where="CSV", what=self.scan_result)
        self.scan_results[self.scan_result.get_entry().get_ip()] = self.scan_result

    def tcp_connect(self, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(Inputs.inputs.get("timeout", Inputs.inputs.get("timeout")))

        start = time.perf_counter()
        result = sock.connect_ex((self.entry.get_ip(), port))
        delay = time.perf_counter() - start
        sock.close()
        if result == 0:
            return delay
        else:
            return -1

    def dns_connect(self):
        try:
            result = subprocess.check_output(
                                    "nslookup tango.lu " + self.entry.get_ip(),
                                    stderr=open(os.devnull, 'w'),
                                    timeout=self.entry.get_timeout(53) + 1
                                ).decode()
            if "request timed out" in result:
                return -1
            else:
                return "OK"
        except subprocess.TimeoutExpired:
            return -1

    def snmp_connect(self):
        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData('public'),
                   UdpTransportTarget((self.entry.get_ip(), 161), timeout=self.entry.get_timeout(161), retries=1),
                   ContextData(),
                   ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0')),
                   ObjectType(ObjectIdentity('1.3.6.1.2.1.1.6.0')))
        )
        if error_indication:
            result = -1
        elif error_status:
            result = -1
        else:
            result = "OK"
        return result
