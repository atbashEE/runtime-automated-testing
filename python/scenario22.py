import os

from endpoints import get_on_endpoint
from file_utils import get_all_files, remove_directory, get_jfr_files
from json_utils import parse_json
from run_command import AtbashRunner, execute_command
from utils import ValidationException


def clean_up():
    remove_directory("default")


def extract_message_code(data):
    x = str(data)
    return x[:x.index(":")]


def check_jfr_data():
    jfr_files = get_jfr_files(".")
    events = []
    for file in jfr_files:
        output = execute_command(["java", "-jar", "AtbashJFRDump.jar", file])
        events.extend([extract_message_code(x["message"]) for x in parse_json(output)["events"]])
        os.remove(file)
    if events.sort() != ['DEPLOY-101', 'DEPLOY-102', 'LOG-1001', 'LOG-1002', 'JERSEY-1001', 'JERSEY-1002', 'JETTY-1001', 'JETTY-1002', 'CONFIG-1001', 'CONFIG-1002'].sort():
        print("Found events in JFR file")
        print(events)
        raise ValidationException("Events are not the same")


"""
Start Runtime with JFR active.

"""
if __name__ == '__main__':
    print("Launching the Runtime with JFR")
    files_at_start = get_all_files(".")
    runner = AtbashRunner()
    runner.launch_runtime(user_params=["-w", "JFR", "demo-rest.war"])

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
    if response.status_code != 200 and response.content != "Hello Atbash":
        print("Call to Hello endpoint not expected result \n" + str(response.content))

    console = runner.end_process()
    check_jfr_data()

    clean_up()
    print("Scenario 22 testing completed successfully")
