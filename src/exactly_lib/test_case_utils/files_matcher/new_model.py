import pathlib
from abc import ABC, abstractmethod
from typing import Iterator

from exactly_lib.type_system.error_message import PropertyDescriptor


class ErrorMessageInfo(ABC):
    @abstractmethod
    def property_descriptor(self, property_name: str) -> PropertyDescriptor:
        pass


class FileModel:
    def __init__(self,
                 path: pathlib.Path,
                 root_dir_path: pathlib.Path):
        self.path = path
        self._root_dir_path = root_dir_path

    def relative_to_root_dir(self) -> pathlib.Path:
        return self.path.relative_to(self._root_dir_path)


class FilesMatcherModel(ABC):
    @property
    @abstractmethod
    def error_message_info(self) -> ErrorMessageInfo:
        pass

    @abstractmethod
    def files(self) -> Iterator[FileModel]:
        pass
