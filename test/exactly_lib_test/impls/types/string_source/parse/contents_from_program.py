import unittest
from typing import List, Callable, Dict, Mapping

from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, MultiSourceExpectation, \
    ExecutionExpectation, Expectation, ParseExpectation, prim_asrt__constant
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntax as string_source_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import integration_check
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.impls.types.test_resources import validation
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources import abstract_syntax as path_abs_stx
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.source.abstract_syntax_impls import OptionallyOnNewLine
from exactly_lib_test.test_resources.source.layout import LayoutSpec
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.types.program.test_resources import abstract_syntax as program_abs_stx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import \
    TransformableProgramAbsStxBuilder, ProgramAbsStx, TransformableProgramAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources import abstract_syntax as str_trans_abs_stx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext, \
    NON_EXISTING_SYSTEM_PROGRAM
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestSuccessfulScenariosWithProgramFromDifferentChannels),
        TestSymbolReferences(),
        TestFailingValidation(),
        unittest.makeSuite(TestNonZeroExitCode),
        unittest.makeSuite(TestUnableToExecute),
        unittest.makeSuite(TestSyntax),
    ])


class TestSymbolReferences(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        text_printed_by_program = StringConstantSymbolContext('STRING_TO_PRINT_SYMBOL', 'hello world')
        to_upper_transformer = TO_UPPER_TRANSFORMER_SYMBOL

        expected_output = text_printed_by_program.str_value.upper()

        transformed_program_output_contents_syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
            ProcOutputFile.STDOUT,
            program_abs_stx.TransformedProgramAbsStx(
                program_abs_stx.ProgramOfPythonInterpreterAbsStx.of_execute_python_src_string(
                    py_programs.single_line_pgm_that_prints_to(
                        ProcOutputFile.STDOUT,
                        text_printed_by_program.name__sym_ref_syntax
                    )
                ),
                to_upper_transformer.abs_stx_of_reference,
            )
        )
        symbols = SymbolContext.symbol_table_of_contexts([
            text_printed_by_program,
            to_upper_transformer,
        ])

        checker = integration_check.checker__w_arbitrary_file_relativities()
        # ACT & ASSERT #
        checker.check__abs_stx__wo_input__std_layouts_and_source_variants(
            self,
            OptionallyOnNewLine(transformed_program_output_contents_syntax),
            arrangement_w_tcds(
                symbols=symbols,
            ),
            MultiSourceExpectation.of_prim__const(
                symbol_references=asrt.matches_sequence([
                    text_printed_by_program.reference_assertion__any_data_type,
                    to_upper_transformer.reference_assertion,
                ]),
                primitive=asrt_string_source.matches__str__const(
                    expected_output,
                    may_depend_on_external_resources=True,
                )
            )
        )


class ProgramCase:
    def __init__(self,
                 name: str,
                 source: TransformableProgramAbsStx,
                 expected_reference: List[ValueAssertion[SymbolReference]]):
        self.name = name
        self.source = source
        self.expected_references = expected_reference


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


class TestSuccessfulScenariosWithProgramFromDifferentChannels(unittest.TestCase):
    def test_with_transformation(self):
        text_printed_by_program = 'the text printed by the program'
        transformer = TO_UPPER_TRANSFORMER_SYMBOL
        self._test(
            text_printed_by_program=text_printed_by_program,
            expected_file_contents=text_printed_by_program.upper(),
            make_arguments=lambda tcc: tcc.with_transformation(transformer.abs_stx_of_reference),
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
              additional_symbol_references: List[ValueAssertion[SymbolReference]],
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
                    program_abs_stx.ProgramOfSymbolReferenceAbsStx(program_that_executes_py_source_symbol.name),
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
                    checker.check__abs_stx__wo_input__std_layouts_and_source_variants__full_line_parse(
                        self,
                        OptionallyOnNewLine(syntax),
                        arrangement_w_tcds(
                            symbols=symbols,
                        ),
                        MultiSourceExpectation.of_prim__const(
                            symbol_references=asrt.matches_sequence(expected_symbol_references),
                            primitive=asrt_string_source.matches__str__const(
                                expected_file_contents,
                                may_depend_on_external_resources=True,
                            ),
                        )
                    )


class TestFailingValidation(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NArrEx(
                'pre SDS validation failure',
                RelOptionType.REL_HDS_CASE,
                validation.pre_sds_validation_fails__w_any_msg(),
            ),
            NArrEx(
                'post SDS validation failure',
                RelOptionType.REL_ACT,
                validation.post_sds_validation_fails__w_any_msg(),
            ),
        ]
        for case in cases:
            program_with_ref_to_non_existing_file = program_abs_stx.ProgramOfExecutableFileCommandLineAbsStx(
                path_abs_stx.RelOptPathAbsStx(case.arrangement, 'non-existing-file')
            )
            string_source_syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
                ProcOutputFile.STDOUT,
                program_with_ref_to_non_existing_file,
                ignore_exit_code=False,
            )

            # ACT & ASSERT #
            checker = integration_check.checker__w_arbitrary_file_relativities()
            with self.subTest(step=case.name):
                checker.check__abs_stx__wo_input__std_layouts_and_source_variants__full_line_parse(
                    self,
                    OptionallyOnNewLine(string_source_syntax),
                    arrangement_w_tcds(),
                    MultiSourceExpectation(
                        execution=ExecutionExpectation(
                            validation=case.expectation
                        )
                    )
                )


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
                            primitive=asrt_string_source.contents_raises_hard_error(
                                may_depend_on_external_resources=asrt.equals(True)
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


class TestNonZeroExitCode(unittest.TestCase):
    def test_syntax_layout_variants(self):
        # ARRANGE #
        exit_code_from_program = 1
        output_from_program = 'the output from the program'
        transformer = TO_UPPER_TRANSFORMER_SYMBOL

        sym_ref_program = program_abs_stx.ProgramOfSymbolReferenceAbsStx('PROGRAM_SYMBOL_NAME')
        program_builder = program_abs_stx.TransformableProgramAbsStxBuilder(
            program_abs_stx.ProgramOfSymbolReferenceAbsStx(sym_ref_program.symbol_name)
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
                            primitive=asrt_string_source.matches__str__const(
                                expected_program_output,
                                may_depend_on_external_resources=True,
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

        sym_ref_program = program_abs_stx.ProgramOfSymbolReferenceAbsStx('PROGRAM_SYMBOL_NAME')
        program_builder = program_abs_stx.TransformableProgramAbsStxBuilder(
            program_abs_stx.ProgramOfSymbolReferenceAbsStx(sym_ref_program.symbol_name)
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
        return asrt_string_source.contents_raises_hard_error(
            may_depend_on_external_resources=asrt.equals(True)
        )

    @staticmethod
    def _contents_is_output_from_program(contents_on_output_channel: str) -> ValueAssertion[StringSource]:
        return asrt_string_source.matches__str__const(
            contents_on_output_channel,
            may_depend_on_external_resources=True,
        )


class TestSyntax(unittest.TestCase):
    def test_string_transformer_should_be_parsed_as_simple_expression(self):
        the_layout = LayoutSpec.of_default()

        output_from_program = 'untransformed output from the program'

        sym_ref_program_syntax = program_abs_stx.ProgramOfSymbolReferenceAbsStx('PROGRAM_THAT_EXECUTES_PY_FILE')

        str_trans__unused = str_trans_abs_stx.StringTransformerSymbolReferenceAbsStx('UNUSED_TRANSFORMER')

        program_w_complex_str_trans_wo_parentheses = program_abs_stx.TransformedProgramAbsStx(
            program_abs_stx.ProgramOfSymbolReferenceAbsStx(sym_ref_program_syntax.symbol_name),
            str_trans_abs_stx.StringTransformerCompositionAbsStx(
                [
                    TO_UPPER_TRANSFORMER_SYMBOL.abs_stx_of_reference,
                    str_trans__unused,
                ],
                within_parens=False,
                allow_elements_on_separate_lines=False,
            )
        )
        expected_remaining_tokens = TokenSequence.concat([
            TokenSequence.singleton(str_trans_abs_stx.names.SEQUENCE_OPERATOR_NAME),
            str_trans__unused.tokenization(),
        ])
        expected_remaining_source = expected_remaining_tokens.layout(the_layout)

        checker = integration_check.checker__w_arbitrary_file_relativities()

        py_program_file = File('program.py',
                               py_programs.py_pgm_with_stdout_stderr_exit_code(
                                   exit_code=0,
                                   stdout_output=output_from_program,
                                   stderr_output=output_from_program,
                               ),
                               )
        py_file_rel_conf = rel_opt.conf_rel_any(RelOptionType.REL_HDS_CASE)
        py_file_conf = py_file_rel_conf.named_file_conf(py_program_file.name)

        program_symbol__that_executes_py_file = ProgramSymbolContext.of_sdv(
            sym_ref_program_syntax.symbol_name,
            program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
        )
        symbols = [
            program_symbol__that_executes_py_file,
            TO_UPPER_TRANSFORMER_SYMBOL,
        ]

        for output_file in ProcOutputFile:
            for ignore_exit_code in [False, True]:
                syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
                    output_file,
                    program_w_complex_str_trans_wo_parentheses,
                    ignore_exit_code=ignore_exit_code,
                )
                with self.subTest(output_file=output_file,
                                  ignore_exit_code=ignore_exit_code):
                    checker.check__abs_stx__wo_input(
                        self,
                        syntax,
                        arrangement_w_tcds(
                            symbols=SymbolContext.symbol_table_of_contexts(symbols),
                            tcds_contents=py_file_rel_conf.populator_for_relativity_option_root(
                                DirContents([py_program_file])
                            )
                        ),
                        Expectation(
                            ParseExpectation(
                                source=asrt_source.source_is_not_at_end(
                                    remaining_source=asrt.equals(expected_remaining_source)
                                ),
                                symbol_references=SymbolContext.references_assertion_of_contexts(symbols),

                            )
                        ),
                        the_layout,
                    )


TO_UPPER_TRANSFORMER_SYMBOL = StringTransformerSymbolContext.of_primitive(
    'TO_UPPER_TRANSFORMER_SYMBOL',
    string_transformers.to_uppercase(),
)
