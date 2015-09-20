import argparse
import shlex

from shellcheck_lib.document.model import Instruction
from shellcheck_lib.general import line_source
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import SingleInstructionParser, \
    SingleInstructionInvalidArgumentException


class SingleLineParser(SingleInstructionParser):
    def __init__(self,
                 parser: argparse.ArgumentParser):
        self._parser = parser

    def apply(self,
              source: line_source.LineSequenceBuilder,
              instruction_argument: str) -> Instruction:
        try:
            arguments = self._split_argument(instruction_argument)
        except Exception:
            raise SingleInstructionInvalidArgumentException('Invalid arguments: "%s"' % instruction_argument)

        original_error_handler = argparse.ArgumentParser.error

        def error_handler(the_parser: argparse.ArgumentParser, the_message: str):
            raise SingleInstructionInvalidArgumentException(the_message)

        try:
            argparse.ArgumentParser.error = error_handler
            namespace = self._parser.parse_args(arguments)
        finally:
            argparse.ArgumentParser.error = original_error_handler
        return self._new_instruction_from(namespace)

    def _new_instruction_from(self, namespace: argparse.Namespace) -> Instruction:
        """
        :raises SingleInstructionInvalidArgumentException:
        :param namespace: Return value from argument parser.
        """
        raise NotImplementedError()

    def _split_argument(self, instruction_argument: str) -> list:
        return shlex.split(instruction_argument)
