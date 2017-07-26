import pathlib

from exactly_lib.symbol.path_resolver import FileRefResolver
from exactly_lib.test_case.phases import common as i
from exactly_lib.test_case_utils.file_properties import must_exist_as, FileType
from exactly_lib.test_case_utils.file_ref_check import pre_or_post_sds_failure_message_or_none, FileRefCheck


class ComparisonActualFile:
    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        """
        :return: None iff there is no failure.
        """
        raise NotImplementedError()

    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        raise NotImplementedError()

    @property
    def symbol_usages(self) -> list:
        return []


class ActComparisonActualFileForFileRef(ComparisonActualFile):
    def __init__(self,
                 file_ref_resolver: FileRefResolver):
        self.file_ref_resolver = file_ref_resolver

    @property
    def symbol_usages(self) -> list:
        return self.file_ref_resolver.references

    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        return pre_or_post_sds_failure_message_or_none(FileRefCheck(self.file_ref_resolver,
                                                                    must_exist_as(FileType.REGULAR)),
                                                       environment.path_resolving_environment_pre_or_post_sds)

    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        file_ref = self.file_ref_resolver.resolve(environment.symbols)
        return file_ref.value_of_any_dependency(environment.path_resolving_environment_pre_or_post_sds.home_and_sds)


class ActComparisonActualFileForStdFileBase(ComparisonActualFile):
    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        return None


class StdoutComparisonActualFile(ActComparisonActualFileForStdFileBase):
    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        return environment.sds.result.stdout_file


class StderrComparisonActualFile(ActComparisonActualFileForStdFileBase):
    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        return environment.sds.result.stderr_file
