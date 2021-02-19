from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_embryo import InstructionEmbryo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForUnconditionalSuccess
from exactly_lib.impls.types.integer import parse_integer
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import \
    std_error_message_text_for_token_syntax_error_from_exception
from exactly_lib.section_document.element_parsers.token_stream import TokenSyntaxError
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from . import defs, impl as _impl

_VALUE_PARSE_CONFIGURATION = parse_string.Configuration(syntax_elements.STRING_SYNTAX_ELEMENT.singular_name)


class EmbryoParser(embryo.InstructionEmbryoParserFromTokensWoFileSystemLocationInfo[None]):
    def __init__(self):
        self._value_parser = parse_integer.MandatoryIntegerParser(
            parse_integer.validator_for_non_negative,
        )

    def _parse_from_tokens(self, token_parser: TokenParser) -> InstructionEmbryo[None]:
        try:
            token_parser.consume_mandatory_keyword(defs.ASSIGNMENT_IDENTIFIER, False)
            value = self._value_parser.parse(token_parser)
            token_parser.report_superfluous_arguments_if_not_at_eol()

            return _impl.TheInstructionEmbryo(value)

        except TokenSyntaxError as ex:
            raise SingleInstructionInvalidArgumentException(
                std_error_message_text_for_token_syntax_error_from_exception(ex))


PARTS_PARSER = PartsParserFromEmbryoParser(
    EmbryoParser(),
    MainStepResultTranslatorForUnconditionalSuccess(),
)
