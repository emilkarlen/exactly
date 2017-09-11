import pathlib

from exactly_lib.named_element.symbol.path_resolver import FileRefResolver
from exactly_lib.named_element.symbol.value_resolvers.file_ref_resolvers import resolver_of_rel_option
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case_file_structure import sandbox_directory_structure
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_utils.err_msg.path_description import path_value_description
from exactly_lib.test_case_utils.err_msg.property_description import PropertyDescriptor
from exactly_lib.test_case_utils.file_properties import must_exist_as, FileType
from exactly_lib.test_case_utils.file_ref_check import pre_or_post_sds_failure_message_or_none, FileRefCheck
from exactly_lib.type_system.data.concrete_path_parts import PathPartAsFixedPath

_CONTENTS_PROPERTY = 'contents'


class ComparisonActualFile:
    def property_descriptor(self, file_property: str = _CONTENTS_PROPERTY) -> PropertyDescriptor:
        return path_value_description(self.property_name(file_property),
                                      self.file_ref_resolver())

    def property_name(self, file_property: str = _CONTENTS_PROPERTY) -> str:
        return file_property + ' of ' + self.object_name()

    def object_name(self) -> str:
        raise NotImplementedError('abstract method')

    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        """
        :return: None iff there is no failure.
        """
        raise NotImplementedError()

    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        file_ref = self.file_ref_resolver().resolve(environment.symbols)
        return file_ref.value_of_any_dependency(environment.path_resolving_environment_pre_or_post_sds.home_and_sds)

    def file_ref_resolver(self) -> FileRefResolver:
        raise NotImplementedError('abstract method')

    @property
    def references(self) -> list:
        return []


class ActComparisonActualFileForFileRef(ComparisonActualFile):
    def __init__(self,
                 file_ref_resolver: FileRefResolver):
        self._file_ref_resolver = file_ref_resolver

    def object_name(self) -> str:
        return 'file'

    @property
    def references(self) -> list:
        return self._file_ref_resolver.references

    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        return pre_or_post_sds_failure_message_or_none(FileRefCheck(self._file_ref_resolver,
                                                                    must_exist_as(FileType.REGULAR)),
                                                       environment.path_resolving_environment_pre_or_post_sds)

    def file_ref_resolver(self) -> FileRefResolver:
        return self._file_ref_resolver


class ActComparisonActualFileForStdFileBase(ComparisonActualFile):
    def __init__(self, checked_file_name: str):
        self.checked_file_name = checked_file_name

    def object_name(self) -> str:
        return self.checked_file_name

    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        return None

    def file_ref_resolver(self) -> FileRefResolver:
        return resolver_of_rel_option(RelOptionType.REL_RESULT,
                                      PathPartAsFixedPath(self.checked_file_name))


class StdoutComparisonActualFile(ActComparisonActualFileForStdFileBase):
    def __init__(self):
        super().__init__(sandbox_directory_structure.RESULT_FILE__STDOUT)


class StderrComparisonActualFile(ActComparisonActualFileForStdFileBase):
    def __init__(self):
        super().__init__(sandbox_directory_structure.RESULT_FILE__STDERR)
