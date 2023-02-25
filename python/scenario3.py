from endpoints import get_on_endpoint
from file_utils import  get_all_files, get_new_files, remove_directory, extract_log_files
from text_formats import FormatSimple, FormatAtbashSimple
from parsing_utils import parse_file, ExpectedLogEntry, require_log_entry, parse_string
from run_command import AtbashRunner
from utils import ValidationException


def define_expected_log_entries_console():
    result = [ExpectedLogEntry(severity="INFO", code="CLI-103", content="Started Atbash Runtime"),
              ExpectedLogEntry(severity="INFO", code="CLI-104", content="1 Application(s) running")]
    return result


def define_expected_log_entries():
    result = [ExpectedLogEntry(severity="INFO", code="*CLI-102", content="Starting Atbash Runtime version"),
              ExpectedLogEntry(severity="INFO", code="CLI-103", content="Started Atbash Runtime"),
              ExpectedLogEntry(severity="INFO", code="DEPLOY-101", content="Starting deployment of 'demo-rest'"),
              ExpectedLogEntry(severity="INFO", content="Loading application demo-rest"),  # now Loading instead of deploying
              ExpectedLogEntry(severity="INFO", code="MPCONFIG-001", content="MP Config functionality is disabled")]
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
    if "./default/applications.json" not in new_files:
        print("Missing default/applications.json file")
        not_found = True
    if not_found:
        raise ValidationException("Not all files are found")


def clean_up():
    remove_directory("default")


def check_number_of_log_files(new_files):
    log_files = extract_log_files(new_files)
    if len(log_files) != 2:
        raise ValidationException("Start of Runtime didn't force a log file rotation")


"""
After a first time, the runtime is again launched but this tim without application. Is the persisted deployment loaded and active?
There is a check if the runtime is correctly serving the application.
"""
if __name__ == '__main__':
    print("Launching the Runtime with an application")
    files_at_start = get_all_files(".")
    runner = AtbashRunner()
    runner.launch_runtime(["demo-rest.war"])

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
    if response.status_code != 200 and response.content != "Hello Atbash":
        print("Call to Hello endpoint not expected result \n" + str(response.content))

    console = runner.end_process()

    print("Launching the Runtime a second time without application on command line. Is Persisted version available?")
    runner.launch_runtime()

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
    if response.status_code != 200 and response.content != "Hello Atbash":
        print("Call to Hello endpoint not expected result \n" + str(response.content))

    console = runner.end_process()

    files = get_all_files(".")
    new_files = get_new_files(files_at_start, files)
    check_files_creates(new_files)

    check_number_of_log_files(new_files)

    check_console_log(console)
    check_log()

    clean_up()
    print("Scenario 3 testing completed successfully")
