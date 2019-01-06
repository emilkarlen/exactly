import pathlib
from abc import ABC, abstractmethod
from typing import Iterator

from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.error_message import PropertyDescriptor


class ErrorMessageInfo(ABC):
    @abstractmethod
    def property_descriptor(self, property_name: str) -> PropertyDescriptor:
        pass


class FileModel(ABC):
    @property
    @abstractmethod
    def path(self) -> pathlib.Path:
        pass

    @property
    @abstractmethod
    def relative_to_root_dir(self) -> pathlib.Path:
        pass

    @property
    @abstractmethod
    def relative_to_root_dir_as_path_value(self) -> FileRef:
        pass


class FilesMatcherModel(ABC):
    @property
    @abstractmethod
    def error_message_info(self) -> ErrorMessageInfo:
        pass

    @abstractmethod
    def files(self) -> Iterator[FileModel]:
        pass
