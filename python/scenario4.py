from endpoints import get_on_endpoint
from file_utils import remove_directory
from json_utils import check_json_value, parse_json, retrieve_application_info
from text_formats import FormatSimple
from parsing_utils import ExpectedLogEntry, require_log_entry, parse_string
from run_command import AtbashRunner
from utils import ValidationException


def define_expected_log_entries_console():
    result = [ExpectedLogEntry(severity="INFO", code="CLI-103", content="Started Atbash Runtime"),
              ExpectedLogEntry(severity="WARNING", code="CLI-105", content="No Applications running")]
    return result


def define_expected_log_entries():
    result = [ExpectedLogEntry(severity="INFO", code="*CLI-102", content="Starting Atbash Runtime version"),
              ExpectedLogEntry(severity="INFO", code="CLI-103", content="Started Atbash Runtime"),
              ExpectedLogEntry(severity="INFO", code="DEPLOY-101", content="Starting deployment of 'demo-rest'"),
              ExpectedLogEntry(severity="INFO", content="Loading application demo-rest"),
              # now Loading instead of deploying
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


def clean_up():
    remove_directory("default")


def check_status_response():
    response = get_on_endpoint("http://localhost:8080/domain/status")
    json = parse_json(response.content.decode())
    checks_passed = True
    checks_passed = checks_passed \
                    and check_json_value(json, ["success"], [True],
                                         "status response - success has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["data", "version"], ["1.0.0-SNAPSHOT"],
                                         "status response - version has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["data", "modules"],
                                         ["Core,Config,Logging,mp-config,jetty,jersey,remote-cli"],
                                         "status response - modules has not the expected value")
    if not checks_passed:
        raise ValidationException("Not all log entries are found")


def check_list_applications_response():
    response = get_on_endpoint("http://localhost:8080/domain/list-applications")
    json = parse_json(response.content.decode())
    applications = retrieve_application_info(json)
    if len(applications) != 1 and "demo-rest" not in applications.keys():
        print("Expecting the result from list-applications to contain just info about demo-rest application")
        print("Received \n" + str(json))
        raise ValidationException("Wrong result from call to list-applications")
    checks_passed = True
    checks_passed = checks_passed \
                    and check_json_value(json, ["success"], [True],
                                         "list-applications response - success has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(applications["demo-rest"], ["contextRoot"], ["/demo-rest"],
                                         "list-applications response - contextRoot has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(applications["demo-rest"], ["specifications"], ["REST"],
                                         "list-applications response - specifications has not the expected value")
    if not checks_passed:
        raise ValidationException("Not all JSON entries are found")


def check_empty_list_applications_response():
    response = get_on_endpoint("http://localhost:8080/domain/list-applications")
    print("list-applications")

    json = parse_json(response.content.decode())
    applications = retrieve_application_info(json)
    if len(applications) != 0:
        print("Expecting the result from list-applications to contain no deployed applications")
        print("Received \n" + str(json))
        raise ValidationException("Wrong result from call to list-applications")


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


def check_deploy_command_output(cli_out):
    parsed_log = parse_string(cli_out, FormatSimple())

    not_found = False
    expected = ExpectedLogEntry(severity="INFO", code="demo-rest",
                                content="Application deployed with the context '/demo-rest")
    if not require_log_entry(parsed_log, expected, "CLI deploy output"):
        not_found = True
    expected = ExpectedLogEntry(severity="INFO", content="Command execution successful")
    if not require_log_entry(parsed_log, expected, "CLI deploy output"):
        not_found = True
    if not_found:
        raise ValidationException("Return from deploy command not as expected")


def check_undeploy_command_output(cli_out):
    parsed_log = parse_string(cli_out, FormatSimple())
    not_found = False
    expected = ExpectedLogEntry(severity="INFO", code="demo-rest", content="Application is removed from the Runtime.")
    if not require_log_entry(parsed_log, expected, "CLI undeploy output"):
        not_found = True
    expected = ExpectedLogEntry(severity="INFO", content="Command execution successful")
    if not require_log_entry(parsed_log, expected, "CLI undeploy output"):
        not_found = True
    if not_found:
        raise ValidationException("Result from undeploy not as expected")


"""
The runtime is first started in domain mode. An application is deployed, checked if the endpoints are available and undeployed again.
- The 'status' command of runtime-cli application is checked
- Health endpoint of runtime is checked if application appears (and disappears)
- The 'list-applications' command of runtime-cli application is checked.
"""
if __name__ == '__main__':
    print("Launching the Runtime in Domain mode with no applications")
    runner = AtbashRunner()
    runner.launch_runtime(["-p", "domain"])

    check_status_response()
    check_health_response([])
    check_empty_list_applications_response()

    print("Deploy application remotely")
    cli = AtbashRunner()
    cli_out = cli.execute_cli(["deploy", "demo-rest.war"])
    check_deploy_command_output(cli_out)

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
    if response.status_code != 200 and response.content != "Hello Atbash":
        print("Call to Hello endpoint not expected result \n" + str(response.content))

    check_health_response(['demo-rest'])
    check_list_applications_response()

    print("Undeploy application remotely")

    cli_out = cli.execute_cli(["undeploy", "demo-rest"])
    check_undeploy_command_output(cli_out)

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
    if response.status_code != 404:
        print("Call to Hello endpoint not expected result (should be 404)")

    check_health_response([])
    check_empty_list_applications_response()

    console = runner.end_process()
    check_console_log(console)

    clean_up()
    print("Scenario 4 testing completed successfully")
