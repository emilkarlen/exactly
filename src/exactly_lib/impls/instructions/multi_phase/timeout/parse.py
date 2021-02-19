from typing import Optional

from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_embryo import InstructionEmbryo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForUnconditionalSuccess
from exactly_lib.impls.types.integer import parse_integer
from exactly_lib.impls.types.integer.integer_sdv import IntegerSdv
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import \
    std_error_message_text_for_token_syntax_error_from_exception
from exactly_lib.section_document.element_parsers.token_stream import TokenSyntaxError
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.util.parse import token_matchers
from . import defs, impl as _impl


class EmbryoParser(embryo.InstructionEmbryoParserFromTokensWoFileSystemLocationInfo[None]):
    def __init__(self):
        self._int_parser = parse_integer.MandatoryIntegerParser(
            parse_integer.validator_for_non_negative,
        )
        self._none_token_matcher = token_matchers.is_unquoted_and_equals(defs.NONE_TOKEN)

    def _parse_from_tokens(self, token_parser: TokenParser) -> InstructionEmbryo[None]:
        try:
            token_parser.consume_mandatory_keyword(defs.ASSIGNMENT_IDENTIFIER, False)
            value = self._parse_value(token_parser)
            token_parser.report_superfluous_arguments_if_not_at_eol()

            return _impl.TheInstructionEmbryo(value)

        except TokenSyntaxError as ex:
            raise SingleInstructionInvalidArgumentException(
                std_error_message_text_for_token_syntax_error_from_exception(ex))

    def _parse_value(self, token_parser: TokenParser) -> Optional[IntegerSdv]:
        if token_parser.has_valid_head_matching__consume(self._none_token_matcher):
            return None
        else:
            return self._int_parser.parse(token_parser)


PARTS_PARSER = PartsParserFromEmbryoParser(
    EmbryoParser(),
    MainStepResultTranslatorForUnconditionalSuccess(),
)
