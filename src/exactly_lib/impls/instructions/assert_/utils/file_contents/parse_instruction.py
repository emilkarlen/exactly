from exactly_lib.impls.instructions.assert_.utils import assertion_part
from exactly_lib.impls.instructions.assert_.utils.assertion_part import AssertionInstructionFromAssertionPart, \
    IdentityAssertionPartWithValidationAndReferences
from exactly_lib.impls.instructions.assert_.utils.file_contents import parse_file_contents_assertion_part
from exactly_lib.impls.instructions.assert_.utils.file_contents.actual_files import ComparisonActualFileConstructor
from exactly_lib.impls.instructions.assert_.utils.file_contents.parts.contents_checkers import \
    FileConstructorAssertionPart, \
    IsExistingRegularFileAssertionPart
from exactly_lib.impls.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionTokenParser
from exactly_lib.section_document.element_parsers.ps_or_tp.parsers import ParserFromTokenParserBase
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction


class ComparisonActualFileParser(ParserFromTokenParserBase[ComparisonActualFileConstructor]):
    pass


class Parser(AssertPhaseInstructionTokenParser):
    """
    An instruction that

     - checks the existence of a file,
     - transform it using a given transformer
     - performs a last custom check on the transformed file
    """

    def __init__(self,
                 instruction_name: str,
                 actual_file_parser: ComparisonActualFileParser):
        self._instruction_name = instruction_name
        self._actual_file_parser = actual_file_parser

    def parse_from_token_parser(self, parser: TokenParser) -> AssertPhaseInstruction:
        actual_file_constructor = self._actual_file_parser.parse_from_token_parser(parser)
        actual_file_assertion_part = parse_file_contents_assertion_part.parse(parser)
        parser.report_superfluous_arguments_if_not_at_eol()

        assertion_part_sequence = assertion_part.compose(
            IdentityAssertionPartWithValidationAndReferences(actual_file_constructor.validator,
                                                             actual_file_constructor.references),
            FileConstructorAssertionPart(),
        )
        assertion_part_sequence = assertion_part.compose_with_sequence(
            assertion_part_sequence,
            IsExistingRegularFileAssertionPart(),
        )
        assertion_part_sequence = assertion_part.compose_with_sequence(
            assertion_part_sequence,
            actual_file_assertion_part,
        )
        return AssertionInstructionFromAssertionPart(
            assertion_part_sequence,
            lambda env: actual_file_constructor,
            actual_file_constructor.failure_message_header,
        )
