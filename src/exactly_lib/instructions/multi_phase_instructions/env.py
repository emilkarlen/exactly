import re

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.entity.concepts import SYMBOL_CONCEPT_INFO
from exactly_lib.help_texts.entity.syntax_elements import SYMBOL_REFERENCE_SYNTAX_ELEMENT
from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase_instructions.utils.assert_phase_info import IsAHelperIfInAssertPhase
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForUnconditionalSuccess
from exactly_lib.section_document.element_parsers.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.section_document.element_parsers.misc_utils import new_token_stream, \
    std_error_message_text_for_token_syntax_error_from_exception
from exactly_lib.section_document.element_parsers.token_stream import TokenStream, TokenSyntaxError
from exactly_lib.symbol.data.restrictions.reference_restrictions import is_any_data_type
from exactly_lib.symbol.data.string_resolver import StringResolver
from exactly_lib.symbol.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    PhaseLoggingPaths
from exactly_lib.test_case_utils.parse import parse_string
from exactly_lib.util.textformat.structure.structures import paras


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase,
                                  IsAHelperIfInAssertPhase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        super().__init__(name, _FORMAT_DICT, is_in_assert_phase)

    def single_line_description(self) -> str:
        return 'Manipulates environment variables'

    def _main_description_rest_body(self) -> list:
        return self._paragraphs(_MAIN_DESCRIPTION_REST_BODY)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                _format('{NAME} = {VALUE}'),
                self._paragraphs(_DESCRIPTION_OF_SET)),
            InvokationVariant(
                _format('unset {NAME}'),
                paras(_format('Removes the environment variable {NAME}.'))),
        ]

    def see_also_targets(self) -> list:
        return [
            SYMBOL_REFERENCE_SYNTAX_ELEMENT.cross_reference_target
        ]


def _format(template: str) -> str:
    return template.format_map(_FORMAT_DICT)


_FORMAT_DICT = {
    'NAME': 'NAME',
    'VALUE': 'VALUE',
    'SYMBOLS': SYMBOL_CONCEPT_INFO.name.plural,
}

_DESCRIPTION_OF_SET = """\
Sets the environment variable {NAME} to {VALUE}.


Elements of the form "${{var_name}}" in {VALUE}, will be replaced with the value of the environment variable "var_name",
or the empty string, if there is no environment variable with that name.


{VALUE} may contain references to {SYMBOLS}.
"""


class Executor:
    def execute(self,
                environ: dict,
                resolving_environment: PathResolvingEnvironmentPreOrPostSds):
        raise NotImplementedError()


class TheInstructionEmbryo(embryo.InstructionEmbryo):
    def __init__(self,
                 executor: Executor,
                 symbol_references: list):
        self.symbol_references = symbol_references
        self.executor = executor

    @property
    def symbol_usages(self) -> list:
        return self.symbol_references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             logging_paths: PhaseLoggingPaths,
             os_services: OsServices):
        return self.executor.execute(environment.environ,
                                     environment.path_resolving_environment_pre_or_post_sds)


class EmbryoParser(embryo.InstructionEmbryoParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> TheInstructionEmbryo:
        try:
            tokens = new_token_stream(rest_of_line)
            if tokens.is_null:
                raise SingleInstructionInvalidArgumentException('Missing arguments')
            first = tokens.consume()
            if first.is_quoted:
                raise SingleInstructionInvalidArgumentException('Variable name must not be quoted')
            if tokens.is_null:
                if first.string == UNSET_IDENTIFIER:
                    raise SingleInstructionInvalidArgumentException('Missing variable name to unset')
                else:
                    raise SingleInstructionInvalidArgumentException('Missing arguments of variable assignment')
            second = tokens.consume()
            if second.source_string == ASSIGNMENT_IDENTIFIER:
                return self._parse_set(first.string, tokens)
            elif first.string == UNSET_IDENTIFIER:
                if second.is_quoted:
                    raise SingleInstructionInvalidArgumentException('Variable name must not be quoted')
                return self._parse_unset(second.string, tokens)

            else:
                raise SingleInstructionInvalidArgumentException('Invalid syntax')
        except TokenSyntaxError as ex:
            raise SingleInstructionInvalidArgumentException(
                std_error_message_text_for_token_syntax_error_from_exception(ex))

    def _parse_unset(self, variable_name: str, remaining_tokens: TokenStream) -> TheInstructionEmbryo:
        if not remaining_tokens.is_null:
            raise SingleInstructionInvalidArgumentException(_format('Superfluous arguments.'))
        return TheInstructionEmbryo(_UnsetExecutor(variable_name), [])

    def _parse_set(self, variable_name: str, tokens_for_value: TokenStream) -> TheInstructionEmbryo:
        if tokens_for_value.is_null:
            raise SingleInstructionInvalidArgumentException(_format('Missing {VALUE}.'))
        value_token = tokens_for_value.consume()
        if not tokens_for_value.is_null:
            raise SingleInstructionInvalidArgumentException(_format('Superfluous arguments.'))
        value_resolver = parse_string.parse_string_resolver_from_token(value_token,
                                                                       is_any_data_type())
        executor = _SetExecutor(variable_name, value_resolver)
        return TheInstructionEmbryo(executor, value_resolver.references)


UNSET_IDENTIFIER = 'unset'
ASSIGNMENT_IDENTIFIER = instruction_arguments.ASSIGNMENT_OPERATOR

PARTS_PARSER = PartsParserFromEmbryoParser(EmbryoParser(),
                                           MainStepResultTranslatorForUnconditionalSuccess())


class _SetExecutor(Executor):
    def __init__(self,
                 name: str,
                 value: StringResolver):
        self.name = name
        self.value_resolver = value

    def execute(self, environ: dict,
                resolving_environment: PathResolvingEnvironmentPreOrPostSds):
        value = self._resolve_value(environ, resolving_environment)
        environ[self.name] = _expand_vars(value, environ)

    def _resolve_value(self,
                       environ: dict,
                       resolving_environment: PathResolvingEnvironmentPreOrPostSds) -> str:
        fragments = []
        for fragment in self.value_resolver.fragments:
            if fragment.is_string_constant:
                fragment_value = _expand_vars(fragment.string_constant, environ)
            elif fragment.is_symbol:
                fragment_value = fragment.resolve_value_of_any_dependency(resolving_environment)
            else:
                raise TypeError('Unknown String Fragment: ' + str(fragment))
            fragments.append(fragment_value)
        return ''.join(fragments)


class _UnsetExecutor(Executor):
    def __init__(self,
                 name: str):
        self.name = name

    def execute(self, environ: dict,
                resolving_environment: PathResolvingEnvironmentPreOrPostSds):
        try:
            del environ[self.name]
        except KeyError:
            pass


_MAIN_DESCRIPTION_REST_BODY = """\
The manipulation affects all following phases.
"""

_ENV_VAR_REFERENCE = re.compile('\${[a-zA-Z0-9_]+}')


def _expand_vars(value: str, environ: dict) -> str:
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
