import pathlib
from typing import Iterator

from exactly_lib.symbol.data.file_ref_resolver import FileRefResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.resolver_structure import FileMatcherResolver
from exactly_lib.test_case_utils.err_msg import path_description
from exactly_lib.test_case_utils.err_msg import property_description
from exactly_lib.test_case_utils.file_matcher import parse_file_matcher
from exactly_lib.test_case_utils.files_matcher.new_model import ErrorMessageInfo, FilesMatcherModel, FileModel
from exactly_lib.type_system.error_message import PropertyDescriptor
from exactly_lib.type_system.logic import file_matcher as file_matcher_type


class FilesMatcherModelForDir(FilesMatcherModel):
    def __init__(self,
                 dir_path_resolver: FileRefResolver,
                 files_selection: FileMatcherResolver,
                 environment: PathResolvingEnvironmentPreOrPostSds):
        self._dir_path_resolver = dir_path_resolver
        self._files_selection = files_selection
        self._environment = environment

    @property
    def error_message_info(self) -> ErrorMessageInfo:
        return ErrorMessageInfoForDir(self._dir_path_resolver,
                                      self._files_selection)

    @property
    def dir_path_resolver(self) -> FileRefResolver:
        return self._dir_path_resolver

    def files(self) -> Iterator[FileModel]:
        dir_path_to_check = self._dir_path_resolver.resolve_value_of_any_dependency(self._environment)

        def mk_model(path: pathlib.Path) -> FileModel:
            return FileModel(path, dir_path_to_check)

        assert isinstance(dir_path_to_check, pathlib.Path), 'Resolved value should be a path'
        file_matcher = self._files_selection.resolve(self._environment.symbols)
        selected_files = file_matcher_type.matching_files_in_dir(file_matcher, dir_path_to_check)
        return map(mk_model, selected_files)


class ErrorMessageInfoForDir(ErrorMessageInfo):
    def __init__(self,
                 dir_path_resolver: FileRefResolver,
                 files_selection: FileMatcherResolver):
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
