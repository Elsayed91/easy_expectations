from easy_expectations.fs_component_extractor.local_fs_component_extractor import (
    LocalFileSystemComponentExtractor,
)
from easy_expectations.fs_component_extractor.s3_gcs_fs_component_extractor import (
    S3GCSFileSystemComponentExtractor,
)


class FileSystemComponentExtractorFactory:
    """
    A factory class that creates an instance of a specific file system
    component extractor based on the file system type provided.
    """

    @staticmethod
    def create_extractor(file_system_type: str, path: str) -> object:
        """
        Create an instance of a file system component extractor based on the
        file system type and path.

        Args:
            file_system_type (str): The type of file system.
            path (str): The file system path.

        Returns:
            object: An instance of the file system component extractor class.

        Raises:
            NotImplementedError: If the file system type is 'azure' (Azure Blob
            Storage is not implemented).
            ValueError: If the file system type is not supported.
        """
        extractor_map = {
            "local": LocalFileSystemComponentExtractor,
            "dbfs": LocalFileSystemComponentExtractor,
            "s3": S3GCSFileSystemComponentExtractor,
            "gcs": S3GCSFileSystemComponentExtractor,
        }

        if file_system_type == "azure":
            raise NotImplementedError(
                "Support for Azure Blob Storage is not yet implemented in this version of the package. "
                "To contribute this functionality, simply provide a functional azure_fs_component extractor.py "
            )

        extractor_class = extractor_map.get(file_system_type)
        if extractor_class is None:
            raise ValueError(f"File system type '{file_system_type}' is not supported.")

        return extractor_class(path)
