# Atbash Runtime Automated Testing


In addition to the tests within the repository https://github.com/atbashEE/runtime-samples, this repo contains additional automated tests using Python.

The runtime-samples repository contains tests where the endpoints of an application are tested and verified if the expected functionality works.

This repository contains tests about the configuration, expected log file content, and integration with JMX and Flight recorder for example. They require that the Atbash Runtime is started with different parameters. Hence, an approach using python scripts that launch the process with various parameters and verify the expected results and behaviour is followed (mainly to have a goal for my learning of Python 3)


## Content

Java directory contains some support artifacts.

- logging: WAR file that can produce (a lot if needed) entries in the log file.
- AtbashJFRDump : A program that filters out the "be.atbash.runtime.event" Flight record events from a dump file and outputs them as a JSON.


Python directory contains the scripts for the test scenarios.

Directory `ext` contains a few files used by the scripts and the program `jmxterm-1.0.2-uber.jar` downloaded from https://docs.cyclopsgroup.org/jmxterm.

The directory `scripts` contains the shell scripts to prepare the environment for testing.

## Setup

To set up the environment for running all testing scenarios, perform the following steps.

- Download the contents of the repo within a directory, called `TESTING_HOME` in the rest of this document.
- Perform a `man clean package` within the _logging_ and _AtbashJFRDump_ dirctories so that the java artefacts are prepared.
- Configure the script by defining all the required files within the file `config.sh`, including the Atbash Runtime Zip distribution, the Atbash Runtime CLI and a demo which are all available from some download area or created by the main https://github.com/atbashEE/runtime repository.
- Open a console with `<TESTING_HOME>/scripts` as working directory.
- Execute the `prepare_work.sh` script
- The end of the installation script shows the command to switch to the work directory that is prepared and start the virtual environment of Python.
- With the script `all_scenarios.sh', all scenarios are tested, and takes about 5 minutes.