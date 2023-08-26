from easy_expectations.fs_component_extractor.base_fs_component_extractor import (
    FileSystemComponentExtractor,
)


class S3GCSFileSystemComponentExtractor(FileSystemComponentExtractor):
    """
    This class extends the FileSystemComponentExtractor class and provides
    methods to extract components from S3/GCS filesystem paths.
    """

    @property
    def bucket(self) -> str:
        """
        Get the bucket name associated with the path.

        Returns:
            str: The name of the bucket.
        """
        return self.path.split("/")[0]

    @property
    def prefix(self) -> str:
        """
        Returns the prefix of the given path.

        The prefix is determined by excluding the last part of the path if it
        has a file extension, and including all other parts.

        Returns:
            str: The prefix of the path.
        """
        parts = self.path.split("/")
        prefix_parts = []

        if "*" in self.path:
            for part in parts[1:]:
                if "*" in part:
                    break
                prefix_parts.append(part)
        else:
            # Check if the last part has a file extension
            last_part = parts[-1]
            if "." in last_part and last_part.rsplit(".", 1)[1]:
                # If it does, exclude it from the prefix
                prefix_parts = parts[1:-1]
            else:
                # Otherwise, include it in the prefix
                prefix_parts = parts[1:]

        return "/".join(prefix_parts) if prefix_parts else ""
        # parts = self.path.split("/")[1:]
        # if "*" in self.path:
        #     for i, part in enumerate(parts):
        #         if "*" in part:
        #             break
        #     else:
        #         i = len(parts)
        # else:
        #     last_part = parts[-1]
        #     if "." in last_part and last_part.rsplit(".", 1)[1]:
        #         i = len(parts) - 1
        #     else:
        #         i = len(parts)
        # return "/".join(parts[:i])

    def components(self) -> dict:
        """
        Extracts various components from a given path and returns them as a
        dictionary.

        Returns:
            dict: A dictionary containing the following components:
                - "bucket": The name of the bucket.
                - "prefix": The prefix of the path.
                - "pattern": The file pattern.
                - "filename": The filename.
        """
        return {
            "bucket": self.bucket,
            "prefix": self.prefix,
            "pattern": self.file_pattern(),
            "filename": self.filename(),
        }
