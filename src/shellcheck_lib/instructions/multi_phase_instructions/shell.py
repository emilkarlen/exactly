import subprocess

from shellcheck_lib.document.model import Instruction
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionParserSource, SingleInstructionInvalidArgumentException
from shellcheck_lib.general.textformat.structure.paragraph import single_para
from shellcheck_lib.test_case.help.instruction_description import Description, InvokationVariant


class TheDescriptionBase(Description):
    def __init__(self, name: str):
        super().__init__(name)

    def single_line_description(self) -> str:
        return "Executes the given program using the system's shell."

    def main_description_rest(self) -> list:
        raise NotImplementedError()

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                    'PROGRAM ARGUMENT...',
                    single_para('A plain file.')),
        ]


class Parser(SingleInstructionParser):
    def __init__(self,
                 executor_2_instruction_function):
        self.executor_2_instruction_function = executor_2_instruction_function

    def apply(self, source: SingleInstructionParserSource) -> Instruction:
        arguments = source.instruction_argument.strip()
        if not arguments:
            msg = 'Program to execute must be given as argument'
            raise SingleInstructionInvalidArgumentException(msg)
        executor = Executor(arguments)
        return self.executor_2_instruction_function(executor)


class Executor:
    def __init__(self,
                 command: str):
        self.command = command

    def run(self) -> int:
        """
        :return: exitcode
        """
        return subprocess.call(self.command,
                               shell=True)
