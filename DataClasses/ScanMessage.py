import json
from datetime import datetime


class ScanMessage:
    """
    Represents a massage that can be generated during the scan. The messages are included into the scan report and
    displayed on the GUI
    """

    def __init__(self, title: str, message: str, type="warning"):
        self.title = title
        self.message = message
        self.type = type
        now = datetime.now()
        self.time = "{year}-{month}-{day} at {hours}:{minutes}:{seconds}" \
            .format(
                year=now.year,
                month='%02d' % now.month,
                day='%02d' % now.day,
                hours='%02d' % now.hour,
                minutes='%02d' % now.minute,
                seconds='%02d' % now.second
            )

    def get_time(self) -> str:
        return self.time

    def get_message(self) -> str:
        return self.message

    def get_type(self) -> str:
        return self.type

    def get_title(self) -> str:
        return self.title

    def to_dict(self) -> dict:
        return {
            "time": self.get_time(),
            "title": self.get_title(),
            "message": self.get_message(),
            "type": self.get_type()
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __str__(self):
        return self.to_json()

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def from_dict(message):
        scan_message = ScanMessage(
            title=message.get("title"),
            message=message.get("message"),
            type=message.get("type")
        )
        scan_message.time = message.get("time")
        return scan_message

    def __eq__(self, other):
        """
        :type other: ScanMessage
        """
        return self.get_title() == other.get_title() and \
               self.get_type() == other.get_type()
