from endpoints import get_on_endpoint
from file_utils import get_all_files, get_new_files, remove_directory
from json_utils import read_json_file, check_json_value
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
              ExpectedLogEntry(severity="INFO", code="MPCONFIG-001", content="MP Config functionality is disabled"),
              ExpectedLogEntry(severity="INFO", code="JERSEY-104", content="End of registration of WebApp 'demo-rest'"),
              ExpectedLogEntry(severity="INFO", code="DEPLOY-102", content="End of deployment of 'demo-rest'"),
              ExpectedLogEntry(severity="INFO", code="CLI-104", content="1 Application(s) running"),
              ExpectedLogEntry(severity="FINEST", code="*CLI-1001", content="Handling command line arguments"),
              ExpectedLogEntry(severity="FINEST", code="*CLI-1002",
                               content="Command line arguments in use --daemon=false --profile=default --verbose=true --watcher=MINIMAL --root=. --configName=default --logToConsole=false --logToFile=true --warmup=false --stateless=false "),
              ExpectedLogEntry(severity="FINEST", code="*CLI-102", content="JDK Version 'JDK 11'"),
              ExpectedLogEntry(severity="FINEST", code="*CLI-102", content="Full version '11.0.14.1+1-LTS'"),
              ExpectedLogEntry(severity="FINEST", code="*CLI-102", content="JVM Vendor 'Azul Systems, Inc.'"),
              ExpectedLogEntry(severity="FINEST", code="*CLI-102", content="JVM name 'OpenJDK 64-Bit Server VM'"),
              ExpectedLogEntry(severity="FINEST", code="*CLI-102", content="OS name 'Mac OS X'"),
              ExpectedLogEntry(severity="FINEST", code="*CLI-102", content="Java memory 256MB"),
              ExpectedLogEntry(severity="FINEST", code="*MODULE-1001",
                               content="List of Modules included in Runtime 'Core,Config,Logging,jetty,jersey,remote-cli,mp-config,mp-jwt,metrics,microstream'"),
              ExpectedLogEntry(severity="FINEST", code="*CORE-1001", content="Module startup"),
              ExpectedLogEntry(severity="FINEST", code="*CORE-1002", content="Module ready"),
              ExpectedLogEntry(severity="FINEST", code="*CORE-1003",
                               content="Registering instance of 'class be.atbash.runtime.core.data.RunData' against Module 'Core'"),
              ExpectedLogEntry(severity="FINEST", code="*CORE-1003",
                               content="Registering instance of 'class be.atbash.runtime.core.data.watcher.WatcherService' against Module 'Core'"),
              ExpectedLogEntry(severity="FINEST", code="*CONFIG-1001", content="Module startup"),
              ExpectedLogEntry(severity="FINEST", code="*CONFIG-1002", content="Module ready"),
              ExpectedLogEntry(severity="FINEST", code="*CORE-1003",
                               content="Registering instance of 'class be.atbash.runtime.core.data.RuntimeConfiguration' against Module 'Config'"),
              ExpectedLogEntry(severity="FINEST", code="*CORE-1003",
                               content="Registering instance of 'class be.atbash.runtime.core.data.deployment.info.PersistedDeployments' against Module 'Config'"),
              ExpectedLogEntry(severity="FINEST", code="*CORE-1003",
                               content="Registering instance of 'class be.atbash.runtime.config.ConfigurationManager' against Module 'Config'"),
              ExpectedLogEntry(severity="FINEST", code="*LOG-1001", content="Logging Module startup"),
              ExpectedLogEntry(severity="FINEST", code="LOG-1002", content="Logging Module ready"),
              ExpectedLogEntry(severity="FINEST", code="JETTY-1001", content="Module startup"),
              ExpectedLogEntry(severity="FINEST", code="JETTY-1002", content="Module ready"),
              ExpectedLogEntry(severity="FINEST", code="CORE-1003",
                               content="Registering instance of 'class org.eclipse.jetty.server.handler.HandlerCollection' against Module 'jetty'"),
              ExpectedLogEntry(severity="FINEST", code="JERSEY-1001", content="Module startup"),
              ExpectedLogEntry(severity="FINEST", code="JERSEY-1002", content="Module ready")]
    return result


def check_console_log(console):
    parsed_log = parse_string(console, FormatSimple())
    not_found = False
    for expected in define_expected_log_entries_console():
        if not require_log_entry(parsed_log, expected, "Console output"):
            not_found = True
    if not_found:
        raise ValidationException("Not all log entries are found")
    if len(parsed_log) > 2:
        raise ValidationException("Console log contains more than 2 entries")


def check_log():
    file_name = "default/logs/runtime.log"
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


def check_application_config():
    json = read_json_file("default/applications.json")
    checks_passed = True
    checks_passed = checks_passed \
                    and check_json_value(json, ["deployments", "deploymentName"], ["demo-rest"],
                                         "applications.json - Deployment name has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["deployments", "deploymentLocation"], ["/demo-rest.war"],
                                         "applications.json - Deployment location has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["deployments", "specifications"], ["REST"],
                                         "applications.json - Discovered specifications has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["deployments", "sniffers"], ["RestSniffer"],
                                         "applications.json - Defined sniffers has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["deployments", "contextRoot"], ["/demo-rest"],
                                         "applications.json - Defined sniffers has not the expected value")
    checks_passed = checks_passed \
                    and check_json_value(json, ["deployments", "deploymentData", "jersey.class.names"], [
        "be.atbash.runtime.demo.rest.resources.HelloResource,be.atbash.runtime.demo.rest.resources.RequestResource"],
                                         "applications.json - Class names provided to Jersey has not the expected value ")
    checks_passed = checks_passed \
                    and check_json_value(json, ["deployments", "deploymentData", "mp-config.enabled"], ["false"],
                                         "applications.json - MP Config enabled has not the expected value ")
    checks_passed = checks_passed \
                    and check_json_value(json, ["deployments", "deploymentData", "jersey.application.path"], ["/rest"],
                                         "applications.json - Application path has not the expected value ")
    checks_passed = checks_passed \
                    and check_json_value(json, ["deployments", "deploymentData", "jersey.package.names"],
                                         ["be.atbash.runtime.demo.rest.resources,be.atbash.runtime.demo.rest.provider"],
                                         "applications.json - Package names for Jersey has not the expected value ")
    if not checks_passed:
        raise ValidationException("Not all JSON entries are found")


def clean_up():
    remove_directory("default")


"""
The Runtime is started with verbose mode on. The log is checked for additional entries.
"""
if __name__ == '__main__':
    print("Launching the Runtime in verbose mode")
    files_at_start = get_all_files(".")
    runner = AtbashRunner()
    runner.launch_runtime(["-v", "demo-rest.war"])

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
    if response.status_code != 200 and response.content != "Hello Atbash":
        print("Call to Hello endpoint not expected result \n" + str(response.content))

    console = runner.end_process()

    files = get_all_files(".")
    new_files = get_new_files(files_at_start, files)
    check_files_creates(new_files)

    check_console_log(console)
    check_log()

    check_application_config()

    clean_up()
    print("Scenario 11 testing completed successfully")
