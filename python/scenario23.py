from endpoints import get_on_endpoint
from file_utils import get_all_files, remove_directory
from run_command import AtbashRunner
from text_formats import PrometheusMetrics
from utils import ValidationException


def clean_up():
    remove_directory("default")


def check_metrics_count(metrics_data, param, line):
    if metrics_data.keys() != param.keys():
        raise ValidationException("Expected keys {keys} not found in {line}".format(keys=param.keys(), line=line))
    for k in param.keys():
        if metrics_data[k] != param[k]:
            raise ValidationException("Expected value {value} for {key} does not match {line}".format(value=param[k], key=k, line=line))


def check_metrics_quantile(metrics_data, param, line):
    if metrics_data.keys() != param.keys():
        raise ValidationException("Expected keys {keys} not found in {line}".format(keys=param.keys(), line=line))
    for k in param.keys():
        if metrics_data[k] != param[k]:
            if "value" != k:
                raise ValidationException("Expected value {value} for {key} does not match {line}".format(value=param[k], key=k, line=line))
            else:
                if metrics_data[k] == 0:
                    raise ValidationException("Value is 0 for {line}".format(line=line))


def check_prometheus_data(output):
    lines = output.rstrip().split("\n")
    if len(lines) != 32:
        raise ValidationException("32 lines on metrics page expected")
    if "# TYPE application_response_time_seconds summary" != lines[0]:
        raise ValidationException("First line not the expected Prometheus # Type line")
    if "# HELP application_response_time_seconds Server response time" != lines[1]:
        raise ValidationException("First line not the expected Prometheus # Help line")

    endpoint_names = ["GET /hello/{name}", "GET /request", "/*"]
    quantile_values = [0.01, 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]
    metrics = PrometheusMetrics()
    idx = 2
    for i in range(3):
        metrics_data = metrics.parse_count_entry(lines[idx])
        expected_count = 1 if i < 2 else 2  # count = 2 for /*
        check_metrics_count(metrics_data, {"application_name": "demo-rest", "endpoint_name": endpoint_names[i],
                                           "count_value": expected_count}, lines[idx])
        idx += 1
        for j in range(9):
            metrics_data = metrics.parse_quantile_entry(lines[idx])
            check_metrics_quantile(metrics_data,
                                {"application_name": "demo-rest", "endpoint_name": endpoint_names[i],
                                 "quantile_value": quantile_values[j], "value": 7},
                                lines[idx])
            idx += 1


"""
Start Runtime with metrics active. Test if metrics are available in Prometheus format

"""
if __name__ == '__main__':
    print("Launching the Runtime with Metrics and test Prometheus output")
    files_at_start = get_all_files(".")
    runner = AtbashRunner()
    runner.launch_runtime(user_params=["-m", "+metrics", "demo-rest.war"])

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/hello/Atbash")
    if response.status_code != 200 and response.content != "Hello Atbash":
        print("Call to Hello endpoint not expected result \n" + str(response.content))

    response = get_on_endpoint("http://localhost:8080/demo-rest/rest/request")
    if response.status_code != 200 and response.content != "RequestScoped resource response":
        print("Call to Request endpoint not expected result \n" + str(response.content))

    response = get_on_endpoint("http://localhost:8080/metrics")
    check_prometheus_data(response.content.decode())

    console = runner.end_process()

    clean_up()
    print("Scenario 23 testing completed successfully")
