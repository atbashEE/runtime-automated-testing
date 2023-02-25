import time

from endpoints import get_on_endpoint
from file_utils import remove_directory, extract_log_files, get_all_files, get_new_files
from json_utils import check_json_value, parse_json
from text_formats import FormatUniformWithAnsi
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


def check_log_files(new_files):
    log_files = extract_log_files(new_files)
    log_files.extend(extract_log_files(new_files, base="test"))
    if len(log_files) != 2:
        raise ValidationException("Log rotation did not happen as we need 2 files")
    parsed_log = parse_file("./default/logs/test.log", FormatUniformWithAnsi())
    if len(parsed_log) < 4:
        raise ValidationException("Not enough entries in the new log file")


def clean_up():
    remove_directory("default")


"""
The runtime is started in domain mode and with the 'runtime-cli', the log configuration is updated by sending a new config file.
The script checks if the log rotation change is picked up dynamically and correctly applied. (uses the uniform log format with ASCII coloring) 
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

    print("Waiting 10 sec")
    time.sleep(10)

    print("Changing log configuration by sending new file")

    cli_out = cli.execute_cli(["set-logging-configuration", "--file", "new-logging.properties"])
    if "INFO: Command execution successful" not in str(cli_out):
        print("output of 'atbash-cli' is not as expected: %s " % cli_out)

    print("Waiting 30 sec")
    time.sleep(30)

    console = runner.end_process()

    files = get_all_files(".")
    new_files = get_new_files(files_at_start, files)
    check_log_files(new_files)

    clean_up()
    print("Scenario 8 testing completed successfully")
