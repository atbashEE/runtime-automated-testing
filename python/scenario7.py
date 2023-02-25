import os
import time

from endpoints import get_on_endpoint
from file_utils import remove_directory, extract_log_files, get_all_files, get_new_files
from json_utils import check_json_value, parse_json

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
    if len(log_files) != 4:
        raise ValidationException("Log rotation did not happen as we need 4 files")
    validation_ok = True
    for name in log_files:
        if not name.endswith(".log"):
            if name.endswith(".gz"):
                file_stats = os.stat(name)
                if file_stats.st_size > 5000:
                    print("File %s doesn't seem to be compressed since the size is too large" % name)
                    validation_ok = False
            else:
                print("File %s doesn't have the correct suffix of .gz" % name)
    if not validation_ok:
        raise ValidationException("Log file check filed")

def clean_up():
    remove_directory("default")


"""
The runtime is started in domain mode and with the 'runtime-cli', the rotation file size is changed, max history files set and compression turned on.
The script checks if the log rotation change is picked up dynamically and correctly applied. (only 3 history files that are compressed)
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

    response = get_on_endpoint("http://localhost:8080/logging/test/logging/flood")
    if response.status_code != 200 and response.content != "Logging started ":
        print("Call to Logging (flood) endpoint not expected result \n" + str(response.content))

    print("Waiting 10 sec")
    time.sleep(10)

    print("Changing log rotation size limit, max history and compression")
    # 500000 is the smallest valid value that is accepted
    cli_out = cli.execute_cli(["set-logging-configuration", "rotationLimitInBytes=500000", "maxHistoryFiles=3", "compressOnRotation=true"])
    if "INFO: Command execution successful" not in str(cli_out):
        print("output of 'atbash-cli' is not as expected: %s " % cli_out)

    print("Waiting 180 sec")
    time.sleep(180)

    console = runner.end_process()

    files = get_all_files(".")
    new_files = get_new_files(files_at_start, files)
    check_number_of_log_files(new_files)

    clean_up()
    print("Scenario 7 testing completed successfully")
