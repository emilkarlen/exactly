import re

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase_instructions.utils.instruction_part_utils import PartsParserFromEmbryoParser, \
    MainStepResultTranslatorForUnconditionalSuccess
from exactly_lib.instructions.utils.arg_parse import parse_string
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.string_resolver import StringResolver
from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep, \
    PhaseLoggingPaths
from exactly_lib.util.textformat.structure.structures import paras


class TheInstructionDocumentation(InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase):
    def __init__(self, name: str, is_in_assert_phase: bool = False):
        super().__init__(name, {}, is_in_assert_phase)

    def single_line_description(self) -> str:
        return 'Manipulates environment variables'

    def _main_description_rest_body(self) -> list:
        return self._paragraphs(_MAIN_DESCRIPTION_REST_BODY)

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                'NAME = VALUE',
                self._paragraphs(_DESCRIPTION_OF_SET)),
            InvokationVariant(
                'unset NAME',
                paras('Removes the environment variable NAME.')),
        ]


_DESCRIPTION_OF_SET = """\
Sets the environment variable NAME to VALUE.


Elements of the form "${{var_name}}" in VALUE, will be replaced with the value of the environment variable "var_name",
or the empty string, if there is no environment variable with that name.
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
        arguments = split_arguments_list_string(rest_of_line)
        if len(arguments) == 3 and arguments[1] == '=':
            value_resolver = parse_string.string_resolver_from_string(arguments[2])
            executor = _SetExecutor(arguments[0], value_resolver)
            return TheInstructionEmbryo(executor, value_resolver.references)
        if len(arguments) == 2 and arguments[0] == 'unset':
            return TheInstructionEmbryo(_UnsetExecutor(arguments[1]), [])
        raise SingleInstructionInvalidArgumentException('Invalid syntax')


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
