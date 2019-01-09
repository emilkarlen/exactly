import pathlib
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Set, Optional

from exactly_lib.test_case_file_structure.dir_dependent_value import MultiDirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.error_message import FilePropertyDescriptorConstructor, ErrorMessageResolver
from exactly_lib.type_system.logic.matcher_base_class import Matcher
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.file_utils import ensure_parent_directory_does_exist, TmpDirFileSpace


class DestinationFilePathGetter:
    """
    Gets a file name that can be used for storing intermediate file contents.
    """

    def __init__(self):
        self._existing_unique_instruction_dir = None

    def get(self,
            tmp_file_space: TmpDirFileSpace,
            src_file_path: pathlib.Path) -> pathlib.Path:
        """
        :return: Path of a non-existing file.
        """
        if not self._existing_unique_instruction_dir:
            self._existing_unique_instruction_dir = tmp_file_space.new_path_as_existing_dir()
        dst_file_base_name = src_file_path.name
        return self._existing_unique_instruction_dir / dst_file_base_name


class FileToCheck:
    """
    Access to the file to check, with functionality designed to
    help assertions on the contents of the file.
    """

    def __init__(self,
                 original_file_path: pathlib.Path,
                 checked_file_describer: FilePropertyDescriptorConstructor,
                 tmp_file_space: TmpDirFileSpace,
                 string_transformer: StringTransformer,
                 destination_file_path_getter: DestinationFilePathGetter):
        self._original_file_path = original_file_path
        self._checked_file_describer = checked_file_describer
        self._tmp_file_space = tmp_file_space
        self._transformed_file_path = None
        self._string_transformer = string_transformer
        self._destination_file_path_getter = destination_file_path_getter

    def with_transformation(self, string_transformer: StringTransformer):
        return FileToCheck(self._original_file_path,
                           self._checked_file_describer,
                           self._tmp_file_space,
                           string_transformer,
                           self._destination_file_path_getter)

    @property
    def string_transformer(self) -> StringTransformer:
        return self._string_transformer

    @property
    def tmp_file_space(self) -> TmpDirFileSpace:
        return self._tmp_file_space

    @property
    def describer(self) -> FilePropertyDescriptorConstructor:
        return self._checked_file_describer

    @property
    def original_file_path(self) -> pathlib.Path:
        return self._original_file_path

    def transformed_file_path(self) -> pathlib.Path:
        """
        Gives a path to a file with contents that has been transformed using the transformer.
        """
        if self._transformed_file_path is not None:
            return self._transformed_file_path
        if self._string_transformer.is_identity_transformer:
            self._transformed_file_path = self._original_file_path
            return self._transformed_file_path
        self._transformed_file_path = self._destination_file_path_getter.get(self._tmp_file_space,
                                                                             self._original_file_path)
        ensure_parent_directory_does_exist(self._transformed_file_path)
        self._write_transformed_contents()
        return self._transformed_file_path

    @contextmanager
    def lines(self) -> iter:
        """
        Gives the lines of the file contents to check.

        Lines are generated each time this method is called,
        so if it is needed to iterate over them multiple times,
        it might be better to store the result in a file,
        using transformed_file_path.
        """
        with self._original_file_path.open() as f:
            if self._string_transformer.is_identity_transformer:
                yield f
            else:
                yield self._string_transformer.transform(f)

    def _write_transformed_contents(self):
        with self._transformed_file_path.open('w') as dst_file:
            with self.lines() as lines:
                for line in lines:
                    dst_file.write(line)


class StringMatcher(Matcher[FileToCheck], ABC):
    @abstractmethod
    def matches(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        """
        :raises HardErrorException: In case of HARD ERROR
        :return: None iff match
        """
        raise NotImplementedError('abstract method')


class StringMatcherValue(MultiDirDependentValue[StringMatcher]):
    def resolving_dependencies(self) -> Set[DirectoryStructurePartition]:
        return set()

    def value_when_no_dir_dependencies(self) -> StringMatcher:
        """
        :raises DirDependencyError: This value has dir dependencies.
        """
        raise ValueError(str(type(self)) + ' do not support this short cut.')

    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringMatcher:
        """Gives the value, regardless of actual dependency."""
        raise NotImplementedError()
