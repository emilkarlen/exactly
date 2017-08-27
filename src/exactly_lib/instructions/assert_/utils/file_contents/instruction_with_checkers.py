from exactly_lib.instructions.assert_.utils.checker import Checker, SequenceOfChecks
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.contents_checkers import FileExistenceChecker, \
    FileTransformerAsChecker
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.result import pfh
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver


class AssertionInstructionWithChecker(AssertPhaseInstruction):
    """
    An instruction that

     - checks the existence of a file,
     - transform it using a given transformer
     - performs a last custom check on the transformed file
    """

    def __init__(self,
                 actual_file: ComparisonActualFile,
                 actual_file_transformer_resolver: FileTransformerResolver,
                 checker_of_transformed_file_path: Checker):
        self.actual_file = actual_file
        self.checker = SequenceOfChecks([
            FileExistenceChecker(),
            FileTransformerAsChecker(actual_file_transformer_resolver),
            checker_of_transformed_file_path,
        ])

    def symbol_usages(self) -> list:
        return self.checker.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices) -> pfh.PassOrFailOrHardError:
        return self.checker.check_and_return_pfh(environment, os_services, self.actual_file)
