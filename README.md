# Atbash Runtime Automated Testing


In addition to the tests within the repository https://github.com/atbashEE/runtime-samples, this repo contains additional automated tests using Python.

The runtime-samples repository contains tests where the endpoints of an application are tested and verified if the expected functionality works.

This repository contains tests about the configuration, expected log file content, and integration with JMX and Flight recorder for example. They require that the Atbash Runtime is started with different parameters. Hence, an approach using python scripts that launch the process with various parameters and verify the expected results and behaviour is followed (mainly to have a goal for my learning of Python 3)


## Content

Java directory contains some support artifacts.

- logging: WAR file that can produce (a lot if needed) entries in the log file.
