
from endpoints import get_on_endpoint
from file_utils import remove_directory
from run_command import AtbashRunner
from utils import ValidationException


def clean_up():
    remove_directory("default")


"""
Start the Runtime with an application (not in domain mode) and tries to access a domain endpoint (set log configuration)
The scenario checks if this fails correctly.
"""
if __name__ == '__main__':
    print("Launching the Runtime with application (no domain)")

    runner = AtbashRunner()
    runner.launch_runtime(["logging.war"])

    response = get_on_endpoint("http://localhost:8080/logging/test/logging")
    if response.status_code != 200 and response.content != "Logging started ":
        print("Call to Logging endpoint not expected result \n" + str(response.content))

    print("Try to access domain endpoint (but needs to fail)")
    cli = AtbashRunner()
    cli_out = cli.execute_cli(["set-logging-configuration", "rotationLimitInBytes=500000"])
    if "SEVERE: RC-211: Calling Runtime domain endpoint resulted in status 404 (message" not in cli_out:
        print("Call the domain endpoint did not fail \n" + str(cli_out))
        raise ValidationException("Attempt to call Domain endpoints did not result in expected message")

    console = runner.end_process()

    clean_up()
    print("Scenario 9 testing completed successfully")
