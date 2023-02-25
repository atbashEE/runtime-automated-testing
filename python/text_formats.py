import pyparsing
from pyparsing import *
from pyparsing.core import _SingleCharLiteral

from json_utils import parse_json
from utils import ValidationException


class LogFormat:
    def is_first_line(self, line):
        pass

    def parse_lines(self, lines):
        pass


class FormatSimple(LogFormat):

    def __init__(self):
        self.month_name_abbr = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                                "Sep": 9, "Oct": 10,
                                "Nov": 11, "Dec": 12}
        self.line1 = self.define_format_line1(self.month_name_abbr)
        self.line2 = self.define_format_line2()

    def define_format_line1(self, month_name_abbr):
        # Define the month name
        month_name = oneOf(list(month_name_abbr.keys()), caseless=True)

        # Define the day of the month
        day = Word(nums)

        # Define the year
        year = Word(nums)

        # Define the hour
        hour = Word(nums)

        # Define the minute
        minute = Word(nums)

        # Define the second
        second = Word(nums)

        # Define the AM/PM indicator
        am_pm = oneOf("AM PM", caseless=True)

        # Define the dateTime format
        datetime = month_name + day + "," + year + hour + ":" + minute + ":" + second + am_pm

        # Define Class name
        class_name = Word(alphanums + ".$").setResultsName("className")
        method_name = Word(alphanums + "<>$").setResultsName("methodName")

        return datetime + class_name + method_name

    def define_format_line2(self):
        # Define severity
        severity = oneOf(list(["INFO", "WARNING", "ERROR", "SEVERE"]), caseless=True).setResultsName("severity")

        # Define the message code
        code = Optional(Word(alphanums + "*-", max=13).setResultsName("messageCode") + _SingleCharLiteral(":"))

        # Define the year
        content = restOfLine.setResultsName("content")

        return severity + ":" + code + content

    def is_first_line(self, line):
        result = False
        for key in self.month_name_abbr:
            if line[:3].casefold() == key.casefold():
                result = True
        return result

    def parse_lines(self, lines):
        result = {}
        result.update(self.line1.parseString(lines[0]).asDict())
        combined = '\n'.join(lines[1:])
        result.update(self.line2.parseString(combined).asDict())
        result["entry"] = lines[0] + "\n" + combined
        return result


class FormatAtbashSimple(LogFormat):

    def __init__(self):
        self.month_name_abbr = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
                                "Sep": 9, "Oct": 10,
                                "Nov": 11, "Dec": 12}
        self.line = self.define_format_line(self.month_name_abbr)

    def define_format_line(self, month_name_abbr):
        # Define the month name
        month_name = oneOf(list(month_name_abbr.keys()), caseless=True)

        # Define the day of the month
        day = Word(nums)

        # Define the year
        year = Word(nums)

        # Define the hour
        hour = Word(nums)

        # Define the minute
        minute = Word(nums)

        # Define the second
        second = Word(nums)

        # Define the dateTime format
        datetime = month_name + day + "," + year + hour + ":" + minute + ":" + second

        # Define Class name
        class_name = Word(alphanums + ".$").setResultsName("className")
        method_name = Word(alphanums + "<>$").setResultsName("methodName")

        # Define severity
        severity = oneOf(list(["FINEST", "INFO", "WARNING", "ERROR", "SEVERE"]), caseless=True).setResultsName(
            "severity")

        # Define the message code
        code = Optional(Word(alphanums + "*-", max=9).setResultsName("messageCode") + _SingleCharLiteral(":"))

        # Define the year
        content = restOfLine.setResultsName("content")

        return datetime + class_name + "#" + method_name + severity + ":" + code + content

    def is_first_line(self, line):
        result = False
        for key in self.month_name_abbr:
            if line[:3].casefold() == key.casefold():
                result = True
        return result

    def parse_lines(self, lines):
        result = {}
        combined = '\n'.join(lines[:])
        try:
            result.update(self.line.parseString(combined).asDict())
            result["entry"] = lines[0] + "\n" + combined
        except pyparsing.exceptions.ParseException:
            print("Problem with parsing %s" % combined)
            raise
        return result


class FormatUniformWithAnsi(LogFormat):

    def __init__(self):
        self.line = self.__define_format_line()

    def __define_format_line(self):
        date_time = Combine(Word(nums, exact=4) + "-" + Word(nums, exact=2) + "-" + Word(nums, exact=2) + "T" +
                            Word(nums, exact=2) + ":" + Word(nums, exact=2) + ":" + Word(nums, exact=2) + "." +
                            Word(nums, exact=3) + "+" + Word(nums, max=4))

        severity = oneOf(list(["INFO", "WARNING", "ERROR", "SEVERE"]), caseless=True).setResultsName("severity")
        class_name = Word(alphanums + ".$").setResultsName("className")
        thread_id = Combine(Literal("_ThreadID=") + Word(nums))
        thread_name = Combine(Literal("_ThreadName=") + Word(alphanums + "-"))
        time_millis = Combine(Literal("_TimeMillis=") + Word(nums))
        level_value = Combine(Literal("_LevelValue=") + Word(nums))
        content = restOfLine.setResultsName("content")

        return "[#|" + date_time + "\x1b[1;92m|" + severity + "|\x1b[0m\x1b[1;94m" + class_name + "|\x1b[0m" + thread_id + ";" \
            + thread_name + ";" + time_millis + ";" + level_value + ";|" + content

    def is_first_line(self, line):
        return line[:3] == "[#|"

    def parse_lines(self, lines):
        result = {}
        combined = '\n'.join(lines[:])
        try:
            result.update(self.line.parseString(combined).asDict())
            result["entry"] = lines[0] + "\n" + combined
        except pyparsing.exceptions.ParseException:
            print("Problem with parsing %s" % combined)
            raise
        return result


class FormatJSON(LogFormat):

    def __init__(self):
        self.message_content = self.__define_message_content_format()

    def __define_message_content_format(self):
        code = Optional(Word(alphanums + "*-", max=9).setResultsName("messageCode") + _SingleCharLiteral(":"))

        # Define the year
        content = restOfLine.setResultsName("content")
        return code + content

    def is_first_line(self, line):
        # Our JSON log entries are on 1 line. So each line is the first line. But for safety, check if it starts with '{'
        return line.startswith('{')

    def __ensure_key(self, dict, old_key, new_key):
        if old_key in dict.keys():
            dict[new_key] = dict[old_key]
            del dict[old_key]
        else:
            dict[new_key] = ""

    def parse_lines(self, lines):
        result = {}
        combined = '\n'.join(lines[:])  # to be on the safe side
        json = parse_json(combined)
        result.update(json)
        if "LogMessage" in json.keys():
            parsed = self.message_content.parseString(json["LogMessage"]).asDict()
            result.update(parsed)
        else:
            result["content"] = ""  # Elsewhere we expect this key

        self.__ensure_key(result, "Level", "severity")
        self.__ensure_key(result, "MethodName", "methodName")
        self.__ensure_key(result, "ClassName", "className")

        return result


def parse_jmx_application_output(output):
    lbrack = Suppress("[")
    rbrack = Suppress("]")
    semi = Suppress(";")
    equals = Suppress("=")

    word = Word(alphas)
    value = Word(alphanums + "/-,")

    key_value = Group(word.setResultsName("key") + equals + value.setResultsName("value")) + semi
    property_ = OneOrMore(key_value)
    application = Group(Suppress("{") + property_ + Suppress("}"))
    applications = OneOrMore(application + Optional(semi))
    running_apps = Keyword("RunningApplications") + equals + Group(lbrack + applications + rbrack)

    parsed = running_apps.parseString(output)
    result = []
    for app in parsed[1]:
        appData = {}
        for idx in range(0, len(app)):
            appData[app[idx].key] = app[idx].value
        if set(appData.keys()) != {"Name", "ContextRoot", "Specifications"}:
            print("Entry that was not having the expected 3 keys")
            print(app)
            raise ValidationException("The JMX bean value did not have the expected names")
        result.append(appData)

    return result


class PrometheusMetrics:

    def __init__(self):
        self.expression_count = self.__define_expression_count()
        self.expression_quantile = self.__define_expression_quantile()

    def __define_expression_quantile(self):
        application = Word(alphanums + "_-")
        endpoint = Word(alphanums+"_- /{}*")
        quantile = Word(nums + ".")
        integer = Word(nums)

        return (Suppress("application_response_time_seconds{application=\"") +
                  application("application") + Suppress("\",endpoint=\"") +
                  endpoint("endpoint") + Suppress("\",quantile=\"") +
                  quantile("quantile") + Suppress("\"}") +
                  integer("value"))

    def __define_expression_count(self):
        application = Word(alphanums + "_-")
        endpoint = Word(alphanums+"_- /{}*")
        integer = Word(nums)

        return (Suppress("application_response_time_seconds_count{application=\"") +
                application("application") + Suppress("\",endpoint=\"") +
                endpoint("endpoint") + Suppress("\"}") +
                integer("count"))

    def parse_count_entry(self, line):
        match = self.expression_count.parseString(line)
        return {"application_name": match.application, "endpoint_name": match.endpoint,
                "count_value": int(match.count)}

    def parse_quantile_entry(self, line):
        match = self.expression_quantile.parseString(line)
        return {"application_name": match.application, "endpoint_name": match.endpoint,
                "quantile_value": float(match.quantile), "value": int(match.value)}
