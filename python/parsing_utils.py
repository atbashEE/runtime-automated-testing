from text_formats import LogFormat
from utils import ValidationException


class ExpectedLogEntry:
    """
    Class to express expected log entries and verification if a log entry matches the expected values.
    """

    def __init__(self, severity: str = "", code: str = "", content: str = "", class_name:str = "", method_name: str = ""):
        self.severity = severity
        self.code = code
        self.content = content
        self.class_name = class_name
        self.method_name = method_name

    def as_expected(self, log_entry: dict) -> list:
        result = []
        if len(self.severity) > 0:
            if log_entry["severity"] != self.severity:
                result.append("Expected severity %s not found." % self.severity)
        if len(self.code) > 0:
            if "messageCode" in log_entry.keys() and log_entry["messageCode"] != self.code:
                result.append("Expected message code %s not found." % self.code)
        if len(self.content) > 0:
            if self.content not in log_entry["content"]:
                result.append("Content %s not found." % self.content)
        if len(self.class_name) > 0:
            if log_entry["className"] != self.class_name:
                result.append("Class name %s does not match." % self.class_name)
        if len(self.method_name) > 0:
            if log_entry["methodName"] != self.method_name:
                result.append("Method name %s does not match." % self.method_name)

        return result

    def __repr__(self):
        properties = [f'{p}={getattr(self, p)}' for p in ['severity', 'code', 'content', 'class_name', 'method_name'] if
                      getattr(self, p)]
        return f'ExpectedLogEntry({", ".join(properties)})'


def parse_file(file_name: str, log_format: LogFormat) -> list:
    """
    Parses the file according to the provided log format and returns a list of dictionary objects describing the log entries.
    :param file_name: File name to parse
    :param log_format: Log format used for parsing
    :return: list of dictionary objects describing the log entries
    """
    result = []
    try:
        with open(file_name, 'r') as f:
            lines = []
            line = f.readline()
            while line:
                if log_format.is_first_line(line):
                    if len(lines) > 0:
                        result.append(log_format.parse_lines(lines))
                        del lines[:]  # Clear list and all referenced places
                lines.append(line)
                # check for next line
                line = f.readline()
            if len(lines) > 0:
                result.append(log_format.parse_lines(lines))
    except IOError:
        print("An error occurred while reading from the file %s." % file_name)
    return result


def parse_string(text: str, log_format: LogFormat) -> list:
    """
    Parses the text (splitted into lines by the newline character) according to the provided log format and returns a list of dictionary objects describing the log entries.
    :param text: Test to be parsed
    :param log_format: Log format used for parsing
    :return: list of dictionary objects describing the log entries
    """
    result = []
    lines = []
    for line in text.splitlines():

        if log_format.is_first_line(line):
            if len(lines) > 0:
                result.append(log_format.parse_lines(lines))
                del lines[:]  # Clear list and all referenced places
        lines.append(line)

    if len(lines) > 0:
        result.append(log_format.parse_lines(lines))

    return result


def find_entries(log_entries: list, search_entry: ExpectedLogEntry) -> list:
    """
    Looks for log entries that match the expected log entry.
    :param log_entries: list of log entries
    :param search_entry: Description of the expected log entry
    :return: list of log entries that match the expected entry.
    """
    return [x for x in log_entries if len(search_entry.as_expected(x)) == 0]


def require_log_entry(log_entries: list, expected_log_entry: ExpectedLogEntry, file_name: str) -> bool:
    """
    Searches for the expected log entry in the log entries and return False if not found.
    :param log_entries: list of log entries
    :param expected_log_entry: Description of the expected log entry
    :param file_name: file name for the message when log entry is not found
    :return: true when log entry found, false otherwise.
    """
    filtered = find_entries(log_entries, expected_log_entry)
    if len(filtered) == 0:
        print("Following matching log entry %s is not found with in %s" % (expected_log_entry, file_name))
        return False
    return True


def parse_jmxterm_output(output: str) -> list:
    """
    Splits the output in lines and searches for the marker 'Welcome to JMX terminal.'. It returns each non, empty
    line before this marker.
    :param output: text to be parsed
    :return: non-empty lines in the output bdfore the marker.
    """
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    marker_index = None
    for i, line in enumerate(lines):
        if line.startswith("Welcome to JMX terminal."):
            marker_index = i
            break
    if marker_index is None:
        raise ValidationException("Marker not found in text")
    return lines[:marker_index]


def check_for_line(lines: list, text: str) -> bool:
    """
    Check if the text occurs within the list as an item.
    :param lines: lines of text to be checked
    :param text: line of text to be searched within the list
    :return: True when line of text is found or false otherwise.
    """
    result = False
    for line in lines:
        if text == line:
            result = True
    return result
