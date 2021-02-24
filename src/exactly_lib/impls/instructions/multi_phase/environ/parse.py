from typing import FrozenSet

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.impls.instructions.multi_phase.environ import defs, impl as _impl
from exactly_lib.impls.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_embryo import InstructionEmbryo
from exactly_lib.impls.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForUnconditionalSuccess
from exactly_lib.impls.types.string_ import parse_string
from exactly_lib.impls.types.string_source import parse as parse_str_src
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import \
    std_error_message_text_for_token_syntax_error_from_exception
from exactly_lib.section_document.element_parsers.token_stream import TokenSyntaxError
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import reference_restrictions
from exactly_lib.util.parse import token_matchers
from exactly_lib.util.str_.formatter import StringFormatter

_VALUE_PARSE_CONFIGURATION = parse_string.Configuration(syntax_elements.STRING_SYNTAX_ELEMENT.singular_name)


class EmbryoParser(embryo.InstructionEmbryoParserFromTokensWoFileSystemLocationInfo[None]):
    def __init__(self, phase_is_after_act: bool):
        self._phase_is_after_act = phase_is_after_act
        self._name_parser = parse_string.StringFromTokensParser(
            parse_string.Configuration(defs.VAR_NAME_ELEMENT,
                                       reference_restrictions.is_string__all_indirect_refs_are_strings())
        )
        self._value_parser = parse_str_src.default_parser_for(phase_is_after_act=self._phase_is_after_act)
        self._unset_keyword_matcher = token_matchers.is_unquoted_and_equals(defs.UNSET_IDENTIFIER)

    def _parse_from_tokens(self, token_parser: TokenParser) -> InstructionEmbryo[None]:
        try:
            phases = self._parse_phases(token_parser)
            modifier = self._parse_modifier(token_parser)
            token_parser.report_superfluous_arguments_if_not_at_eol()

            return _impl.TheInstructionEmbryo(phases, modifier)

        except TokenSyntaxError as ex:
            raise SingleInstructionInvalidArgumentException(
                std_error_message_text_for_token_syntax_error_from_exception(ex))

    def _parse_modifier(self, token_parser: TokenParser) -> _impl.ModifierSdv:
        if (token_parser.has_valid_head_token() and
                self._unset_keyword_matcher.matches(token_parser.head)):
            token_parser.consume_head()
            return self._parse_unset(token_parser)
        else:
            return self._parse_set(token_parser)

    def _parse_unset(self, token_parser: TokenParser) -> _impl.ModifierSdv:
        var_name = self._name_parser.parse(token_parser)
        return _impl.ModifierSdvOfUnset(var_name)

    def _parse_set(self, token_parser: TokenParser) -> _impl.ModifierSdv:
        var_name = self._name_parser.parse(token_parser)
        token_parser.consume_mandatory_keyword(defs.ASSIGNMENT_IDENTIFIER, False)
        value = self._value_parser.parse_from_token_parser(token_parser)

        return _impl.ModifierSdvOfSet(var_name, value)

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


def parts_parser(phase_is_after_act: bool):
    return PartsParserFromEmbryoParser(EmbryoParser(phase_is_after_act),
                                       MainStepResultTranslatorForUnconditionalSuccess())


class _MissingUnsetKeywordOrVarNameErrorMessage(token_stream_parser.ErrorMessageGenerator):
    def message(self) -> str:
        return _SF.format('Expecting {unset_keyword} or {var_name}')


class _VarNameErrorMessage(token_stream_parser.ErrorMessageGenerator):
    def message(self) -> str:
        return _SF.format('Expecting {var_name}')


_MISSING_UNSET_KEYWORD_OR_VAR_NAME_ERROR_MESSAGE = _MissingUnsetKeywordOrVarNameErrorMessage()
_MISSING_VAR_NAME_ERROR_MESSAGE = _VarNameErrorMessage()

_SF = StringFormatter({
    'unset_keyword': defs.UNSET_IDENTIFIER,
    'var_name': defs.VAR_NAME_ELEMENT,
})
