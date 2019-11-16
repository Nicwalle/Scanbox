import json


class UIErrorMessage:
    """
    Represents an error message which will be displayed on the UI. (e.g. dns input file does not exists)
    """

    def __init__(self, message: str, type="general"):
        self.message = message
        self.type = type

    def get_message(self) -> str:
        return self.message

    def get_type(self) -> str:
        return self.type

    def to_dict(self) -> dict:
        return {
            "message": self.get_message(),
            "type": self.get_type()
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def __str__(self):
        return self.to_json()
