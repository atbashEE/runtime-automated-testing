from endpoints import get_on_endpoint
from file_utils import get_all_files, get_new_files, remove_directory
from text_formats import FormatSimple, FormatAtbashSimple
from parsing_utils import parse_file, ExpectedLogEntry, require_log_entry, find_entries, parse_string
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
              ExpectedLogEntry(severity="INFO", content="Deploying application demo-rest.war"),
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
    file_name = "logs/runtime.log"
    parsed_log = parse_file(file_name, FormatAtbashSimple())
    not_found = False
    for expected in define_expected_log_entries():
        if not require_log_entry(parsed_log, expected, file_name):
            not_found = True
    if not_found:
        raise ValidationException("Not all log entries are found")
    filtered = find_entries(parsed_log, ExpectedLogEntry(severity="INFO", method_name="log",
                                                         content="All endpoints for Jersey application"))
    if len(filtered) == 1:
        content = filtered[0]["entry"]
        if "GET     /rest/hello/{name}" not in content or \
                "OPTIONS /rest/hello/{name}" not in content or \
                "GET     /rest/request" not in content or \
                "OPTIONS /rest/request" not in content:
            print("Not all endpoints of the application are present in the log")
            raise ValidationException("Not all endpoints are listed in the log")
    else:
        raise ValidationException("Missing information about the endpoints of the application")


def check_files_creates(new_files):
    not_found = False
    if "./logs/runtime.log" not in new_files:
        print("Missing ./logs/runtime.log file")
        not_found = True
    if not_found:
        raise ValidationException("Created files are not correct.")
    not_found = True
    for item in new_files:
        if item.startswith("./default"):
            not_found = False
    if not not_found:
        raise ValidationException("The 'default' directory is created")


def clean_up():
    remove_directory("logs")


"""
The Runtime is started in stateless mode and checked if the application is accessible.
The start is performed za second time, with same parameters, to make sure no blocking info is kept on disk
There is a check to see if the log is still created correctly. 
"""
if __name__ == '__main__':
    print("Starting Runtime with application in stateless mode")
    files_at_start = get_all_files(".")
    runner = AtbashRunner()
    runner.launch_runtime(["--stateless", "demo-rest.war"])

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
    if response.status_code != 200 and response.content != "Hello Atbash":
        print("Call to Hello endpoint not expected result \n" + str(response.content))

    console = runner.end_process()

    files = get_all_files(".")
    new_files = get_new_files(files_at_start, files)
    check_files_creates(new_files)

    check_console_log(console)
    check_log()

    print("Starting Runtime with application in stateless mode for the second time")
    runner.launch_runtime(["--stateless", "demo-rest.war"])

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
    if response.status_code != 200 and response.content != "Hello Atbash":
        print("Call to Hello endpoint not expected result \n" + str(response.content))

    console = runner.end_process()

    clean_up()

    print("Scenario 13 testing completed successfully")
