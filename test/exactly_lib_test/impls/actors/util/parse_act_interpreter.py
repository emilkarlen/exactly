import sys
import unittest
from typing import Sequence, List, Callable

from exactly_lib.impls.actors.util import parse_act_interpreter as sut
from exactly_lib.symbol.sdv_structure import SymbolDependentValue
from exactly_lib.tcfs.path_relativity import RelHdsOptionType
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.program.ddv.command import CommandDdv
from exactly_lib.type_val_deps.types.program.sdv.command import CommandSdv
from exactly_lib.type_val_prims.program.command import CommandDriver
from exactly_lib_test.impls.types.parse.test_resources.arguments_building import ArgumentElements
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants_for_consume_until_end_of_last_line2
from exactly_lib_test.impls.types.program.test_resources import arguments_building as pgm_args
from exactly_lib_test.impls.types.program.test_resources import program_arguments
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_resources.argument_renderer import ArgumentElementsRenderer
from exactly_lib_test.test_resources.value_assertions import file_assertions as asrt_path
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources.ddv_w_deps_assertions import \
    matches_dir_dependent_value
from exactly_lib_test.type_val_deps.sym_ref.test_resources.sdv_assertions import matches_sdv
from exactly_lib_test.type_val_deps.test_resources.w_str_rend import data_restrictions_assertions as asrt_rest
from exactly_lib_test.type_val_deps.types.list_.test_resources.list_ import ListConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources import reference_assertions
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.type_val_prims.program.test_resources import command_assertions as asrt_command
from exactly_lib_test.util.test_resources.quoting import surrounded_by_soft_quotes


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestWithoutExecution)


class TestWithoutExecution(unittest.TestCase):
    TCDS = fake_tcds()
    PARSER = sut.parser()

    def test_without_arguments(self):
        # ARRANGE #
        command_cases = _single_line_command_cases()
        for command_case in command_cases:
            expected_command_sdv = command_case.sdv_assertion(self.TCDS,
                                                              arguments=asrt.is_empty_sequence)
            for source_case in equivalent_source_variants_for_consume_until_end_of_last_line2(
                    command_case.source.as_arguments):
                with self.subTest(command=command_case.name,
                                  following_source_variant=source_case.name):
                    # ACT #
                    actual = self.PARSER.parse(command_case.source.as_remaining_source)
                    # ASSERT #
                    expected_command_sdv.apply_without_message(self, actual)

    def test_with_arguments(self):
        arg_wo_space = 'arg_wo_space'
        arg_w_space = 'an arg w space'
        arg_w_space__src = surrounded_by_soft_quotes(arg_w_space)
        string_symbol = StringConstantSymbolContext(
            'STRING_SYMBOL',
            'the string value',
            default_restrictions=asrt_rest.is_reference_restrictions__w_str_rendering(),
        )
        list_symbol = ListConstantSymbolContext(
            'LIST_SYMBOL',
            ['1st value', '2nd value'],
        )
        string_with_invalid_quoting = '"string without ending soft quote'
        arguments_cases = [
            ArgumentsCase(
                'one',
                source=ArgumentElements([arg_w_space__src]),
                expected_arguments=[arg_w_space],
            ),
            ArgumentsCase(
                'two',
                source=ArgumentElements([arg_wo_space, arg_w_space__src]),
                expected_arguments=[arg_wo_space, arg_w_space],
            ),
            ArgumentsCase(
                'string symbol reference',
                source=ArgumentElements([string_symbol.name__sym_ref_syntax]),
                expected_arguments=[string_symbol.str_value],
                symbols=[string_symbol],
            ),
            ArgumentsCase(
                'list symbol reference',
                source=ArgumentElements([list_symbol.name__sym_ref_syntax]),
                expected_arguments=list_symbol.constant_list,
                symbols=[list_symbol],
            ),
            ArgumentsCase(
                'list and string symbol reference',
                source=ArgumentElements([list_symbol.name__sym_ref_syntax,
                                         string_symbol.name__sym_ref_syntax]),
                expected_arguments=list_symbol.constant_list + [string_symbol.str_value],
                symbols=[list_symbol, string_symbol],
            ),
            ArgumentsCase(
                'special program argument',
                source=program_arguments.remaining_part_of_current_line_as_literal(
                    string_with_invalid_quoting
                ).as_argument_elements,
                expected_arguments=[string_with_invalid_quoting],
                symbols=[],
            ),
        ]
        # ARRANGE #
        command_cases = _single_line_command_cases()
        for command_case in command_cases:
            for arguments_case in arguments_cases:
                source_w_arguments = (
                    command_case.source.as_argument_elements
                        .followed_by(arguments_case.source)
                        .as_arguments
                )
                expected_arguments = asrt.matches_sequence([
                    asrt.equals(arg)
                    for arg in arguments_case.expected_arguments
                ])
                expected_command_sdv = command_case.sdv_assertion(self.TCDS,
                                                                  arguments=expected_arguments,
                                                                  arguments_symbols=arguments_case.symbols)
                for source_case in equivalent_source_variants_for_consume_until_end_of_last_line2(source_w_arguments):
                    with self.subTest(command=command_case.name,
                                      arguments=arguments_case.name,
                                      following_source_variant=source_case.name):
                        # ACT #
                        actual = self.PARSER.parse(source_case.input_value)
                        # ASSERT #
                        source_case.expected_value.apply_with_message(self, source_case.input_value, 'source')
                        expected_command_sdv.apply_with_message(self, actual, 'command')


class Case:
    def __init__(self,
                 name: str,
                 source: ArgumentElementsRenderer,
                 expected_command_driver: Callable[[TestCaseDs], Assertion[CommandDriver]],
                 symbols: Sequence[SymbolContext] = (),
                 ):
        self.name = name
        self.source = source
        self.symbols = symbols
        self.expected_command_driver = expected_command_driver

    def sdv_assertion(self,
                      tcds: TestCaseDs,
                      arguments: Assertion[Sequence[str]],
                      arguments_symbols: Sequence[SymbolContext] = (),
                      ) -> Assertion[SymbolDependentValue]:
        expected_command = asrt_command.matches_command(
            driver=self.expected_command_driver(tcds),
            arguments=arguments
        )
        symbols = tuple(self.symbols) + tuple(arguments_symbols)
        return matches_sdv(
            asrt.is_instance(CommandSdv),
            symbols=SymbolContext.symbol_table_of_contexts(symbols),
            references=SymbolContext.references_assertion_of_contexts(symbols),
            resolved_value=asrt.is_instance_with(
                CommandDdv,
                matches_dir_dependent_value(
                    lambda _: expected_command
                )
            ),
        )


def _single_line_command_cases() -> List[Case]:
    exe_file_name = 'executable-file'
    exe_file_relativity__explicit = rel_opt.conf_rel_hds(RelHdsOptionType.REL_HDS_ACT)
    exe_file_ddv__explicit_relativity = path_ddvs.of_rel_option(exe_file_relativity__explicit.relativity,
                                                                path_ddvs.constant_path_part(exe_file_name)
                                                                )

    exe_file_relativity__default = rel_opt.default_conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)
    exe_file_ddv__default_relativity = path_ddvs.of_rel_option(exe_file_relativity__default.relativity,
                                                               path_ddvs.constant_path_part(exe_file_name)
                                                               )

    system_program = 'the-system-program'
    system_program_symbol = StringConstantSymbolContext(
        'SYSTEM_PROGRAM_SYMBOL',
        system_program,
        default_restrictions=reference_assertions.IS_REFERENCE__STRING__W_ALL_INDIRECT_REFS_ARE_STRINGS,
    )

    return [
        Case(
            'executable file / explicit relativity',
            source=pgm_args.executable_file_command_line(
                exe_file_relativity__explicit.named_file_conf(exe_file_name).cl_argument.as_str
            ),
            expected_command_driver=lambda tcds: (
                asrt_command.matches_executable_file_command_driver(
                    asrt.equals(exe_file_ddv__explicit_relativity.value_of_any_dependency__d(tcds).primitive),
                )),
        ),
        Case(
            'executable file / default relativity',
            source=pgm_args.executable_file_command_line(
                exe_file_relativity__default.named_file_conf(exe_file_name).cl_argument.as_str
            ),
            expected_command_driver=lambda tcds: (
                asrt_command.matches_executable_file_command_driver(
                    asrt.equals(exe_file_ddv__default_relativity.value_of_any_dependency__d(tcds).primitive),
                )),
        ),
        Case(
            '-python',
            source=pgm_args.py_interpreter_command_line(),
            expected_command_driver=constant_assertion(
                asrt_command.matches_executable_file_command_driver(
                    asrt_path.path_as_str(asrt.equals(sys.executable)),
                )),
        ),
        Case(
            'system program',
            source=pgm_args.system_program_command_line(system_program),
            expected_command_driver=constant_assertion(
                asrt_command.matches_system_program_command_driver(
                    asrt.equals(system_program)
                ))
        ),
        Case(
            'system program / w symbol reference',
            source=pgm_args.system_program_command_line(system_program_symbol.name__sym_ref_syntax),
            symbols=[system_program_symbol],
            expected_command_driver=constant_assertion(
                asrt_command.matches_system_program_command_driver(
                    asrt.equals(system_program_symbol.str_value)
                ))
        ),
    ]


class ArgumentsCase:
    def __init__(self,
                 name: str,
                 source: ArgumentElements,
                 expected_arguments: Sequence[str],
                 symbols: Sequence[SymbolContext] = (),
                 ):
        self.name = name
        self.source = source
        self.expected_arguments = expected_arguments
        self.symbols = symbols


def constant_assertion(constant: Assertion[CommandDriver]) -> Callable[
    [TestCaseDs], Assertion[CommandDriver]]:
    def ret_val(tcds: TestCaseDs) -> Assertion[CommandDriver]:
        return constant

    return ret_val


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
