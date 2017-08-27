from exactly_lib.instructions.assert_.utils.checker import Checker, SequenceOfChecks, AssertionInstructionFromChecker
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.contents_checkers import FileExistenceChecker, \
    FileTransformerAsChecker
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver


def instruction_with_exist_trans_and_checker(actual_file: ComparisonActualFile,
                                             actual_file_transformer_resolver: FileTransformerResolver,
                                             checker_of_transformed_file_path: Checker) -> AssertPhaseInstruction:
    """
    An instruction that

     - checks the existence of a file,
     - transform it using a given transformer
     - performs a last custom check on the transformed file
    """

    return AssertionInstructionFromChecker(
        SequenceOfChecks([
            FileExistenceChecker(actual_file),
            FileTransformerAsChecker(actual_file_transformer_resolver),
            checker_of_transformed_file_path,
        ]),
        lambda env: 'not used'
    )
