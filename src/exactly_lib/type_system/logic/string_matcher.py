import pathlib
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Optional, Iterable

from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependentValue
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_utils.description_tree.tree_structured import WithCachedTreeStructureDescriptionBase
from exactly_lib.type_system.data.file_ref import DescribedPathPrimitive
from exactly_lib.type_system.description import trace_renderers
from exactly_lib.type_system.description.trace_building import TraceBuilder
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.err_msg.err_msg_resolver import ErrorMessageResolver
from exactly_lib.type_system.err_msg.prop_descr import FilePropertyDescriptorConstructor
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace, MatchingResult, MatcherValue
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.description_tree import renderers
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
                 original_file_path: DescribedPathPrimitive,
                 checked_file_describer: FilePropertyDescriptorConstructor,
                 tmp_file_space: TmpDirFileSpace,
                 string_transformer: StringTransformer,
                 tmp_file_for_transformed_getter: DestinationFilePathGetter):
        self._original_file_path = original_file_path
        self._checked_file_describer = checked_file_describer
        self._tmp_file_space = tmp_file_space
        self._transformed_file_path = None
        self._string_transformer = string_transformer
        self._tmp_file_for_transformed_getter = tmp_file_for_transformed_getter

    def with_transformation(self, string_transformer: StringTransformer) -> 'FileToCheck':
        return FileToCheck(self._original_file_path,
                           self._checked_file_describer,
                           self._tmp_file_space,
                           string_transformer,
                           self._tmp_file_for_transformed_getter)

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
    def original_file_path(self) -> DescribedPathPrimitive:
        return self._original_file_path

    def transformed_file_path(self) -> pathlib.Path:
        """
        Gives a path to a file with contents that has been transformed using the transformer.
        """
        if self._transformed_file_path is not None:
            return self._transformed_file_path
        if self._string_transformer.is_identity_transformer:
            self._transformed_file_path = self._original_file_path.primitive
            return self._transformed_file_path
        self._transformed_file_path = self._tmp_file_for_transformed_getter.get(self._tmp_file_space,
                                                                                self._original_file_path.primitive)
        ensure_parent_directory_does_exist(self._transformed_file_path)
        self._write_transformed_contents()
        return self._transformed_file_path

    @contextmanager
    def lines(self) -> Iterable[str]:
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


class StringMatcher(WithCachedTreeStructureDescriptionBase,
                    MatcherWTrace[FileToCheck],
                    ABC):

    def _structure(self) -> StructureRenderer:
        return renderers.header_only(self.name)

    @abstractmethod
    def matches_emr(self, model: FileToCheck) -> Optional[ErrorMessageResolver]:
        """
        :raises HardErrorException: In case of HARD ERROR
        :return: None iff match
        """
        pass

    def matches_w_trace(self, model: FileToCheck) -> MatchingResult:
        mb_emr = self.matches_emr(model)

        tb = self._new_tb()

        if mb_emr is None:
            return tb.build_result(True)
        else:
            tb.details.append(
                trace_renderers.DetailsRendererOfErrorMessageResolver(mb_emr))
            return tb.build_result(False)

    def _new_tb(self) -> TraceBuilder:
        return TraceBuilder(self.name)


class StringMatcherValue(DirDependentValue[StringMatcher],
                         MatcherValue[FileToCheck],
                         ABC):
    def structure(self) -> StructureRenderer:
        return renderers.header_only('string-matcher TODO')

    @abstractmethod
    def value_of_any_dependency(self, home_and_sds: HomeAndSds) -> StringMatcher:
        pass
