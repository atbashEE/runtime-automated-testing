import json


def read_json_file(file_name: str) -> dict:
    """
    Reads the content of the file and parses it as a JSON object. The return object is a dictionary.
    :param file_name: File to read
    :return: JSON as dictionary.
    """
    f = open(file_name)
    # returns JSON object as a dictionary
    data = json.load(f)
    f.close()
    return data


def parse_json(text: str) -> dict:
    """
    Returns JSON text parsed as a dictionary
    :param text: string with the JSON
    :return: JSON as dictionary.
    """
    data = json.loads(text)
    return data


def get_value(data: dict, path: list) -> list:
    """
    Return the list of values from the dictionary that math the path. This is a kind on JSON query.
    :param data: dictionary representing JSON object
    :param path: list of strings describing the path for extracting the value.
    :return: List of values extracted from the JSON using the indicated path values.
    """
    current = [data]
    for item in path:
        temp = []
        for instance in current:
            if __is_list(instance):
                temp.append(__all_items(instance, item))
            else:
                temp.append(instance[item])
        current = temp
    return __flatten(current)


def __is_list(var: any) -> bool:
    """
    Tests if the argument is a list.
    :param var: argument to test
    :return: True when argument is a list, false otherwise.
    """
    return type(var) is list


def __all_items(lst: list, name: str) -> list:
    """
    the parameter lst is assumed to be a list of dictionary items.  It returns the value of keys named 'name' within
    the dictionary.
    :param lst: List of Dictionary items
    :param name: Name of dictionary key we are interested in.
    :return: list of matching dictionary values.
    """
    result = []
    for item in lst:
        if __is_list(item):
            print("Seems we have nested lists %s" % lst)
        else:
            result.append(item[name])
    return result


def __flatten(lst: list) -> list:
    """
    Flattens the items in a list. if an item is a list, it unwraps it as individual items.
    :param lst: List of items to process
    :return: list with unwrapped items.
    """
    flat_list = []
    for element in lst:
        if __is_list(element):
            flat_list.extend(__flatten(element))
        else:
            flat_list.append(element)
    return flat_list


def check_json_value(json: dict, path: list, expected: any, error_message: str) -> bool:
    """
    Verifies if the extracted value(s) from the json defined by path, through function get_value, is identical
    to the parameter expected. If the values don't match, the error_message is shown on the console.
    :param json: dictionary representing JSON object
    :param path: list of strings describing the path for extracting the value.
    :param expected: Expected value to be found in JSON.
    :param error_message: Error message shown on console when values don't match.
    :return: return True when values are the same, False otherwise.
    """
    result = True
    actual_value = get_value(json, path)
    if actual_value != expected:
        print(error_message)
        print("Expected %s" % expected)
        print("Actual %s" % actual_value)
        result = False
    return result


def retrieve_application_info(json: dict) -> dict:
    """
    Extract the application info from the JSON retrieved from the list-applications endpoint of the domain mode.
    :param json: dictionary representing JSON object
    :return: dictionary with application info.
    """
    result = {}
    data_ = json["data"]
    for key in data_:
        if not key.startswith("$$") and key != "RC-102":
            result[key] = parse_json(data_[key])
    return result

