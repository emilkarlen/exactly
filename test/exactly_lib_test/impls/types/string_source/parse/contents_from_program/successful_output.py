import unittest
from typing import List, Callable, Dict

from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, MultiSourceExpectation
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_full_line_expr_parse__s__nsc
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import integration_check
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.source.abstract_syntax_impls import OptionallyOnNewLine
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.program.test_resources import abstract_syntaxes as program_abs_stx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import PgmAndArgsAbsStx, \
    ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import \
    ProgramAbsStx, TransformableProgramAbsStxBuilder
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(TestSuccessfulScenariosWithProgramFromDifferentChannels)


class ProgramCase:
    def __init__(self,
                 name: str,
                 source: PgmAndArgsAbsStx,
                 expected_reference: List[Assertion[SymbolReference]]):
        self.name = name
        self.source = source
        self.expected_references = expected_reference


class TestSuccessfulScenariosWithProgramFromDifferentChannels(unittest.TestCase):
    def test_with_transformation(self):
        text_printed_by_program = 'the text printed by the program'
        transformer = TO_UPPER_TRANSFORMER_SYMBOL
        self._test(
            text_printed_by_program=text_printed_by_program,
            expected_file_contents=text_printed_by_program.upper(),
            make_arguments=lambda tcc: tcc.with_transformation(transformer.abstract_syntax),
            additional_symbols={transformer.name: transformer.symbol_table_container},
            additional_symbol_references=[transformer.reference_assertion]
        )

    def test_without_transformation(self):
        text_printed_by_program = 'the text printed by the program'
        self._test(
            text_printed_by_program=text_printed_by_program,
            expected_file_contents=text_printed_by_program,
            make_arguments=lambda tcc: tcc.without_transformation(),
            additional_symbols={},
            additional_symbol_references=[]
        )

    def _test(self,
              text_printed_by_program: str,
              expected_file_contents: str,
              make_arguments: Callable[[TransformableProgramAbsStxBuilder], ProgramAbsStx],
              additional_symbols: Dict[str, SymbolContainer],
              additional_symbol_references: List[Assertion[SymbolReference]],
              ):

        for proc_output_file in ProcOutputFile:
            python_source = py_programs.single_line_pgm_that_prints_to(proc_output_file,
                                                                       text_printed_by_program)

            program_that_executes_py_source_symbol = ProgramSymbolContext.of_sdv(
                'PROGRAM_THAT_EXECUTES_PY_SOURCE',
                program_sdvs.for_py_source_on_command_line(python_source)
            )

            program_cases = [
                ProgramCase(
                    'python interpreter',
                    program_abs_stx.ProgramOfPythonInterpreterAbsStx.of_execute_python_src_string(python_source),
                    []
                ),
                ProgramCase(
                    'symbol reference program',
                    ProgramOfSymbolReferenceAbsStx(program_that_executes_py_source_symbol.name),
                    [program_that_executes_py_source_symbol.reference_assertion],
                ),
            ]

            symbols_dict = {
                program_that_executes_py_source_symbol.name:
                    program_that_executes_py_source_symbol.symbol_table_container,
            }
            symbols_dict.update(additional_symbols)
            symbols = SymbolTable(symbols_dict)

            checker = integration_check.checker__w_arbitrary_file_relativities()
            for program_case in program_cases:
                program_syntax_builder = TransformableProgramAbsStxBuilder(program_case.source)
                program_syntax = make_arguments(program_syntax_builder)

                expected_symbol_references = program_case.expected_references + additional_symbol_references

                syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
                    proc_output_file, program_syntax,
                    ignore_exit_code=False,
                )
                with self.subTest(program=program_case.name,
                                  output_channel=proc_output_file):
                    checker.check__abs_stx__layouts__source_variants__wo_input(
                        self,
                        equivalent_source_variants__for_full_line_expr_parse__s__nsc,
                        OptionallyOnNewLine(syntax),
                        arrangement_w_tcds(
                            symbols=symbols,
                        ),
                        MultiSourceExpectation.of_prim__const(
                            symbol_references=asrt.matches_sequence(expected_symbol_references),
                            primitive=asrt_string_source.pre_post_freeze__matches_str__const_2(
                                expected_file_contents,
                                may_depend_on_external_resources=True,
                                frozen_may_depend_on_external_resources=asrt.anything_goes(),
                            ),
                        )
                    )


TO_UPPER_TRANSFORMER_SYMBOL = StringTransformerSymbolContext.of_primitive(
    'TO_UPPER_TRANSFORMER_SYMBOL',
    string_transformers.to_uppercase(),
)
