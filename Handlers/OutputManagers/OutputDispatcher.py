from DataClasses.ScanResult import ScanResult
from DataClasses.ScanMessage import ScanMessage
from Handlers.OutputManagers.CSVOutput import CSVOutput
from Handlers.OutputManagers.JSONOutput import JSONOutput
from Handlers.OutputManagers.ListeningPortsOutput import ListeningPortsOutput
from Handlers.OutputManagers.STDOutput import STDOutput
from Handlers.OutputManagers.UIErrorOutput import UIErrorOutput
from Handlers.OutputManagers.UIMessagesOutput import UIMessagesOutput
from Handlers.OutputManagers.UIReportOutput import UIReportOutput
from Singletons import Inputs


class OutputDispatcher:
    """
    Manages all the outputs and dispatches the messages to the concerned output manager
    """

    def __init__(self):
        if Inputs.inputs.get("UI", False):
            self.listening_ports_output = None
            self.ui_messages_output = None
            self.ui_error_output = None
            self.ui_report_output = None

        self.std_output = None
        self.csv_output = None
        self.json_output = None

    def write(self, what, where="STD"):
        """
        Will write "what" on the right "where"
        :type what: ScanResult | ScanMessage | UIErrorMessage | str
        :param what: params to be printed
        :param where: where to output   - CSV:  CSV file
                                        - JSON: JSON file for results storage
                                        - PORTS: GUI listening ports table
                                        - MSG:  GUI messages list
                                        - STD:  Classic STDOut
                                        - ERR: GUI errors bar
        """
        if where == "CSV":
            self.get_csv_output().write(what)
        elif where == "JSON":
            self.get_json_output().write(what)
        elif where == "PORTS" and Inputs.inputs["UI"]:
            self.get_listening_port_output().write(what)
        elif where == "MSG" and Inputs.inputs["UI"]:
            self.get_ui_messages_output().write(what)
        elif where == "ERR" and Inputs.inputs["UI"]:
            self.get_ui_error_output().write(what)
        elif where == "STD":
            self.get_std_output().write(what)
        elif where == "REPORT" and Inputs.inputs["UI"]:
            self.get_ui_report_output().write(what)
            
    def get_listening_port_output(self) -> ListeningPortsOutput:
        if self.listening_ports_output is None:
            self.listening_ports_output = ListeningPortsOutput()
        return self.listening_ports_output

    def get_ui_messages_output(self) -> UIMessagesOutput:
        if self.ui_messages_output is None:
            self.ui_messages_output = UIMessagesOutput()
        return self.ui_messages_output

    def get_ui_error_output(self) -> UIErrorOutput:
        if self.ui_error_output is None:
            self.ui_error_output = UIErrorOutput()
        return self.ui_error_output

    def get_std_output(self) -> STDOutput:
        if self.std_output is None:
            self.std_output = STDOutput()
        return self.std_output

    def get_csv_output(self) -> CSVOutput:
        if self.csv_output is None:
            self.csv_output = CSVOutput()
        return self.csv_output

    def get_json_output(self) -> JSONOutput:
        if self.json_output is None:
            self.json_output = JSONOutput()
        return self.json_output

    def get_ui_report_output(self) -> UIReportOutput:
        if self.ui_report_output is None:
            self.ui_report_output = UIReportOutput()
        return self.ui_report_output
