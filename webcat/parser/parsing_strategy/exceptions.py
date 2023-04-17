
class NoParsableContentError(Exception):
    """
    Exception raised when no parsable content is found in a file.
    Raised by Parser class.
    """
    def __init__(self, value):
        self.value = value
        # set default message
        if value is None:
            self.value = "No parsable content found."

    def __str__(self):
        return repr(self.value)