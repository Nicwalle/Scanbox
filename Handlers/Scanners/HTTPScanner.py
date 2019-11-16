import re
import requests

from Singletons import Inputs
from Utils.Utils import Utils
from DataClasses.ScanMessage import ScanMessage


class HTTPScanner:
    """
    Scans a domain name (Layer 7) using HTTP/HTTPS to see if its applicative response.
    If asked for, scans the content of the responded web page to find other urls to scan.
    """

    def __init__(self,
                 subdomain,
                 domain="tango.lu",
                 scanned_urls=None,
                 port=80,
                 scan_result=None,
                 ip="",
                 output_dispatcher=None
                 ):
        """

        :type scan_result: ScanResult
        """
        self.scan_result = scan_result
        self.output_dispatcher = output_dispatcher
        self.ip = ip
        if scanned_urls is None:
            scanned_urls = []
        self.scanned_urls = scanned_urls
        self.port = port
        if port == 80:
            protocol = "http"
        else:
            protocol = "https"
        if len(subdomain) > 8 and subdomain[-8:-1] == "tango.lu":
            self.start_url = protocol + "://" + subdomain
        else:
            self.start_url = protocol + "://" + subdomain + "." + domain

    def scan(self):
        regex = r"href=\"((https?:\/\/[\w\-]+\.(proximus\.lu|tango\.lu|telindus\.lu))?(\/[\w.\/\-\#?=%&]+)?)\""
        # href=\"((https?://[\w\-]+\.(proximus\.lu|tango.lu))?/[\w.\/\-\#?=%&]+)\"
        try:
            response = requests.get(self.start_url, timeout=Inputs.inputs.get("timeout", 2))
            self.scanned_urls.append(self.start_url)
            if response.status_code == 200:
                reg = r"(https?:\/\/[\w.-]+)"

                mat = re.search(reg, response.headers.get("Link", self.start_url))

                if mat:
                    self.start_url = mat.group(1)

                matches = re.finditer(regex, response.content.decode(), re.MULTILINE | re.DOTALL)

                for matchNum, match in enumerate(matches, start=1):
                    if len(match.group(1)) > 1 and match.group(1)[0:2] != "//":
                        if match.group(1)[0] == "/":
                            next_url = self.start_url + match.group(1)
                        else:
                            next_url = match.group(1)

                        if next_url not in self.scanned_urls:
                            self.scanned_urls.append(next_url)
                            try:
                                next_response = requests.get(next_url, timeout=Inputs.inputs.get("timeout", 2))
                                if int(next_response.status_code) == 404 or int(next_response.status_code) >= 500:
                                    scan_message = ScanMessage(
                                        title=f"{Utils.make_link(next_url, True)} responded with status code "
                                              f"{next_response.status_code}",
                                        message=f"{Utils.make_link(next_url)} reached via {self.start_url} on {self.ip}" 
                                                f":{self.port} responded with status code {next_response.status_code}"
                                    )
                                    self.output_dispatcher.write(where="MSG", what=scan_message)
                                    self.scan_result.add_message(scan_message)
                            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as err:
                                scan_message = ScanMessage(
                                    title=f"{Utils.make_link(next_url, True)} was unreachable",
                                    message=f"{Utils.make_link(next_url)} on page {self.start_url} on {self.ip}:" 
                                            f"{self.port} was unreachable: {err}"
                                )
                                self.output_dispatcher.write(where="MSG", what=scan_message)
                                self.scan_result.add_message(scan_message)

            elif int(response.status_code) == 404 or int(response.status_code) >= 500:
                scan_message = ScanMessage(
                    title=f"{Utils.make_link(self.start_url, True)} responded with status code {response.status_code}",
                    message=f"{Utils.make_link(self.start_url)} on {self.ip}:{self.port} responded with status code "
                            f"{response.status_code} "
                )
                self.output_dispatcher.write(where="MSG", what=scan_message)
                self.scan_result.add_message(scan_message)

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as err:
            scan_message = ScanMessage(
                title=f"{Utils.make_link(self.start_url, True)} was unreachable on port {self.port}",
                message=f"{Utils.make_link(self.start_url)} on {self.ip}:{self.port} did not respond but port "
                        f"{self.port} is listening.<br>Error message:<br>{err}"
            )
            self.output_dispatcher.write(where="MSG", what=scan_message)
            self.scan_result.add_message(scan_message)
