import types

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.utils.parse_utils import split_arguments_list_string
from shellcheck_lib.test_case.instruction_description import InvokationVariant, Description
from shellcheck_lib.test_case.os_services import OsServices
from shellcheck_lib.test_case.phases.common import TestCaseInstruction
from shellcheck_lib.test_case.phases.result import sh
from shellcheck_lib.util.textformat.structure.paragraph import single_para


class TheDescription(Description):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return 'Manipulates environment variables.'

    def main_description_rest(self) -> list:
        return []

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    'NAME = VALUE',
                    single_para('Sets the environment variable NAME to VALUE.')),
            InvokationVariant(
                    'unset NAME',
                    single_para('Removes the environment variable NAME.')),
        ]


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
    def execute(self, os_services: OsServices):
        raise NotImplementedError()


def execute_and_return_sh(executor: Executor,
                          os_services: OsServices) -> sh.SuccessOrHardError:
    executor.execute(os_services)
    return sh.new_sh_success()


class _SetExecutor(Executor):
    def __init__(self,
                 name: str,
                 value: str):
        self.name = name
        self.value = value

    def execute(self, os_services: OsServices):
        os_services.environ[self.name] = self.value


class _UnsetExecutor(Executor):
    def __init__(self,
                 name: str):
        self.name = name

    def execute(self, os_services: OsServices):
        try:
            del os_services.environ[self.name]
        except KeyError:
            pass
