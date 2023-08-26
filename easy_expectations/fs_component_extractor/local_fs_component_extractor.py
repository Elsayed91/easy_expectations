import os

from easy_expectations.fs_component_extractor.base_fs_component_extractor import (
    FileSystemComponentExtractor,
)


class LocalFileSystemComponentExtractor(FileSystemComponentExtractor):
    """
    A class for extracting components from a local file system path.
    This also works for databricks filesystem.
    This class is a subclass of the FileSystemComponentExtractor class.
    It provides methods to extract components such as the base directory,
    file pattern, and filename from a local file system path.
    ```
    """

    def to_absolute_path(self, path):
        """Convert a relative path to an absolute path by prepending the
        current working directory."""
        if not path.startswith("/"):
            return os.path.join(os.getcwd(), path)
        return path

    def components(self):
        """
        Extracts the components from the file system path.

        Returns:
        A dictionary containing the base directory, file pattern, and filename
        extracted from the file system path.
        """
        base_directory = self.to_absolute_path(self.base_dir())
        return {
            "base_dir": base_directory,
            "pattern": self.file_pattern(),
            "filename": self.filename(),
        }
