import atexit
import concurrent.futures
from subprocess import Popen, PIPE, TimeoutExpired

from endpoints import wait_until_healthy
from utils import ValidationException

# Keep track of all processes started and clean them up
processes = []
cleanup_registered = False


def cleanup_processes():
    # Registered by AtbashRunner constructor
    print("Cleaning processes up before exit...")
    for p in processes:
        if p.poll() is None:
            p.terminate()


class AtbashRunner:

    def __init__(self):
        self.process = None
        global cleanup_registered  # cleanup_registered is not from the class
        if not cleanup_registered:
            cleanup_registered = True
            atexit.register(cleanup_processes)

    def launch_runtime_no_wait(self, user_params=None, time_out=10):
        params = ["java", "-jar", "atbash-runtime/atbash-runtime.jar"]
        if user_params is not None:
            params.extend(user_params)

        # Run a command
        process = Popen(params, stdout=PIPE, stderr=PIPE)
        processes.append(process)

        # Wait for the process to terminate
        try:
            out, err = process.communicate(timeout=time_out)

        except TimeoutExpired:
            process.kill()
            out, err = process.communicate()

        return out.decode() + err.decode()

    def launch_runtime(self, user_params=None, jvm_params=None, port=8080):
        params = ["java"]
        if jvm_params is not None:
            params.extend(jvm_params)
        params.extend(["-jar", "atbash-runtime/atbash-runtime.jar"])
        if user_params is not None:
            params.extend(user_params)

        # Run a command
        process = Popen(params, stdout=PIPE, stderr=PIPE)
        processes.append(process)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(wait_until_healthy, "http://localhost:" + str(port) + "/health")
            healthy = future.result()

        if not healthy:
            process.kill()
            print(process.communicate())
            raise ValidationException("Runtime not healthy within 10 seconds")
        self.process = process

    def end_process(self):
        self.process.terminate()
        out, err = self.process.communicate()

        return err.decode()

    def execute_cli(self, user_params, time_out=10):
        params = ["java", "-jar", "atbash-cli.jar"]
        params.extend(user_params)
        # Run a command
        process = Popen(params, stdout=PIPE, stderr=PIPE)
        processes.append(process)
        # Wait for the process to terminate
        try:
            out, err = process.communicate(timeout=time_out)

        except TimeoutExpired:
            process.kill()
            out, err = process.communicate()

        return out.decode() + err.decode()


def execute_command(command_params, time_out=10):
    # Run a command
    process = Popen(command_params, stdout=PIPE, stderr=PIPE)
    processes.append(process)

    # Wait for the process to terminate
    try:
        out, err = process.communicate(timeout=time_out)

    except TimeoutExpired:
        process.kill()
        out, err = process.communicate()

    return out.decode() + err.decode()