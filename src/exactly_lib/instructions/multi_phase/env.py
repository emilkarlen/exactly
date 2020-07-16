import re
from typing import Sequence, Dict, List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.definitions import instruction_arguments
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.instructions.multi_phase.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForUnconditionalSuccess
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.instruction_parser_exceptions import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import \
    std_error_message_text_for_token_syntax_error_from_exception
from exactly_lib.section_document.element_parsers.token_stream import TokenSyntaxError
from exactly_lib.section_document.element_parsers.token_stream_parser import TokenParser
from exactly_lib.symbol.data.string_sdv import StringSdv
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.symbol.sdv_structure import SymbolUsage, SymbolReference
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.util.str_.formatter import StringFormatter
from exactly_lib.util.textformat.structure.core import ParagraphItem

UNSET_IDENTIFIER = 'unset'
ASSIGNMENT_IDENTIFIER = instruction_arguments.ASSIGNMENT_OPERATOR


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        super().__init__(name, _FORMAT_DICT, is_in_assert_phase)

    def single_line_description(self) -> str:
        return 'Manipulates environment variables'

    def _main_description_rest_body(self) -> List[ParagraphItem]:
        return self._tp.fnap(_MAIN_DESCRIPTION_REST_BODY)

    def invokation_variants(self) -> Sequence[InvokationVariant]:
        return [
            InvokationVariant(
                self._tp.format('{NAME} = {VALUE}'),
                self._tp.fnap(_DESCRIPTION_OF_SET)),
            InvokationVariant(
                self._tp.format('{unset_keyword} {NAME}'),
                self._tp.fnap('Removes the environment variable {NAME}.')),
        ]

    def see_also_targets(self) -> list:
        return [
            syntax_elements.STRING_SYNTAX_ELEMENT.cross_reference_target,
        ]


class Executor:
    def execute(self,
                environ: Dict[str, str],
                resolving_environment: PathResolvingEnvironmentPreOrPostSds):
        raise NotImplementedError()


class TheInstructionEmbryo(embryo.InstructionEmbryo[None]):
    def __init__(self,
                 executor: Executor,
                 symbol_references: Sequence[SymbolReference]):
        self.symbol_references = symbol_references
        self.executor = executor

    @property
    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.symbol_references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             ):
        self.executor.execute(environment.proc_exe_settings.environ,
                              environment.path_resolving_environment_pre_or_post_sds)


class EmbryoParser(embryo.InstructionEmbryoParserFromTokensWoFileSystemLocationInfo[None]):
    def _parse_from_tokens(self, token_parser: TokenParser) -> TheInstructionEmbryo:
        try:
            unset_keyword_or_var_name = token_parser.consume_mandatory_unquoted_string__w_err_msg(
                False,
                _MISSING_UNSET_KEYWORD_OR_VAR_NAME_ERROR_MESSAGE
            )

            return (
                self._parse_unset_or_set_var_with_same_name_as_unset_keyword(token_parser)
                if unset_keyword_or_var_name == UNSET_IDENTIFIER
                else
                self._parse_set(token_parser, unset_keyword_or_var_name)
            )

        except TokenSyntaxError as ex:
            raise SingleInstructionInvalidArgumentException(
                std_error_message_text_for_token_syntax_error_from_exception(ex))

    def _parse_unset_or_set_var_with_same_name_as_unset_keyword(self,
                                                                token_parser: TokenParser,
                                                                ) -> TheInstructionEmbryo:
        if token_parser.has_valid_head_token():
            head = token_parser.head
            if head.is_plain and head.string == ASSIGNMENT_IDENTIFIER:
                return self._parse_set(token_parser, UNSET_IDENTIFIER)

        var_name = token_parser.consume_mandatory_unquoted_string__w_err_msg(
            False,
            _MISSING_VAR_NAME_ERROR_MESSAGE
        )

        token_parser.report_superfluous_arguments_if_not_at_eol()
        return TheInstructionEmbryo(_UnsetExecutor(var_name), [])

    def _parse_set(self, token_parser: TokenParser, var_name: str) -> TheInstructionEmbryo:
        token_parser.consume_mandatory_keyword(ASSIGNMENT_IDENTIFIER, False)

        value = parse_string.parse_string_from_token_parser(token_parser, _VALUE_PARSE_CONFIGURATION)
        token_parser.report_superfluous_arguments_if_not_at_eol()

        executor = _SetExecutor(var_name, value)
        return TheInstructionEmbryo(executor, value.references)


PARTS_PARSER = PartsParserFromEmbryoParser(EmbryoParser(),
                                           MainStepResultTranslatorForUnconditionalSuccess())


class _SetExecutor(Executor):
    def __init__(self,
                 name: str,
                 value: StringSdv):
        self.name = name
        self.value_sdv = value

    def execute(self,
                environ: Dict[str, str],
                resolving_environment: PathResolvingEnvironmentPreOrPostSds):
        value = self._resolve_value(environ, resolving_environment)
        environ[self.name] = _expand_vars(value, environ)

    def _resolve_value(self,
                       environ: Dict[str, str],
                       resolving_environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        fragments = []
        for fragment in self.value_sdv.fragments:
            if fragment.is_string_constant:
                fragment_value = _expand_vars(fragment.string_constant, environ)
            else:
                fragment_value = fragment.resolve_value_of_any_dependency(resolving_environment)
            fragments.append(fragment_value)
        return ''.join(fragments)


class _UnsetExecutor(Executor):
    def __init__(self, name: str):
        self.name = name

    def execute(self,
                environ: Dict[str, str],
                resolving_environment: PathResolvingEnvironmentPreOrPostSds):
        try:
            del environ[self.name]
        except KeyError:
            pass


def _expand_vars(value: str, environ: Dict[str, str]) -> str:
    def substitute(reference: str) -> str:
        var_name = reference[2:-1]
        try:
            return environ[var_name]
        except KeyError:
            return ''

    processed = ''
    remaining = value
    match = _ENV_VAR_REFERENCE.search(remaining)
    while match:
        processed += remaining[:match.start()]
        processed += substitute(remaining[match.start():match.end()])
        remaining = remaining[match.end():]
        match = _ENV_VAR_REFERENCE.search(remaining)
    processed += remaining
    return processed


class _MissingUnsetKeywordOrVarNameErrorMessage(token_stream_parser.ErrorMessageGenerator):
    def message(self) -> str:
        return _SF.format('Expecting {unset_keyword} or {var_name}')


class _VarNameErrorMessage(token_stream_parser.ErrorMessageGenerator):
    def message(self) -> str:
        return _SF.format('Expecting {var_name}')


_MISSING_UNSET_KEYWORD_OR_VAR_NAME_ERROR_MESSAGE = _MissingUnsetKeywordOrVarNameErrorMessage()
_MISSING_VAR_NAME_ERROR_MESSAGE = _VarNameErrorMessage()

_ENV_VAR_REFERENCE = re.compile('\${[a-zA-Z0-9_]+}')

_VALUE_PARSE_CONFIGURATION = parse_string.Configuration(syntax_elements.STRING_SYNTAX_ELEMENT.singular_name)

_VAR_NAME_ELEMENT = 'NAME'

_SF = StringFormatter({
    'unset_keyword': UNSET_IDENTIFIER,
    'var_name': _VAR_NAME_ELEMENT,
})

_FORMAT_DICT = {
    'NAME': _VAR_NAME_ELEMENT,
    'VALUE': syntax_elements.STRING_SYNTAX_ELEMENT.singular_name,
    'SYMBOLS': concepts.SYMBOL_CONCEPT_INFO.name.plural,
    'unset_keyword': UNSET_IDENTIFIER,
}

_DESCRIPTION_OF_SET = """\
Sets the environment variable {NAME} to {VALUE}.


Elements of the form "${{var_name}}" in {VALUE}, will be replaced with the value of the environment variable "var_name",
or the empty string, if there is no environment variable with that name.
"""

_MAIN_DESCRIPTION_REST_BODY = """\
The manipulation affects all following phases.
"""
