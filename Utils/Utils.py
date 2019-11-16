class Utils:
    @staticmethod
    def make_link(url: str, trim=False) -> str:
        if trim and len(url) > 55:
            return f"<a href='{url}' target='_blank'>{url[0:45]}&nbsp;[...]&nbsp;{url[-10:]}</a>&nbsp;"
        else:
            return f"<a href='{url}' target='_blank'>{url}</a>&nbsp;"

    @staticmethod
    def is_same_port_result(result1, result2):
        return (Utils.is_positive_result(result1) and Utils.is_positive_result(result2)) or \
               (Utils.is_negative_result(result1) and Utils.is_negative_result(result2))

    @staticmethod
    def get_new_messages(previous_messages, current_messages):
        new_messages = []
        for message in current_messages:
            if message not in previous_messages:
                new_messages.append(message)
        return new_messages

    @staticmethod
    def is_positive_result(result):
        return result is not None and (result == "OK" or result >= 0)

    @staticmethod
    def is_negative_result(result):
        return result is None or result == -1
