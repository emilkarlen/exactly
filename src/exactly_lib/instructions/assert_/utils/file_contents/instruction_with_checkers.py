from exactly_lib.instructions.assert_.utils.assertion_part import SequenceOfCooperativeAssertionParts, \
    AssertionInstructionFromAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFile
from exactly_lib.instructions.assert_.utils.file_contents.parts.contents_checkers import FileExistenceAssertionPart, \
    FileTransformerAsAssertionPart
from exactly_lib.instructions.assert_.utils.file_contents.parts.file_assertion_part import ActualFileAssertionPart
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction
from exactly_lib.test_case_utils.file_transformer.file_transformer import FileTransformerResolver


def instruction_with_exist_trans_and_assertion_part(actual_file: ComparisonActualFile,
                                                    actual_file_transformer_resolver: FileTransformerResolver,
                                                    checker_of_transformed_file_path: ActualFileAssertionPart
                                                    ) -> AssertPhaseInstruction:
    """
    An instruction that

     - checks the existence of a file,
     - transform it using a given transformer
     - performs a last custom check on the transformed file
    """

    return AssertionInstructionFromAssertionPart(
        SequenceOfCooperativeAssertionParts([
            FileExistenceAssertionPart(actual_file),
            FileTransformerAsAssertionPart(actual_file_transformer_resolver),
            checker_of_transformed_file_path,
        ]),
        lambda env: 'not used'
    )
