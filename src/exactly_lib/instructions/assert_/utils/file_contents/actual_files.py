import pathlib

from exactly_lib.instructions.utils.file_properties import must_exist_as, FileType
from exactly_lib.instructions.utils.file_ref import FileRef
from exactly_lib.instructions.utils.file_ref_check import pre_or_post_sds_failure_message_or_none, FileRefCheck
from exactly_lib.test_case.phases import common as i


class ComparisonActualFile:
    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        """
        :return: None iff there is no failure.
        """
        raise NotImplementedError()

    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        raise NotImplementedError()


class ActComparisonActualFileForFileRef(ComparisonActualFile):
    def __init__(self,
                 file_ref: FileRef):
        self.file_ref = file_ref

    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        return pre_or_post_sds_failure_message_or_none(FileRefCheck(self.file_ref,
                                                                    must_exist_as(FileType.REGULAR)),
                                                       environment.home_and_sds)

    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        return self.file_ref.file_path_pre_or_post_sds(environment.home_and_sds)


class ActComparisonActualFileForStdFileBase(ComparisonActualFile):
    def file_check_failure(self, environment: i.InstructionEnvironmentForPostSdsStep) -> str:
        return None


class StdoutComparisonActualFile(ActComparisonActualFileForStdFileBase):
    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        return environment.sds.result.stdout_file


class StderrComparisonActualFile(ActComparisonActualFileForStdFileBase):
    def file_path(self, environment: i.InstructionEnvironmentForPostSdsStep) -> pathlib.Path:
        return environment.sds.result.stderr_file
