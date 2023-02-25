from endpoints import get_on_endpoint
from file_utils import get_all_files, remove_directory
from text_formats import parse_jmx_application_output
from parsing_utils import parse_jmxterm_output, check_for_line
from run_command import AtbashRunner, execute_command
from utils import ValidationException, jmx_config

def check_JMX_atbash_info(output):
    lines = parse_jmxterm_output(output)
    expected = ["Version = 1.0.0-SNAPSHOT;", "Mode = Runtime;",
                "StartedModules = ( Core, Config, Logging, mp-config, jetty, jersey );"]
    not_found = []
    for entry in expected:
        if not check_for_line(lines, entry):
            not_found.extend(entry)

    if len(not_found) > 0 or len(lines) != 3:
        print("JMX Atbash Info Bean info")
        print(output)
        raise ValidationException("The JMX Atbash Info Bean does not contain the expected value")


def check_JMX_atbash_applications(output):
    lines = parse_jmxterm_output(output)
    apps = parse_jmx_application_output('\n'.join(lines))
    if len(apps) != 1:
        print(output)
        raise ValidationException("The JMX Atbash Application Bean should only have data for 1 application")
    if apps[0]["Name"] != "demo-rest" or apps[0]["ContextRoot"] != "/demo-rest" or apps[0]["Specifications"] != "REST":
        print(output)
        raise ValidationException("The JMX Atbash Application Bean does not contain the expected values")


def clean_up():
    remove_directory("default")


"""
Start Runtime with watcher OFF. Does JMX has no Atbash bean?

"""
if __name__ == '__main__':
    print("Launching the Runtime with watcher off")
    files_at_start = get_all_files(".")
    runner = AtbashRunner()
    runner.launch_runtime(jvm_params=jmx_config(), user_params=["-w", "OFF", "demo-rest.war"])

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
    if response.status_code != 200 and response.content != "Hello Atbash":
        print("Call to Hello endpoint not expected result \n" + str(response.content))

    output = execute_command(
        ["java", "-jar", "jmxterm-1.0.2-uber.jar", "-l", "localhost:8765", "-i", "Atbash-info.jmx"])
    if "#IllegalArgumentException: Domain Atbash doesn't exist, check your spelling" not in output:
        raise ValidationException("The Atbash Bean still exist on JMX")

    console = runner.end_process()

    clean_up()
    print("Scenario 21 testing completed successfully")
