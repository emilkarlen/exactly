from typing import FrozenSet

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.instructions.multi_phase.environ import defs, impl as _impl
from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_embryo import InstructionEmbryo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForUnconditionalSuccess
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import \
    std_error_message_text_for_token_syntax_error_from_exception
from exactly_lib.section_document.element_parsers.token_stream import TokenSyntaxError
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.util.str_.formatter import StringFormatter


class EmbryoParser(embryo.InstructionEmbryoParserFromTokensWoFileSystemLocationInfo[None]):
    def _parse_from_tokens(self, token_parser: TokenParser) -> InstructionEmbryo[None]:
        try:
            phases = self._parse_phases(token_parser)

            unset_keyword_or_var_name = token_parser.consume_mandatory_unquoted_string__w_err_msg(
                False,
                _MISSING_UNSET_KEYWORD_OR_VAR_NAME_ERROR_MESSAGE
            )

            modifier = (
                self._parse_unset_or_set_var_with_same_name_as_unset_keyword(token_parser)
                if unset_keyword_or_var_name == defs.UNSET_IDENTIFIER
                else
                self._parse_set(token_parser, unset_keyword_or_var_name)
            )

            token_parser.report_superfluous_arguments_if_not_at_eol()

            return _impl.TheInstructionEmbryo(phases, modifier)

        except TokenSyntaxError as ex:
            raise SingleInstructionInvalidArgumentException(
                std_error_message_text_for_token_syntax_error_from_exception(ex))

    def _parse_unset_or_set_var_with_same_name_as_unset_keyword(self,
                                                                token_parser: TokenParser,
                                                                ) -> _impl.ModifierResolver:
        if token_parser.has_valid_head_token():
            head = token_parser.head
            if head.is_plain and head.string == defs.ASSIGNMENT_IDENTIFIER:
                return self._parse_set(token_parser, defs.UNSET_IDENTIFIER)

        var_name = token_parser.consume_mandatory_unquoted_string__w_err_msg(
            False,
            _MISSING_VAR_NAME_ERROR_MESSAGE
        )

        return _impl.ModifierResolverOfUnset(var_name)

    @staticmethod
    def _parse_set(token_parser: TokenParser, var_name: str) -> _impl.ModifierResolver:
        token_parser.consume_mandatory_keyword(defs.ASSIGNMENT_IDENTIFIER, False)

        value = parse_string.parse_string_from_token_parser(token_parser, _VALUE_PARSE_CONFIGURATION)

        return _impl.ModifierResolverOfSet(var_name, value)

    @staticmethod
    def _parse_phases(token_parser: TokenParser) -> FrozenSet[_impl.Phase]:
        return token_parser.consume_and_handle_optional_option(
            _ALL_PHASES,
            _parse_phase_spec_option_argument,
            defs.PHASE_SPEC__OPTION_NAME,
        )


def _parse_phase_spec_option_argument(token_parser: TokenParser) -> FrozenSet[_impl.Phase]:
    return token_parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
        _SET_SPEC_ARGUMENTS,
        _SET_SPEC_ARGUMENT_2_SPEC.get,
        _INVALID_PHASE_SPEC_ARGUMENT__ERR_MSG,
    )


_INVALID_PHASE_SPEC_ARGUMENT__ERR_MSG = 'Invalid phase spec <TODO>'

_SET_SPEC_ARGUMENTS = (defs.PHASE_SPEC__ACT, defs.PHASE_SPEC__NON_ACT)

_SET_SPEC_ARGUMENT_2_SPEC = {
    defs.PHASE_SPEC__ACT: frozenset((_impl.Phase.ACT,)),
    defs.PHASE_SPEC__NON_ACT: frozenset((_impl.Phase.NON_ACT,)),
}

_ALL_PHASES = frozenset(_impl.Phase)

PARTS_PARSER = PartsParserFromEmbryoParser(EmbryoParser(),
                                           MainStepResultTranslatorForUnconditionalSuccess())


class _MissingUnsetKeywordOrVarNameErrorMessage(token_stream_parser.ErrorMessageGenerator):
    def message(self) -> str:
        return _SF.format('Expecting {unset_keyword} or {var_name}')


class _VarNameErrorMessage(token_stream_parser.ErrorMessageGenerator):
    def message(self) -> str:
        return _SF.format('Expecting {var_name}')


_MISSING_UNSET_KEYWORD_OR_VAR_NAME_ERROR_MESSAGE = _MissingUnsetKeywordOrVarNameErrorMessage()
_MISSING_VAR_NAME_ERROR_MESSAGE = _VarNameErrorMessage()
_VALUE_PARSE_CONFIGURATION = parse_string.Configuration(syntax_elements.STRING_SYNTAX_ELEMENT.singular_name)
_SF = StringFormatter({
    'unset_keyword': defs.UNSET_IDENTIFIER,
    'var_name': defs.VAR_NAME_ELEMENT,
})
