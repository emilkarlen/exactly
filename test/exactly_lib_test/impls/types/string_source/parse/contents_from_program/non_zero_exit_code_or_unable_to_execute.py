import unittest
from typing import List, Callable
from typing import Mapping

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, MultiSourceExpectation, \
    Expectation, ParseExpectation, prim_asrt__constant
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import integration_check
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.source.abstract_syntax_impls import OptionallyOnNewLine
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.types.program.test_resources import abstract_syntaxes as program_abs_stx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext, \
    NON_EXISTING_SYSTEM_PROGRAM
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_source.test_resources import contents_assertions as asrt_str_src_contents
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestNonZeroExitCode),
        unittest.makeSuite(TestUnableToExecute),
    ])


class TestUnableToExecute(unittest.TestCase):
    def test_WHEN_program_is_non_non_existing_system_command_THEN_result_SHOULD_be_hard_error(self):
        failing_program_builder = program_abs_stx.TransformableProgramAbsStxBuilder(
            program_abs_stx.ProgramOfSystemCommandLineAbsStx.of_str(NON_EXISTING_SYSTEM_PROGRAM)
        )
        transformer = TO_UPPER_TRANSFORMER_SYMBOL
        symbols = transformer.symbol_table

        cases = failing_program_builder.with_and_without_transformer_cases(transformer.abs_stx_of_reference)

        for ignore_exit_code in [False, True]:
            for transformation_case in cases:
                syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
                    ProcOutputFile.STDOUT,
                    transformation_case.value,
                    ignore_exit_code=ignore_exit_code,
                )
                checker = integration_check.checker__w_arbitrary_file_relativities()
                with self.subTest(transformation=transformation_case.name,
                                  ignore_exit_code=ignore_exit_code):
                    # ACT & ASSERT #
                    checker.check__abs_stx__wo_input__std_layouts_and_source_variants__full_line_parse(
                        self,
                        OptionallyOnNewLine(syntax),
                        arrangement_w_tcds(
                            symbols=symbols,
                        ),
                        MultiSourceExpectation.of_const(
                            symbol_references=asrt.anything_goes(),
                            primitive=asrt_string_source.pre_post_freeze(
                                asrt_str_src_contents.contents_raises_hard_error(
                                    may_depend_on_external_resources=asrt.equals(True)
                                ),
                                asrt_str_src_contents.contents_raises_hard_error__including_ext_deps(),
                            ),
                        )
                    )


class OutputFileCase:
    def __init__(self,
                 output_file: ProcOutputFile,
                 program_output: Mapping[ProcOutputFile, str],
                 ):
        self.output_file = output_file
        self.program_output = program_output


class ProgramAndSymbolsCase:
    def __init__(self,
                 name: str,
                 syntax: ProgramAbsStx,
                 additional_symbols: List[SymbolContext],
                 adapt_expected_program_output: Callable[[str], str],
                 ):
        self.name = name
        self.syntax = syntax
        self.additional_symbols = additional_symbols
        self.adapt_expected_program_output = adapt_expected_program_output


class TestNonZeroExitCode(unittest.TestCase):
    def test_syntax_layout_variants(self):
        # ARRANGE #
        exit_code_from_program = 1
        output_from_program = 'the output from the program'
        transformer = TO_UPPER_TRANSFORMER_SYMBOL

        sym_ref_program = ProgramOfSymbolReferenceAbsStx('PROGRAM_SYMBOL_NAME')
        program_builder = program_abs_stx.TransformableProgramAbsStxBuilder(
            ProgramOfSymbolReferenceAbsStx(sym_ref_program.symbol_name)
        )
        output_cases = [
            OutputFileCase(
                ProcOutputFile.STDOUT,
                {
                    ProcOutputFile.STDOUT: output_from_program,
                    ProcOutputFile.STDERR: '',
                }
            ),
            OutputFileCase(
                ProcOutputFile.STDERR,
                {
                    ProcOutputFile.STDOUT: '',
                    ProcOutputFile.STDERR: output_from_program,
                }
            ),
        ]
        program_cases = [
            ProgramAndSymbolsCase(
                'without transformation',
                program_builder.without_transformation(),
                [],
                adapt_expected_program_output=lambda s: s
            ),
            ProgramAndSymbolsCase(
                'with transformation',
                program_builder.with_transformation(transformer.abs_stx_of_reference),
                [transformer],
                adapt_expected_program_output=str.upper
            ),
        ]
        py_file_rel_conf = rel_opt.conf_rel_any(RelOptionType.REL_HDS_CASE)

        for output_case in output_cases:
            py_file = File('exit-with-hard-coded-exit-code.py',
                           py_programs.py_pgm_with_stdout_stderr_exit_code_2(
                               exit_code=exit_code_from_program,
                               output=output_case.program_output,
                           ),
                           )

            py_file_conf = py_file_rel_conf.named_file_conf(py_file.name)

            program_symbol = ProgramSymbolContext.of_sdv(
                sym_ref_program.symbol_name,
                program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
            )
            for program_case in program_cases:
                syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
                    output_case.output_file,
                    program_case.syntax,
                    ignore_exit_code=True,
                )
                expected_program_output = program_case.adapt_expected_program_output(output_from_program)
                symbol_contexts = [program_symbol] + program_case.additional_symbols
                # ACT && ASSERT #
                checker = integration_check.checker__w_arbitrary_file_relativities()
                with self.subTest(output_file=output_case.output_file,
                                  program=program_case.name):
                    checker.check__abs_stx__wo_input__std_layouts_and_source_variants__full_line_parse(
                        self,
                        OptionallyOnNewLine(syntax),
                        arrangement_w_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(symbol_contexts),
                            tcds_contents=py_file_rel_conf.populator_for_relativity_option_root(
                                DirContents([py_file])
                            )
                        ),
                        MultiSourceExpectation.of_const(
                            symbol_references=SymbolContext.references_assertion_of_contexts(symbol_contexts),
                            primitive=asrt_string_source.pre_post_freeze__matches_str__const_2(
                                expected_program_output,
                                may_depend_on_external_resources=True,
                                frozen_may_depend_on_external_resources=asrt.anything_goes(),
                            ),
                        ),
                    ),

    def test_result_SHOULD_be_failure_WHEN_non_zero_exit_code_and_exit_code_is_not_ignored(self):
        self._check_exit_codes(
            exit_code_cases=[1, 69],
            ignore_exit_code=False,
            expected_primitive=self._contents_access_raises_hard_error
        )

    def test_result_SHOULD_be_success_WHEN_any_zero_exit_code_and_exit_code_is_ignored(self):
        self._check_exit_codes(
            exit_code_cases=[0, 1, 2, 69],
            ignore_exit_code=True,
            expected_primitive=self._contents_is_output_from_program,
        )

    def _check_exit_codes(self,
                          exit_code_cases: List[int],
                          ignore_exit_code: bool,
                          expected_primitive: Callable[[str], ValueAssertion[StringSource]],
                          ):
        # ARRANGE #

        program_output = {
            ProcOutputFile.STDOUT: 'output on stdout',
            ProcOutputFile.STDERR: 'output on stderr',
        }
        transformer = TO_UPPER_TRANSFORMER_SYMBOL

        sym_ref_program = ProgramOfSymbolReferenceAbsStx('PROGRAM_SYMBOL_NAME')
        program_builder = program_abs_stx.TransformableProgramAbsStxBuilder(
            ProgramOfSymbolReferenceAbsStx(sym_ref_program.symbol_name)
        )
        program_cases = [
            ProgramAndSymbolsCase(
                'without transformation',
                program_builder.without_transformation(),
                [],
                adapt_expected_program_output=lambda s: s
            ),
            ProgramAndSymbolsCase(
                'with transformation',
                program_builder.with_transformation(transformer.abs_stx_of_reference),
                [transformer],
                adapt_expected_program_output=str.upper
            ),
        ]
        program_builder.with_and_without_transformer_cases(transformer.abs_stx_of_reference)

        py_file_rel_conf = rel_opt.conf_rel_any(RelOptionType.REL_HDS_CASE)

        for exit_code in exit_code_cases:
            py_file = File('exit-with-hard-coded-exit-code.py',
                           py_programs.py_pgm_with_stdout_stderr_exit_code(
                               exit_code=exit_code,
                               stdout_output=program_output[ProcOutputFile.STDOUT],
                               stderr_output=program_output[ProcOutputFile.STDERR],
                           ),
                           )

            py_file_conf = py_file_rel_conf.named_file_conf(py_file.name)

            program_symbol = ProgramSymbolContext.of_sdv(
                sym_ref_program.symbol_name,
                program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
            )
            for output_file in ProcOutputFile:
                for program_case in program_cases:
                    syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
                        output_file,
                        program_case.syntax,
                        ignore_exit_code=ignore_exit_code,
                    )
                    expected_program_output = program_case.adapt_expected_program_output(program_output[output_file])
                    symbol_contexts = [program_symbol] + program_case.additional_symbols
                    # ACT && ASSERT #
                    checker = integration_check.checker__w_arbitrary_file_relativities()
                    with self.subTest(exit_code=exit_code,
                                      output_file=output_file,
                                      program=program_case.name):
                        checker.check__abs_stx(
                            self,
                            syntax,
                            None,
                            arrangement_w_tcds(
                                symbols=SymbolContext.symbol_table_of_contexts(symbol_contexts),
                                tcds_contents=py_file_rel_conf.populator_for_relativity_option_root(
                                    DirContents([py_file])
                                )
                            ),
                            Expectation(
                                ParseExpectation(
                                    symbol_references=SymbolContext.references_assertion_of_contexts(symbol_contexts),
                                ),
                                primitive=prim_asrt__constant(
                                    expected_primitive(expected_program_output)
                                ),
                            ),
                        ),

    @staticmethod
    def _contents_access_raises_hard_error(contents_on_output_channel: str) -> ValueAssertion[StringSource]:
        return asrt_string_source.pre_post_freeze(
            asrt_str_src_contents.contents_raises_hard_error(
                may_depend_on_external_resources=asrt.equals(True)
            ),
            asrt_str_src_contents.contents_raises_hard_error__including_ext_deps(),
        )

    @staticmethod
    def _contents_is_output_from_program(contents_on_output_channel: str) -> ValueAssertion[StringSource]:
        return asrt_string_source.pre_post_freeze__matches_str__const_2(
            contents_on_output_channel,
            may_depend_on_external_resources=True,
            frozen_may_depend_on_external_resources=asrt.anything_goes(),
        )


TO_UPPER_TRANSFORMER_SYMBOL = StringTransformerSymbolContext.of_primitive(
    'TO_UPPER_TRANSFORMER_SYMBOL',
    string_transformers.to_uppercase(),
)
