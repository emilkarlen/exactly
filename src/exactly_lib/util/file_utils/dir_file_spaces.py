import os
import pathlib
from typing import Iterator, Optional

from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.str_ import sequences


class FileNamesConfig:
    def __init__(self,
                 suffix_separator: str,
                 root_file_names: Iterator[str],
                 sub_space_file_names: Iterator[Iterator[str]],
                 ):
        self._suffix_separator = suffix_separator
        self._root_file_names = root_file_names
        self._sub_space_file_names = sub_space_file_names

    @property
    def suffix_separator(self) -> str:
        """
        :return: A string that precedes the name suffix, if one is given.
        """
        return self._suffix_separator

    @property
    def root_file_names(self) -> Iterator[str]:
        """
        :return: Gives a sequence of different file names used for files in the root space.
        Must be long enough to supply a name for every requested path.
        """
        return self._root_file_names

    @property
    def sub_space_file_names(self) -> Iterator[Iterator[str]]:
        """
        :return: Gives names for every sub space created. Must be long enough
        to supply an iterator of names for every sub space.
        """
        return self._sub_space_file_names


class DirFileSpaceAsDirCreatedOnDemand(DirFileSpace):
    """
    A tmp file space that is a dir that (probably) do not exist,
    but is created when tmp files are demanded.
    """

    def __init__(self,
                 root_dir_to_create_on_demand: pathlib.Path,
                 file_names_config: FileNamesConfig,
                 ):
        """
        :param root_dir_to_create_on_demand: Either must not exist, or must be an existing empty dir
        If it does not exit, it must be possible to create it as a dir
        (i.e no path components may be a file, and must be writable).
        """
        self._file_names = file_names_config
        self._root_dir_to_create_on_demand = root_dir_to_create_on_demand
        self._existing_root_dir_path = None

    def new_path(self, name_suffix: Optional[str] = None) -> pathlib.Path:
        return self._root_dir() / self._next_base_name(name_suffix)

    def new_path_as_existing_dir(self, name_suffix: Optional[str] = None) -> pathlib.Path:
        ret_val = self.new_path(name_suffix)
        ret_val.mkdir()
        return ret_val

    def sub_dir_space(self, name_suffix: Optional[str] = None) -> DirFileSpace:
        return DirFileSpaceAsDirCreatedOnDemand(
            self.new_path(name_suffix),
            FileNamesConfig(self._file_names.suffix_separator,
                            next(self._file_names.sub_space_file_names),
                            self._file_names.sub_space_file_names,
                            ),
        )

    def _root_dir(self) -> pathlib.Path:
        if self._existing_root_dir_path is None:
            self._existing_root_dir_path = self._root_dir_to_create_on_demand
            self._existing_root_dir_path.mkdir(parents=True,
                                               exist_ok=True)
        return self._existing_root_dir_path

    def _next_base_name(self, name_suffix: Optional[str] = None) -> str:
        ret_val = next(self._file_names.root_file_names)
        if name_suffix is not None:
            name_suffix = name_suffix.replace(os.sep, '_')
            ret_val = ''.join((ret_val, self._file_names.suffix_separator, name_suffix))
        return ret_val


class DirFileSpaceThatMustNoBeUsed(DirFileSpace):
    def __init__(self, msg_header: str = ''):
        self._msg_header = msg_header

    def new_path(self, name_suffix: Optional[str] = None) -> pathlib.Path:
        raise ValueError(self._msg_header + ': must not be used')

    def new_path_as_existing_dir(self, name_suffix: Optional[str] = None) -> pathlib.Path:
        raise ValueError(self._msg_header + ': must not be used')

    def sub_dir_space(self, name_suffix: Optional[str] = None) -> DirFileSpace:
        raise ValueError(self._msg_header + ': must not be used')


class DirFileSpaceThatDoNotCreateFiles(DirFileSpace):
    def __init__(self, root_dir: pathlib.Path):
        self._root_dir = root_dir
        self._path_name_sequence = sequences.int_strings(1, 2)

    def new_path(self, name_suffix: Optional[str] = None) -> pathlib.Path:
        return self._root_dir / next(self._path_name_sequence)

    def new_path_as_existing_dir(self, name_suffix: Optional[str] = None) -> pathlib.Path:
        raise ValueError('must not be used')

    def sub_dir_space(self, name_suffix: Optional[str] = None) -> DirFileSpace:
        return DirFileSpaceThatDoNotCreateFiles(self.new_path())
