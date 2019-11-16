import json
import re
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from DataClasses.ScanResult import ScanResult
from Handlers.OutputManagers.OutputDispatcher import OutputDispatcher
from Singletons import Inputs
from Utils.Utils import Utils


class AlertsManager:
    """
    Manages the alerts. Sends an email with the report if needed (depending on the specified alert triggers)
    """
    def __init__(self, previous_results=None, current_results=None, output_dispatcher: OutputDispatcher = None):
        self.csv_file = output_dispatcher.get_csv_output().output_filename
        self.current_results = current_results
        self.previous_results = previous_results
        self.trigger_alert = False
        self.report = {
            "new-entry": [],
            "changed-dns-records": [],
            "different-open-ports": [],
            "unexpected-port-responses": [],
            "warnings": []
        }
        self.output_dispatcher = output_dispatcher

    def check_for_alerts(self):
        current_result: ScanResult
        for key, current_result in self.current_results.items():
            if self.previous_results is not None:
                self.check_changed_dns_record(key=key, current_result=current_result)
                self.check_results_since_previous_scan(key=key, current_result=current_result)

            self.check_new_entry(key=key, current_result=current_result)
            self.check_expected_port_responses(current_result=current_result)
            self.check_messages(key=key, current_result=current_result)

    def check_new_entry(self, key: str, current_result: ScanResult):
        if self.previous_results is None:
            previous = {}
        else:
            previous = self.previous_results
        if (current_result.entry_type == "DNS") and (key not in previous):
            # New record since previous scan
            if Inputs.inputs.get("alert-triggers", {}).get("new-entry", True):
                self.trigger_alert = True

            self.report.get("new-entry").append(
                "[{name}\t{rclass}\t{type}\t{data}] at line [{line}]".format(
                    name=current_result.get_entry().get_name(),
                    rclass=current_result.get_entry().get_class(),
                    type=current_result.get_entry().get_type(),
                    data=current_result.get_entry().get_data(),
                    line=current_result.get_entry().get_line()
                ))
        elif (current_result.entry_type == "IP") and (key not in previous):
            if Inputs.inputs.get("alert-triggers", {}).get("new-entry", True):
                self.trigger_alert = True

            self.report.get("new-entry").append(
                "IP [{ip}] has been added to the scan list".format(
                    ip=current_result.get_entry().get_ip()
                ))

    def check_changed_dns_record(self, key: str, current_result: ScanResult):
        # Changed record since previous scan
        previous_result = self.previous_results.get(key, None)
        if (current_result.entry_type == "DNS") and \
                previous_result is not None and \
                current_result.get_entry() != previous_result.get_entry():

            if Inputs.inputs.get("alert-triggers", {}).get("changed-dns-record", True):
                self.trigger_alert = True

            self.report.get("changed-dns-records") \
                .append("[{name}] record was [{name}\t{rclass}\t{type}\t{old_data}] is now [{name}\t {rclass}\t"
                        "{type}\t{current_data}] at line {line}".format(
                            name=current_result.get_entry().get_name(),
                            rclass=current_result.get_entry().get_class(),
                            type=current_result.get_entry().get_type(),
                            old_data=previous_result.get_entry().get_data(),
                            current_data=current_result.get_entry().get_data(),
                            line=current_result.get_entry().get_line()
                        ))

    def check_expected_port_responses(self, current_result):
        if current_result.entry_type == "IP":
            for port, response in current_result.get_ports_results().items():
                expected_response = current_result.get_entry().get_expected_value(port)
                if not self.response_match_expected(response, expected_response):
                    if Inputs.inputs.get("alert-triggers", {}).get("unexpected-state", True):
                        self.trigger_alert = True

                    if Utils.is_positive_result(response):
                        self.report.get("unexpected-port-responses") \
                            .append(f"IP [{current_result.get_entry().get_ip()}] responded in [{response}s] "
                                    f"expected [{expected_response}] on port [{port}]")
                    else:
                        self.report.get("unexpected-port-responses") \
                            .append(f"IP [{current_result.get_entry().get_ip()}] did not responded on port [{port}] "
                                    f"expected [{expected_response}]. Timeout: "
                                    f"[{current_result.get_entry().get_timeout(port)}s]")

    def check_results_since_previous_scan(self, key, current_result):
        previous_result = self.previous_results.get(key, None)

        # Different open/closed ports
        if previous_result is not None:
            different_ports_results = self.get_different_ports(
                previous=previous_result.get_ports_results(),
                current=current_result.get_ports_results()
            )

            for port in different_ports_results:
                if current_result.entry_type == "DNS" or current_result.get_entry().get_expected_value(port) == "NONE":
                    if Inputs.inputs.get("alert-triggers", {}).get("different-open-ports", True):
                        self.trigger_alert = True

                    message = "IP [{ip}]: port [{port}] was [{previous_status}] is now [{new_status}]".format(
                        ip=current_result.get_entry().get_ip(),
                        port=port,
                        previous_status=previous_result.get_port_result(port),
                        new_status=current_result.get_port_result(port)
                    )
                    if message not in self.report.get("different-open-ports", []):
                        self.report.get("different-open-ports", []).append(message)

    def check_messages(self, key, current_result):
        new_messages = []
        previous_result = None
        if self.previous_results is not None:
            previous_result = self.previous_results.get(key, None)

        if self.previous_results is None or \
                previous_result is None or \
                Inputs.inputs.get("alert-triggers", {}).get("all-warnings", False):
            new_messages = current_result.get_messages()
        elif Inputs.inputs.get("alert-triggers", {}).get("new-warnings-only", True):
            new_messages = Utils.get_new_messages(
                previous_messages=previous_result.get_messages(),
                current_messages=current_result.get_messages()
            )

        if len(new_messages) > 0:
            if Inputs.inputs.get("alert-triggers", {}).get("new-warnings-only", True) \
                    or Inputs.inputs.get("alert-triggers", {}).get("all-warnings", True):
                self.trigger_alert = True

            for warning in new_messages:
                warning_message = "{title}\n\t  {message}" \
                    .format(title=warning.get_title(), message=warning.get_message())
                warning_message = re.sub(r"<[^>]+>|&nbsp;", "", warning_message)
                if warning_message not in self.report.get("warnings", []):
                    self.report.get("warnings").append(warning_message)

    @staticmethod
    def get_different_ports(previous: dict, current: dict):
        different_ports_results = []
        for port, current_result in current.items():
            if port not in previous:
                continue

            previous_result = previous.get(port)
            if not Utils.is_same_port_result(current_result, previous_result):
                different_ports_results.append(port)

        return different_ports_results

    def print_report(self):
        self.output_dispatcher.write(where="REPORT", what=self.generate_report())

    def send_report(self):
        if self.trigger_alert:
            try:
                from_addr = "tvw@tango.lu"
                to_addr = Inputs.inputs.get("email-address")

                mail_content = self.generate_report()

                s = smtplib.SMTP(host=Inputs.inputs.get("mail-server"), port=Inputs.inputs.get("mail-server-port"))
                s.starttls()
                s.login(Inputs.inputs.get("mail-server-auth"), Inputs.inputs.get("mail-server-pass"))

                msg = MIMEMultipart()
                msg['From'] = from_addr
                msg['To'] = to_addr
                msg['Subject'] = "SCANBOX Report"
                msg.attach(MIMEText(mail_content, 'plain'))

                attachment = open(self.csv_file, 'rb')
                part = MIMEBase("application", "octet-stram")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", "attachment; filename= " + self.csv_file.split("/")[-1])

                msg.attach(part)
                # send the message via the server set up earlier.
                s.sendmail(from_addr, to_addr, msg.as_string())

                del msg
                s.quit()
            except (ConnectionError, TimeoutError):
                print("Unable to connect with mail server")
        else:
            print("No need to send an email")

    def generate_report(self) -> str:
        report = "=========================================== SCANBOX report " \
                 "===========================================\n\n"
        report += "Please find attached the CSV file containing the open ports for each IP + response time.\n\n"

        if len(self.report.get("new-entry", [])) > 0:
            report += "[X] New IP/record scanned:\n"
            for line in self.report.get("new-entry", []):
                report += "\t- {line}\n".format(line=line)
            report += "\n"

        if len(self.report.get("changed-dns-records", [])) > 0:
            report += "[X] DNS record changes:\n"
            for line in self.report.get("changed-dns-records", []):
                report += "\t- {line}\n".format(line=line)
            report += "\n"

        if len(self.report.get("unexpected-port-responses", [])) > 0:
            report += "[X] Unexpected port responses:\n"
            for line in self.report.get("unexpected-port-responses", []):
                report += "\t- {line}\n".format(line=line)
            report += "\n"

        if len(self.report.get("different-open-ports", [])) > 0:
            report += "[X] Different open/closed ports:\n"
            for line in self.report.get("different-open-ports", []):
                report += "\t- {line}\n".format(line=line)
            report += "\n"

        if len(self.report.get("warnings", [])) > 0:
            report += "[x] Warnings"
            if Inputs.inputs.get("new-warnings-only") and not Inputs.inputs.get("all-warnings"):
                report += " (only new warnings):\n"
            else:
                report += ":\n"

            for line in self.report.get("warnings", []):
                report += "\t- {line}\n".format(line=line)

        report += "\n------------------------------------------------------------------------------------------------" \
                  "------\n"
        report += "This report was generated using the following config:\n\n"
        inputs_censored = Inputs.inputs.copy()
        inputs_censored["mail-server-pass"] = "*" * len(inputs_censored.get("mail-server-pass"))
        report += json.dumps(inputs_censored, indent=4)

        return report

    @staticmethod
    def response_match_expected(response, expected):
        if expected == "NONE":
            return True
        elif (expected == "OPEN" and Utils.is_positive_result(response)) or \
             (expected == "CLOSE" and Utils.is_negative_result(response)):
            return True
        else:
            return False
