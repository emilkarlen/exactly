import unittest
from typing import Sequence

from exactly_lib.type_val_prims.program.command import Command
from exactly_lib.type_val_prims.program.program import Program
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_transformer import StringTransformer
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, AssertionBase
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command


def is_no_stdin() -> Assertion[Sequence[StringSource]]:
    return asrt.is_empty_sequence


def is_no_transformation() -> Assertion[Sequence[StringTransformer]]:
    return asrt.is_empty_sequence


def matches_program(command: Assertion[Command],
                    stdin: Assertion[Sequence[StringSource]],
                    transformer: Assertion[Sequence[StringTransformer]]) -> Assertion[Program]:
    return _MatchesProgramAssertion(command, stdin, transformer)


def matches_py_source_on_cmd_line_program(py_source_to_interpret: str,
                                          stdin: Assertion[Sequence[StringSource]] = is_no_stdin(),
                                          transformer: Assertion[Sequence[StringTransformer]]
                                          = is_no_transformation()
                                          ) -> Assertion[Program]:
    return matches_program(asrt_command.equals_execute_py_source_command(py_source_to_interpret),
                           stdin=stdin,
                           transformer=transformer)


class _MatchesProgramAssertion(AssertionBase[Program]):
    def __init__(self,
                 command: Assertion[Command],
                 stdin: Assertion[Sequence[StringSource]],
                 transformer: Assertion[Sequence[StringTransformer]],
                 ):
        self.command = command
        self.stdin = stdin
        self.transformer = transformer

    def _apply(self,
               put: unittest.TestCase,
               value: Program,
               message_builder: MessageBuilder):
        asrt.is_instance(Program).apply(put, value, message_builder.for_sub_component('class'))

        assert isinstance(value, Program)

        self.command.apply(put, value.command, message_builder.for_sub_component('command'))

        self.stdin.apply(put, value.stdin, message_builder.for_sub_component('stdin'))

        self.transformer.apply(put, value.transformation, message_builder.for_sub_component('transformation'))
