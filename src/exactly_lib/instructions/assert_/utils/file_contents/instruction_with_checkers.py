import pathlib

from exactly_lib.instructions.assert_.utils.assertion_part import AssertionPart, SequenceOfCooperativeAssertionParts, \
    AssertionInstructionFromChecker
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.contents_checkers import FileExistenceAssertionPart, \
    FileTransformerAsAssertionPart
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver


class ActualFileAssertionPart(AssertionPart):
    """
    A :class:`AssertionPart` that is given
    the path of a file to operate on.

    This class is just a marker for more informative types.

    Behaviour is identical to :class:`AssertionPart`.
    """

    def check(self,
              environment: InstructionEnvironmentForPostSdsStep,
              os_services: OsServices,
              file_to_check: pathlib.Path
              ):
        return super().check(environment, os_services, file_to_check)


def instruction_with_exist_trans_and_checker(actual_file: ComparisonActualFile,
                                             actual_file_transformer_resolver: FileTransformerResolver,
                                             checker_of_transformed_file_path: ActualFileAssertionPart
                                             ) -> AssertPhaseInstruction:
    """
    An instruction that

     - checks the existence of a file,
     - transform it using a given transformer
     - performs a last custom check on the transformed file
    """

    return AssertionInstructionFromChecker(
        SequenceOfCooperativeAssertionParts([
            FileExistenceAssertionPart(actual_file),
            FileTransformerAsAssertionPart(actual_file_transformer_resolver),
            checker_of_transformed_file_path,
        ]),
        lambda env: 'not used'
    )
