import re
import types

from exactly_lib.common.help.syntax_contents_structure import InvokationVariant
from exactly_lib.instructions.utils.arg_parse.parse_utils import split_arguments_list_string
from exactly_lib.instructions.utils.documentation.instruction_documentation_with_text_parser import \
    InstructionDocumentationThatIsNotMeantToBeAnAssertionInAssertPhaseBase
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.common import TestCaseInstruction
from exactly_lib.test_case.phases.result import sh
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


class Parser(SingleInstructionParser):
    def __init__(self,
                 instruction_constructor_for_executor: types.FunctionType):
        self.instruction_constructor_for_executor = instruction_constructor_for_executor

    def apply(self, source: SingleInstructionParserSource) -> TestCaseInstruction:
        arguments = split_arguments_list_string(source.instruction_argument)
        if len(arguments) == 3 and arguments[1] == '=':
            return self.instruction_constructor_for_executor(_SetExecutor(arguments[0],
                                                                          arguments[2]))
        if len(arguments) == 2 and arguments[0] == 'unset':
            return self.instruction_constructor_for_executor(_UnsetExecutor(arguments[1]))
        raise SingleInstructionInvalidArgumentException('Invalid syntax')


class Executor:
    def execute(self, environ: dict):
        raise NotImplementedError()


def execute_and_return_sh(executor: Executor,
                          environ: dict) -> sh.SuccessOrHardError:
    executor.execute(environ)
    return sh.new_sh_success()


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
