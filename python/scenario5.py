import time

from endpoints import get_on_endpoint
from file_utils import remove_directory, extract_log_files, sort_log_file_names, get_all_files, get_new_files
from json_utils import check_json_value, parse_json, retrieve_application_info
from text_formats import FormatAtbashSimple
from parsing_utils import parse_file
from run_command import AtbashRunner
from utils import ValidationException


def check_health_response(expected):
    response = get_on_endpoint("http://localhost:8080/health")
    json = parse_json(response.content.decode())
    checks_passed = True
    checks_passed = checks_passed \
                    and check_json_value(json, ["status"], ["UP"],
                                         "health response - status has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["checks", "data"], expected,
                                         "health response - checks data has not the expected value")
    if not checks_passed:
        raise ValidationException("Not all JSON entries are found")


def check_number_of_log_files(new_files):
    log_files = extract_log_files(new_files)
    if len(log_files) != 3:
        raise ValidationException("Log rotation did not happen as we need 3 files")
    sorted_log_files = sort_log_file_names(log_files)
    # The log file nr 1 is the one that should have just lasted 1 minute = 12 (entries) * 5 second
    parsed_log = parse_file(sorted_log_files[1], FormatAtbashSimple())
    if len(parsed_log) != 12:
        msg = "Log File %s does not contain the 12 expected entries " % sorted_log_files[1]
        raise ValidationException(msg)


def clean_up():
    remove_directory("default")


"""
The runtime is started in domain mode and with the 'runtime-cli', the rotation time for the log file is changed.
The script checks if the log rotation change is picked up dynamically and correctly applied.
"""
if __name__ == '__main__':
    files_at_start = get_all_files(".")

    print("Launching the Runtime in Domain mode with logging application")
    runner = AtbashRunner()
    runner.launch_runtime(["-p", "domain"])

    # We deploy remotely since health endpoint is more complicated in Domain mode when application is specified at start
    print("Deploy application remotely")
    cli = AtbashRunner()
    cli.execute_cli(["deploy", "logging.war"])

    check_health_response(['logging'])

    response = get_on_endpoint("http://localhost:8080/logging/test/logging")
    if response.status_code != 200 and response.content != "Logging started ":
        print("Call to Logging endpoint not expected result \n" + str(response.content))

    print("Waiting 30 sec")
    time.sleep(30)

    print("Changing log rotation time limit")
    cli_out = cli.execute_cli(["set-logging-configuration", "rotationTimelimitInMinutes=1"])
    if "INFO: Command execution successful" not in str(cli_out):
        print("output of 'atbash-cli' is not as expected: %s " % cli_out)

    print("Waiting 70 sec")
    time.sleep(70)

    console = runner.end_process()

    files = get_all_files(".")
    new_files = get_new_files(files_at_start, files)
    check_number_of_log_files(new_files)

    clean_up()
    print("Scenario 5 testing completed successfully")
