import pathlib
from contextlib import contextmanager
from typing import ContextManager, Iterator

from exactly_lib.type_system.data.path_ddv import DescribedPath
from exactly_lib.type_system.logic.string_matcher import StringMatcherModel
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


class StringMatcherModelFromFile(StringMatcherModel):
    def __init__(self,
                 original_file_path: DescribedPath,
                 string_transformer: StringTransformer,
                 tmp_file_for_transformed_getter: DestinationFilePathGetter):
        self._original_file_path = original_file_path
        self._transformed_file_path = None
        self._string_transformer = string_transformer
        self._tmp_file_for_transformed_getter = tmp_file_for_transformed_getter

    def with_transformation(self, string_transformer: StringTransformer) -> StringMatcherModel:
        return StringMatcherModelFromFile(self._original_file_path,
                                          string_transformer,
                                          self._tmp_file_for_transformed_getter)

    @property
    def string_transformer(self) -> StringTransformer:
        return self._string_transformer

    def transformed_file_path(self, tmp_file_space: TmpDirFileSpace) -> pathlib.Path:
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
    def lines(self) -> ContextManager[Iterator[str]]:
        with self._original_file_path.primitive.open() as f:
            if self._string_transformer.is_identity_transformer:
                yield f.readlines()
            else:
                yield self._string_transformer.transform(f)

    def _write_transformed_contents(self):
        with self._transformed_file_path.open('w') as dst_file:
            with self.lines() as lines:
                for line in lines:
                    dst_file.write(line)
