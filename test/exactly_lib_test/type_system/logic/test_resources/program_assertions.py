import unittest

from exactly_lib.type_system.logic.program.program_value import Program
from exactly_lib.type_system.logic.program.stdin_data_values import StdinData
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib.util.process_execution.command import Command
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder, ValueAssertionBase
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources import string_transformer_assertions as asrt_line_trans
from exactly_lib_test.util.test_resources import command_assertions as asrt_command


def no_stdin() -> ValueAssertion[StdinData]:
    return asrt.is_instance_with(StdinData,
                                 asrt.sub_component('fragments',
                                                    StdinData.fragments.fget,
                                                    asrt.is_empty_sequence),
                                 )


def matches_program(command: ValueAssertion[Command],
                    stdin: ValueAssertion[StdinData],
                    transformer: ValueAssertion[StringTransformer]) -> ValueAssertion[Program]:
    return _MatchesProgramAssertion(command, stdin, transformer)


def matches_plain_program(command: ValueAssertion[Command]):
    return matches_program(command,
                           no_stdin(),
                           asrt_line_trans.is_identity_transformer())


def matches_py_source_on_cmd_line_program(py_source_to_interpret: str,
                                          stdin: ValueAssertion[StdinData] = no_stdin(),
                                          transformer: ValueAssertion[
                                              StringTransformer] = asrt_line_trans.is_identity_transformer()
                                          ) -> ValueAssertion[Program]:
    return matches_program(asrt_command.equals_execute_py_source_command(py_source_to_interpret),
                           stdin=stdin,
                           transformer=transformer)


class _MatchesProgramAssertion(ValueAssertionBase[Program]):
    def __init__(self,
                 command: ValueAssertion[Command],
                 stdin: ValueAssertion[StdinData],
                 transformer: ValueAssertion[StringTransformer],
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
