
from file_utils import get_all_files, get_new_files, remove_directory
from json_utils import read_json_file, check_json_value
from text_formats import FormatSimple, FormatAtbashSimple
from parsing_utils import parse_file, ExpectedLogEntry, require_log_entry, parse_string
from run_command import AtbashRunner
from utils import ValidationException


def define_expected_log_entries_console():
    result = [ExpectedLogEntry(severity="INFO", code="CLI-103", content="Started Atbash Runtime"),
              ExpectedLogEntry(severity="WARNING", code="CLI-105", content="No Applications running"),
              ExpectedLogEntry(severity="SEVERE", code="CLI-108", content="Atbash Runtime stopped")]
    return result


def define_expected_log_entries():
    result = [ExpectedLogEntry(severity="INFO", code="*CLI-102", content="Starting Atbash Runtime version"),
              ExpectedLogEntry(severity="WARNING", code="CLI-105", content="No Applications running"),
              ExpectedLogEntry(severity="SEVERE", code="CLI-108", content="Atbash Runtime stopped")]
    return result


def check_console_log(console):
    parsed_log = parse_string(console, FormatSimple())
    not_found = False
    for expected in define_expected_log_entries_console():
        if not require_log_entry(parsed_log, expected, "Console output"):
            not_found = True
    if not_found:
        raise ValidationException("Not all log entries are found")


def check_log():
    file_name = "default/logs/runtime.log"
    parsed_log = parse_file(file_name, FormatAtbashSimple())
    not_found = False
    for expected in define_expected_log_entries():
        if not require_log_entry(parsed_log, expected, file_name):
            not_found = True
    if not_found:
        raise ValidationException("Not all log entries are found")


def check_files_creates(new_files):
    not_found = False
    if "./default/logging.properties" not in new_files:
        print("Missing default/logging.properties file")
        not_found = True
    if "./default/config.json" not in new_files:
        print("Missing default/config.json file")
        not_found = True
    if "./default/logs/runtime.log" not in new_files:
        print("Missing default/logs/runtime.log file")
        not_found = True
    if not_found:
        raise ValidationException("Not all files are found")


def check_json_config():
    json = read_json_file("default/config.json")
    checks_passed = True
    checks_passed = checks_passed \
                    and check_json_value(json, ["endpoints", "port"], [8080],
                                         "config.json - Http Port has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["logging", "logToConsole"], [False],
                                         "config.json - logToConsole has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["logging", "logToFile"], [True],
                                         "config.json - logToFile has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["monitoring", "jmx"], [False],
                                         "config.json - Monitoring jmx has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["monitoring", "flightRecorder"], [False],
                                         "config.json - Monitoring flightRecorder has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["modules", "configuration"], [{}],
                                         "config.json - Configuration modules has not the expected value")
    if not checks_passed:
        raise ValidationException("Not all JSON entries are found")


def clean_up():
    remove_directory("default")


"""
Start Runtime with no application (not in domain mode). Does it stop and shows appropriate error messages.
The console and log file are checked for log entries.
Checks if the config.json file is present and has the correct content.
"""
if __name__ == '__main__':
    print("Launching the Runtime with no application")
    files_at_start = get_all_files(".")
    runner = AtbashRunner()
    console = runner.launch_runtime_no_wait()

    files = get_all_files(".")
    new_files = get_new_files(files_at_start, files)
    check_files_creates(new_files)

    check_console_log(console)
    check_log()

    check_json_config()
    clean_up()
    print("Scenario 1 testing completed successfully")
