from DataClasses.IPEntry import IPEntry
from DataClasses.ScanResult import ScanResult
from Handlers.Scanners.Scanner import Scanner


class IPScanner(Scanner):
    """
    Scans an IPEntry coming form the IPs input. (not the DNS)
    """
    def __init__(self, entry: IPEntry, output_dispatcher, scan_results):
        super().__init__(
            entry=entry,
            output_dispatcher=output_dispatcher,
            scan_results=scan_results,
            scan_result=ScanResult(entry)
        )

    def scan(self):
        self.scan_ip()
        self.output_results()

        self.output_dispatcher.write(where="JSON", what=self.scan_result)
