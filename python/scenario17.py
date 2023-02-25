import atexit
import requests

from endpoints import get_on_endpoint, wait_until_healthy
from file_utils import remove_directory
from text_formats import FormatSimple
from parsing_utils import parse_string
from run_command import AtbashRunner
from utils import ValidationException


def clean_up():
    remove_directory("default")


def check_list_processes_output(output, is_running):
    lines = output.rstrip().split("\n")
    if not is_running:
        if len(lines) != 1 or lines[0] != "CLI-202: These are the Atbash Runtime processes":
            msg = "list-processes should not report any process. But output is %s " % output
            raise ValidationException(msg)
    else:
        correct = True
        if len(lines) != 2:
            correct = False
        if lines[0] != "CLI-202: These are the Atbash Runtime processes":
            correct = False
        if not lines[1].startswith("PID") or not lines[1].endswith("demo-rest.war"):
            correct = False
        if not correct:
            msg = "list-processes should report 1 process. But output is \n%s " % output
            raise ValidationException(msg)


def cleanup_daemon():
    cli = AtbashRunner()
    cli.execute_cli(["stop-process"])


def check_start_daemon_log(output):
    parsed_log = parse_string(output, FormatSimple())
    if len(parsed_log) != 1:
        raise ValidationException("Log from Daemon start contains more than 1 entry")
    log_entry = parsed_log[0]
    if not log_entry["messageCode"] == "CLI-116" or "INFO: CLI-116: The runtime is started in the background with process id" in log_entry["content"]:
        print("Log entry " + log_entry)
        raise ValidationException("Runtime as daemon not started as expected")


"""
Start the runtime as Daemon process through the runtime-cli, wait until the health endpoint says it is ready
Check the application call, and stop the process through the runtime-cli.  
"""
if __name__ == '__main__':
    print("Launch Runtime as daemon through the atbash-cli with application")
    runner = AtbashRunner()
    output = runner.execute_cli(["--runtime-jar", "atbash-runtime/atbash-runtime.jar", "demo-rest.war"])

    # Make sure that we kill the daemon at the end
    atexit.register(cleanup_daemon)

    check_start_daemon_log(output)

    # The daemon process was just started, we need to use health endpoint to see when ready
    healthy = wait_until_healthy("http://localhost:8080/health")
    if not healthy:
        raise ValidationException("Runtime not healthy within 10 seconds")

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
    if response.status_code != 200 and response.content != "Hello Atbash":
        print("Call to Hello endpoint not expected result \n" + str(response.content))

    print("Check runtime-cli list-processes command.")
    output = runner.execute_cli(["list-processes"])
    check_list_processes_output(output, True)

    print("execute runtime-cli stop-process command.")
    output = runner.execute_cli(["stop-process"])
    if output != "CLI-215: The stop command is issued. Was it successful? true":
        print("FAILURE: The output of 'stop-process' command is not as expected %s" % output)

    try:
        response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
        print("The Runtime is still active \n" + str(response.content))
    except requests.exceptions.ConnectionError as e:
        print("Runtime is stopped correctly")

    output = runner.execute_cli(["list-processes"])
    check_list_processes_output(output, False)

    clean_up()
    print("Scenario 17 testing completed successfully")
