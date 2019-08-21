import os
import pathlib
from typing import Iterator, Optional

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.logic.files_matcher import ErrorMessageInfo, FileModel, FilesMatcherModel
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_utils.err_msg import path_description
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.err_msg2.described_path import DescribedPathPrimitive
from exactly_lib.test_case_utils.err_msg2.path_impl import described_path_resolvers
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher, file_matchers
from exactly_lib.test_case_utils.file_matcher.file_matcher_values import FileMatcherAndValue, MATCH_EVERY_FILE_VALUE
from exactly_lib.type_system.error_message import PropertyDescriptor
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue
from exactly_lib.util.file_utils import TmpDirFileSpace


class FileModelForDir(FileModel):
    def __init__(self,
                 file_name: str,
                 root_dir: DescribedPathPrimitive):
        self._relative_to_root_dir = pathlib.Path(file_name)
        self._path = root_dir.child(file_name)

    @property
    def path(self) -> DescribedPathPrimitive:
        return self._path

    @property
    def relative_to_root_dir(self) -> pathlib.Path:
        return self._relative_to_root_dir


class FilesMatcherModelForDir(FilesMatcherModel):
    def __init__(self,
                 tmp_file_space: TmpDirFileSpace,
                 dir_path_resolver: FileRefResolver,
                 environment: PathResolvingEnvironmentPreOrPostSds,
                 files_selection: Optional[FileMatcherValue] = None,
                 ):
        self._tmp_file_space = tmp_file_space
        self._dir_path_resolver = dir_path_resolver
        self._files_selection = files_selection
        self._environment = environment

    def sub_set(self, selector: FileMatcherValue) -> FilesMatcherModel:
        new_file_selector = (selector
                             if self._files_selection is None
                             else FileMatcherAndValue([self._files_selection,
                                                       selector])
                             )

        return FilesMatcherModelForDir(self._tmp_file_space,
                                       self._dir_path_resolver,
                                       self._environment,
                                       new_file_selector,
                                       )

    @property
    def error_message_info(self) -> ErrorMessageInfo:
        file_selector = (self._files_selection
                         if self._files_selection is not None
                         else
                         MATCH_EVERY_FILE_VALUE
                         )

        return ErrorMessageInfoForDir(self._dir_path_resolver,
                                      file_selector)

    def files(self) -> Iterator[FileModel]:
        environment = self._environment
        described_value = described_path_resolvers.of(self._dir_path_resolver).resolve(environment.symbols)
        dir_path_to_check = described_value.value_of_any_dependency(environment.home_and_sds)

        def mk_model(file_name: str) -> FileModel:
            return FileModelForDir(file_name, dir_path_to_check)

        if self._files_selection is None:
            return map(mk_model, os.listdir(str(dir_path_to_check.primitive)))
        else:
            file_matcher = self._files_selection.value_of_any_dependency(environment.home_and_sds)
            file_names = file_matchers.matching_files_in_dir(file_matcher,
                                                             self._tmp_file_space,
                                                             dir_path_to_check.primitive)
            return map(mk_model, file_names)


class ErrorMessageInfoForDir(ErrorMessageInfo):
    def __init__(self,
                 dir_path_resolver: FileRefResolver,
                 files_selection: FileMatcherValue):
        self._dir_path_resolver = dir_path_resolver
        self._files_selection = files_selection

    def property_descriptor(self, property_name: str) -> PropertyDescriptor:
        return property_description.PropertyDescriptorWithConstantPropertyName(
            property_name,
            property_description.multiple_object_descriptors([
                path_description.PathValuePartConstructor(self._dir_path_resolver),
                parse_file_matcher.FileSelectionDescriptor(self._files_selection),
            ])
        )
