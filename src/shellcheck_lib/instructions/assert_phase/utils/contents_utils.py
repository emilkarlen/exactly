import filecmp
import pathlib

from shellcheck_lib.execution.execution_directory_structure import ExecutionDirectoryStructure
from shellcheck_lib.instructions.assert_phase.utils import instruction_utils
from shellcheck_lib.instructions.instruction_parser_for_single_phase import SingleInstructionInvalidArgumentException
from shellcheck_lib.test_case.instruction import common as i
from shellcheck_lib.test_case.instruction.result import pfh
from shellcheck_lib.test_case.instruction.result import svh
from shellcheck_lib.test_case.instruction.sections.assert_ import AssertPhaseInstruction


class ComparisonSource:
    def __init__(self,
                 check_during_validation: bool,
                 file_name: str):
        self.check_during_validation = check_during_validation
        self.file_name = file_name

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        raise NotImplementedError()


class ComparisonSourceForFileRelHome(ComparisonSource):
    def __init__(self, file_name: str):
        super().__init__(True, file_name)

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return global_environment.home_directory / self.file_name


class ComparisonSourceForFileRelCwd(ComparisonSource):
    def __init__(self, file_name: str):
        super().__init__(False, file_name)

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return pathlib.Path(self.file_name)


class ComparisonTarget:
    def __init__(self, do_check_file_properties: bool):
        self.do_check_file_properties = do_check_file_properties

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        raise NotImplementedError()


class ActComparisonTarget(ComparisonTarget):
    def __init__(self,
                 file_name: str):
        super().__init__(True)
        self.file_name = file_name

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return pathlib.Path(self.file_name)


class StdoutComparisonTarget(ComparisonTarget):
    def __init__(self):
        super().__init__(False)

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return global_environment.eds.result.std.stdout_file


class StderrComparisonTarget(ComparisonTarget):
    def __init__(self):
        super().__init__(False)

    def file_path(self, global_environment: i.GlobalEnvironmentForPostEdsPhase) -> pathlib.Path:
        return global_environment.eds.result.std.stderr_file


def check(file_path: pathlib.Path) -> str:
    if not file_path.exists():
        return 'File does not exist: ' + str(file_path)
    if not file_path.is_file():
        return 'Not a regular file: ' + str(file_path)
    return None


class Checker:
    def validate(self,
                 eds: ExecutionDirectoryStructure) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main_check_target_file(self,
                               eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def main_check_comparison_file(self,
                                   eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def target_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def compare(self, eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        raise NotImplementedError()


class CheckerWithFileRelHome(Checker):
    def validate(self,
                 eds: ExecutionDirectoryStructure) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main_check_target_file(self,
                               eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def main_check_comparison_file(self,
                                   eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def target_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def comparison_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def compare(self, eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        target_file_name = str(self.target_file_path(eds))
        comparison_file_name = str(self.comparison_file_path(eds))
        if not filecmp.cmp(target_file_name, comparison_file_name, shallow=False):
            return pfh.new_pfh_fail('Unexpected content in file: ' + target_file_name)


class CheckerForComparisonWithFile(Checker):
    def validate(self,
                 eds: ExecutionDirectoryStructure) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main_check_target_file(self,
                               eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def main_check_comparison_file(self,
                                   eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def target_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def comparison_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def compare(self, eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        target_file_name = str(self.target_file_path(eds))
        comparison_file_name = str(self.comparison_file_path(eds))
        if not filecmp.cmp(target_file_name, comparison_file_name, shallow=False):
            return pfh.new_pfh_fail('Unexpected content in file: ' + target_file_name)


class CheckerForEmptiness(Checker):
    def __init__(self, expect_empty: bool):
        self._expect_empty = expect_empty

    def validate(self,
                 eds: ExecutionDirectoryStructure) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main_check_target_file(self,
                               eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def main_check_comparison_file(self,
                                   eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        return pfh.new_pfh_pass()

    def target_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def comparison_file_path(self, eds: ExecutionDirectoryStructure) -> pathlib.Path:
        raise NotImplementedError()

    def compare(self, eds: ExecutionDirectoryStructure) -> pfh.PassOrFailOrHardError:
        size = self.target_file_path(eds).stat().st_size
        if self._expect_empty:
            if size != 0:
                return pfh.new_pfh_fail('File is not empty: Size (in bytes): ' + str(size))
        else:
            if size == 0:
                return pfh.new_pfh_fail('File is empty')
        return pfh.new_pfh_pass()


class ContentCheckerInstruction(AssertPhaseInstruction):
    def __init__(self,
                 comparison_source: ComparisonSource,
                 comparison_target: ComparisonTarget):
        self.comparison_target = comparison_target
        self._comparison_source = comparison_source

    def validate(self,
                 global_environment: i.GlobalEnvironmentForPostEdsPhase) -> svh.SuccessOrValidationErrorOrHardError:
        if self._comparison_source.check_during_validation:
            error_message = check(self._comparison_source.file_path(global_environment))
            if error_message:
                return svh.new_svh_validation_error(error_message)
        return svh.new_svh_success()

    def main(self, global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> pfh.PassOrFailOrHardError:
        comparison_file_path = self._comparison_source.file_path(global_environment)
        error_message = check(comparison_file_path)
        if error_message:
            return pfh.new_pfh_fail(error_message)

        comparison_target_path = self.comparison_target.file_path(global_environment)
        if self.comparison_target.do_check_file_properties:
            error_message = check(comparison_target_path)
            if error_message:
                return pfh.new_pfh_fail(error_message)

        target_file_name = str(comparison_target_path)
        comparison_file_name = str(comparison_file_path)
        if not filecmp.cmp(target_file_name, comparison_file_name, shallow=False):
            return pfh.new_pfh_fail('Unexpected content in file: ' + target_file_name)
        return pfh.new_pfh_pass()


class EmptinessCheckerInstruction(instruction_utils.InstructionWithoutValidationBase):
    def __init__(self,
                 expect_empty: bool,
                 comparison_target: ComparisonTarget):
        self.comparison_target = comparison_target
        self.expect_empty = expect_empty

    def main(self, global_environment: i.GlobalEnvironmentForPostEdsPhase,
             phase_environment: i.PhaseEnvironmentForInternalCommands) -> pfh.PassOrFailOrHardError:
        comparison_target_path = self.comparison_target.file_path(global_environment)
        if self.comparison_target.do_check_file_properties:
            error_message = check(comparison_target_path)
            if error_message:
                return pfh.new_pfh_fail(error_message)

        size = self.comparison_target.file_path(global_environment).stat().st_size
        if self.expect_empty:
            if size != 0:
                return pfh.new_pfh_fail('File is not empty: Size (in bytes): ' + str(size))
        else:
            if size == 0:
                return pfh.new_pfh_fail('File is empty')
        return pfh.new_pfh_pass()


def try_parse_content(comparison_target: ComparisonTarget, arguments: list) -> AssertPhaseInstruction:
    def _parse_empty(target: ComparisonTarget,
                     extra_arguments: list) -> AssertPhaseInstruction:
        if extra_arguments:
            raise SingleInstructionInvalidArgumentException('file/empty: Extra arguments: ' + str(extra_arguments))
        return EmptinessCheckerInstruction(True, target)

    def _parse_non_empty(target: ComparisonTarget,
                         extra_arguments: list) -> AssertPhaseInstruction:
        if extra_arguments:
            raise SingleInstructionInvalidArgumentException('file/!empty: Extra arguments: ' + str(extra_arguments))
        return EmptinessCheckerInstruction(False, target)

    def _parse_contents(target: ComparisonTarget,
                        extra_arguments: list) -> AssertPhaseInstruction:
        if len(extra_arguments) != 2:
            msg_header = 'file/contents: Invalid number of arguments (expecting two): '
            raise SingleInstructionInvalidArgumentException(msg_header + str(extra_arguments))
        if extra_arguments[0] == '--rel-home':
            comparison_source = ComparisonSourceForFileRelHome(extra_arguments[1])
        elif extra_arguments[0] == '--rel-cwd':
            comparison_source = ComparisonSourceForFileRelCwd(extra_arguments[1])
        else:
            raise SingleInstructionInvalidArgumentException('Invalid argument: ' + extra_arguments[0])
        return ContentCheckerInstruction(comparison_source, target)

    if arguments[0] == 'contents':
        return _parse_contents(comparison_target, arguments[1:])
    elif arguments[0] == 'empty':
        return _parse_empty(comparison_target, arguments[1:])
    elif arguments[:2] == ['!', 'empty']:
        return _parse_non_empty(comparison_target, arguments[2:])
    return None
