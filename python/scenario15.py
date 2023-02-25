import requests

from endpoints import get_on_endpoint
from file_utils import remove_directory
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
        if not lines[1].startswith("PID") or not lines[1].endswith(" - archives demo-rest.war"):
            correct = False
        if not correct:
            msg = "list-processes should report 1 process. But output is %s " % output
            raise ValidationException(msg)


"""
Checks if the runtime-cli command list-processes and stop-process works on a Runtime running in the foreground.

"""
if __name__ == '__main__':
    print("Check runtime-cli list-processes command.")

    runner = AtbashRunner()
    output = runner.execute_cli(["list-processes"])
    check_list_processes_output(output, False)

    print("Launch Runtime with application")
    runner.launch_runtime(["demo-rest.war"])

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
    print("Scenario 15 testing completed successfully")
