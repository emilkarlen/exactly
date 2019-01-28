import pathlib
from typing import Iterator, Optional

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.data.file_ref_resolver_impls.file_ref_with_symbol import StackedFileRef
from exactly_lib.symbol.logic.files_matcher import ErrorMessageInfo, FileModel, FilesMatcherModel
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_utils.err_msg import path_description
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher, file_matchers
from exactly_lib.test_case_utils.file_matcher.file_matcher_models import FileMatcherModelForPrimitivePath
from exactly_lib.test_case_utils.file_matcher.file_matcher_values import FileMatcherAndValue, MATCH_EVERY_FILE_VALUE
from exactly_lib.type_system.data import file_refs
from exactly_lib.type_system.data.file_ref import FileRef
from exactly_lib.type_system.error_message import PropertyDescriptor
from exactly_lib.type_system.logic.file_matcher import FileMatcherValue
from exactly_lib.util.file_utils import TmpDirFileSpace


class FileModelForDir(FileModel):
    def __init__(self,
                 path: pathlib.Path,
                 root_dir_path: pathlib.Path,
                 root_dir_path_value: FileRef):
        self._path = path
        self._root_dir_path = root_dir_path
        self._root_dir_path_value = root_dir_path_value

    @property
    def path(self) -> pathlib.Path:
        return self._path

    @property
    def relative_to_root_dir(self) -> pathlib.Path:
        return self.path.relative_to(self._root_dir_path)

    @property
    def relative_to_root_dir_as_path_value(self) -> FileRef:
        return StackedFileRef(self._root_dir_path_value,
                              file_refs.constant_path_part(str(self.relative_to_root_dir)))


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

    @property
    def dir_path_resolver(self) -> FileRefResolver:
        return self._dir_path_resolver

    def files(self) -> Iterator[FileModel]:
        dir_path_to_check_value = self._dir_path_resolver.resolve(self._environment.symbols)
        dir_path_to_check = dir_path_to_check_value.value_of_any_dependency(self._environment.home_and_sds)

        def mk_model(path: pathlib.Path) -> FileModel:
            return FileModelForDir(path, dir_path_to_check, dir_path_to_check_value)

        assert isinstance(dir_path_to_check, pathlib.Path), 'Resolved value should be a path'

        file_paths = dir_path_to_check.iterdir()

        if self._files_selection is not None:
            file_matcher_model = FileMatcherModelForPrimitivePath(self._tmp_file_space, dir_path_to_check)
            file_matcher = self._files_selection.value_of_any_dependency(self._environment.home_and_sds)
            file_paths = file_matchers.matching_files_in_dir(file_matcher, file_matcher_model)

        return map(mk_model, file_paths)


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
