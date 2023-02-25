import os.path
from datetime import datetime
from os import path
import shutil


def write(file_name: str, content: str):
    """
    Writes the content to the indicated file. In case of an error, a message is written to the console.
    :param file_name: file to write to.
    :param content: The content of the file.
    """
    try:
        with open(file_name, 'w') as file:
            file.write(content)
    except IOError:
        print("An error occurred while writing to the file %s." % file_name)


def exists_file(file_name: str) -> bool:
    """
    Is the file_name a file?
    :param file_name: file name to test.
    :return: true when it is file, false otherwise.
    """
    return path.isfile(file_name)


def get_all_files(directory: str) -> list:
    """
    Return all files in the directory and subdirectory. Return absolute file names.
    :param directory: directory to search for files.
    :return: list with all files within directory.
    """
    result = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for file in filenames:
            result.append(os.path.join(dirpath, file))
    return result


def get_new_files(old_files: list, new_files: list) -> list:
    """
    Determines the new items in the list. Every item present in new_files but not in old_files is returned.
    :param old_files: The old items list
    :param new_files: The new items list
    :return: list if items found in new list but not in old list.
    """
    return [x for x in new_files if x not in old_files and not x.startswith("__py")]


def extract_log_files(files: list, domain: str = "default", base: str = "runtime"):
    """
    Defines the log files, items within directory log and extension .log.
    :param files: List of all files.
    :param domain: The domain entry, 'default' is the default value.
    :param base: The base name of the file, 'runtime' is the default value.
    :return: List of files matching the parameters and extension.
    """
    match = "./" + domain + "/logs/" + base + ".log"
    return [x for x in files if x.startswith(match)]


def remove_directory(directory: str):
    """
    Recursive deletes the directory. Warning this can be very dangerous, make sure you double-check the directory you
    pass to this function.
    :param directory: directory that needs to be deletd
    """
    shutil.rmtree(directory)


def sort_log_file_names(file_names: list) -> list:
    """
    Purpose: Sort a list of log file names into two groups: the most recent log files, and the archived log files sorted in descending order by date.
    Notes: The date format used in the archived log file names must be as indicated within the param description.
    :param file_names: list of file names. Names must be in the format of "*.log" for the most recent log files or "file_name_YYYY-MM-DDTHH-MM-SS" for archived log files.
    :return: List of file names that are sorted in the following order: the most recent log files, followed by the archived log files sorted in descending order by date.
    """
    date_fmt = "%Y-%m-%dT%H-%M-%S"
    result = []
    archived_files = {}
    for name in file_names:
        if name.endswith(".log"):
            result.append(name)  # No time indication means it is the most recent
        else:
            key = datetime.strptime(name[-19:], date_fmt)
            archived_files[key] = name
    sorted_keys = list(archived_files.keys())
    sorted_keys.sort(reverse=True)
    for k in sorted_keys:
        result.append(archived_files[k])
    return result


def get_jfr_files(directory: str) -> list:
    """
    Search all files with extension '.jfr' in the directory specified as parameter or in any sub-directory.
    :param directory: Directory to search for JFR dump files
    :return: JFR Files found in the directory.
    """
    result = []
    for dirpath, dirnames, filenames in os.walk(directory):
        for file in filenames:
            if file.endswith(".jfr"):
                result.append(os.path.join(dirpath, file))
    return result
