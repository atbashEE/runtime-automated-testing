
class ValidationException(Exception):

    def __init__(self, message):
        super().__init__(message)


def jmx_config():
    return ["-Dcom.sun.management.jmxremote.port=8765", "-Dcom.sun.management.jmxremote.authenticate=false", "-Dcom.sun.management.jmxremote.ssl=false"]