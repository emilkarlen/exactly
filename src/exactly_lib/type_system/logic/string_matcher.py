import pathlib
from contextlib import contextmanager
from typing import Iterable, ContextManager

from exactly_lib.symbol.logic.matcher import MatcherSdv
from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.matcher_base_class import MatcherDdv, \
    MatcherAdv, MatcherWTrace
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
                 original_file_path: DescribedPath,
                 string_transformer: StringTransformer,
                 tmp_file_for_transformed_getter: DestinationFilePathGetter):
        self._original_file_path = original_file_path
        self._transformed_file_path = None
        self._string_transformer = string_transformer
        self._tmp_file_for_transformed_getter = tmp_file_for_transformed_getter

    def with_transformation(self, string_transformer: StringTransformer) -> 'FileToCheck':
        return FileToCheck(self._original_file_path,
                           string_transformer,
                           self._tmp_file_for_transformed_getter)

    @property
    def string_transformer(self) -> StringTransformer:
        return self._string_transformer

    @property
    def original_file_path(self) -> DescribedPath:
        return self._original_file_path

    def transformed_file_path(self, tmp_file_space: TmpDirFileSpace) -> pathlib.Path:
        """
        Gives a path to a file with contents that has been transformed using the transformer.
        """
        if self._transformed_file_path is not None:
            return self._transformed_file_path
        if self._string_transformer.is_identity_transformer:
            self._transformed_file_path = self._original_file_path.primitive
            return self._transformed_file_path
        self._transformed_file_path = self._tmp_file_for_transformed_getter.get(tmp_file_space,
                                                                                self._original_file_path.primitive)
        ensure_parent_directory_does_exist(self._transformed_file_path)
        self._write_transformed_contents()
        return self._transformed_file_path

    @contextmanager
    def lines(self) -> ContextManager[Iterable[str]]:
        """
        Gives the lines of the file contents to check.

        Lines are generated each time this method is called,
        so if it is needed to iterate over them multiple times,
        it might be better to store the result in a file,
        using transformed_file_path.
        """
        with self._original_file_path.primitive.open() as f:
            if self._string_transformer.is_identity_transformer:
                yield f
            else:
                yield self._string_transformer.transform(f)

    def _write_transformed_contents(self):
        with self._transformed_file_path.open('w') as dst_file:
            with self.lines() as lines:
                for line in lines:
                    dst_file.write(line)


StringMatcher = MatcherWTrace[FileToCheck]

StringMatcherAdv = MatcherAdv[FileToCheck]

StringMatcherDdv = MatcherDdv[FileToCheck]

StringMatcherSdv = MatcherSdv[FileToCheck]
