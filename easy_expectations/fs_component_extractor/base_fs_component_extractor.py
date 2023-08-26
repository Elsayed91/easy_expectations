import os
import re
from abc import ABC, abstractmethod


class FileSystemComponentExtractor(ABC):
    """
    This class extracts components from a file system path.
    """

    def __init__(self, path: str):
        self.path = re.sub(r"^(local:|s3://|gs://)", "", path)
        self.contains_wildcard = "*" in self.path

    def base_dir(self):
        """
        Returns the base directory of the path.

        If the path contains a wildcard character (*), it splits the path by
        the first occurrence of * and returns the directory of the split part.
        If the path does not contain a wildcard character but contains a
        forward slash (/), it returns the directory of the path.
        If the path does not contain a wildcard character or a forward slash,
        it returns the path itself.
        """
        if self.contains_wildcard:
            return os.path.dirname(self.path.split("*")[0])
        elif "/" in self.path:
            # Check if the last part has a file extension
            if "." not in os.path.basename(self.path):
                return self.path
            else:
                return os.path.dirname(self.path)
        else:
            # Return the absolute path of the current working directory
            return os.path.abspath(os.getcwd())

    def file_pattern(self):
        """
        Returns a regular expression pattern that matches the files in the path.

        If the path contains a wildcard character (*), it splits the path by
        forward slashes (/) and translates each component into a regular
        expression pattern using the fnmatch.translate() function.
        The translated patterns are then joined with forward slashes and
        enclosed within ^ and $ to create a regular expression pattern.
        If the path does not contain a wildcard character, it returns (.*)
        which matches any string.
        """
        # if self.contains_wildcard:
        #     components = self.path.split("/")
        #     regex_components = [
        #         fnmatch.translate(component)[4:-3]
        #         for component in components
        #         if "*" in component
        #     ]
        #     return "^" + "/".join(regex_components) + "$"
        # else:
        #     return "(.*)"

        if not self.contains_wildcard:
            return "(.*)"

        wild_path = self.path.split("*", 1)[1]
        if wild_path:
            return "^.*" + re.escape(wild_path) + "$"
        else:
            return "^.*$"

    def filename(self):
        """
        Returns the filename from the path.

        If the path does not contain a wildcard character (*), it extracts the
        filename using the os.path.basename() function.
        It then checks if the filename has a valid extension by splitting it at
        the last occurrence of . and checking if the second part exists.
        If the filename has a valid extension, it returns the filename.
        Otherwise, it returns None.
        """
        if not self.contains_wildcard:
            filename = os.path.basename(self.path)
            # Check if the filename has a valid extension
            if "." in filename and filename.rsplit(".", 1)[1]:
                return filename
        return None

    @abstractmethod
    def components(self):
        pass
