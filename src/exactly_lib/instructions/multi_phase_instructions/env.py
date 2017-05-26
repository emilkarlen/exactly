import re

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.instructions.multi_phase_instructions.utils import instruction_embryo as embryo
from exactly_lib.instructions.multi_phase_instructions.utils.main_step_executor_for_single_method_executor import \
    MainStepExecutorForGenericMethodWithStringErrorMessage
from exactly_lib.instructions.multi_phase_instructions.utils.parser import InstructionPartsParser
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.instructions.utils.instruction_parts import InstructionParts
from exactly_lib.instructions.utils.pre_or_post_validation import ConstantSuccessValidator
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
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
    def execute(self, environ: dict):
        raise NotImplementedError()


class InstructionEmbryo(embryo.InstructionEmbryo):
    def __init__(self, executor: Executor):
        self.executor = executor


class TheMainStepExecutor(MainStepExecutorForGenericMethodWithStringErrorMessage):
    def __init__(self, executor: Executor):
        self.executor = executor

    def execute(self,
                environment: InstructionEnvironmentForPostSdsStep,
                logging_paths: PhaseLoggingPaths,
                os_services: OsServices) -> str:
        self.executor.execute(environment.environ)
        return None


class EmbryoParser(embryo.InstructionEmbryoParserThatConsumesCurrentLine):
    def _parse(self, rest_of_line: str) -> InstructionEmbryo:
        arguments = split_arguments_list_string(rest_of_line)
        if len(arguments) == 3 and arguments[1] == '=':
            return InstructionEmbryo(_SetExecutor(arguments[0],
                                                  arguments[2]))
        if len(arguments) == 2 and arguments[0] == 'unset':
            return InstructionEmbryo(_UnsetExecutor(arguments[1]))
        raise SingleInstructionInvalidArgumentException('Invalid syntax')


class PartsParser(InstructionPartsParser):
    embryo_parser = EmbryoParser()

    def parse(self, source: ParseSource) -> InstructionParts:
        the_embryo = self.embryo_parser.parse(source)
        assert isinstance(the_embryo, InstructionEmbryo)
        return InstructionParts(ConstantSuccessValidator(),
                                TheMainStepExecutor(the_embryo.executor),
                                symbol_usages=tuple(the_embryo.symbol_usages))


class _SetExecutor(Executor):
    def __init__(self,
                 name: str,
                 value: str):
        self.name = name
        self.value = value

    def execute(self, environ: dict):
        environ[self.name] = _expand_vars(self.value, environ)


class _UnsetExecutor(Executor):
    def __init__(self,
                 name: str):
        self.name = name

    def execute(self, environ: dict):
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
