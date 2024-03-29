import unittest

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, MultiSourceExpectation, \
    ExecutionExpectation, Expectation, ParseExpectation, arrangement_wo_tcds
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_full_line_expr_parse__s__nsc, equivalent_source_variants__for_expr_parse__s__nsc
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import integration_check
from exactly_lib_test.impls.types.string_transformer.test_resources import abstract_syntaxes as str_trans_abs_stx
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.source.abstract_syntax_impls import OptionallyOnNewLine
from exactly_lib_test.test_resources.source.layout import LayoutSpec
from exactly_lib_test.test_resources.source.token_sequence import TokenSequence
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.type_val_deps.types.path.test_resources import abstract_syntaxes as path_abs_stx
from exactly_lib_test.type_val_deps.types.program.test_resources import abstract_syntaxes as program_abs_stx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import ProgramOfSymbolReferenceAbsStx, \
    ProgramAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.argument_abs_stxs import ArgumentOfExistingPathAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.symbol_context import ProgramSymbolContext
from exactly_lib_test.type_val_deps.types.string_.test_resources.symbol_context import StringConstantSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.validation_cases import \
    failing_validation_cases
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSymbolReferences(),
        unittest.makeSuite(TestFailingValidation),
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
            program_abs_stx.FullProgramAbsStx(
                program_abs_stx.ProgramOfPythonInterpreterAbsStx.of_execute_python_src_string(
                    py_programs.single_line_pgm_that_prints_to(
                        ProcOutputFile.STDOUT,
                        text_printed_by_program.name__sym_ref_syntax
                    )
                ),
                transformation=to_upper_transformer.abstract_syntax,
            )
        )
        symbols = SymbolContext.symbol_table_of_contexts([
            text_printed_by_program,
            to_upper_transformer,
        ])

        checker = integration_check.checker__w_arbitrary_file_relativities()
        # ACT & ASSERT #
        checker.check__abs_stx__layouts__std_source_variants__wo_input(
            self,
            OptionallyOnNewLine(transformed_program_output_contents_syntax),
            arrangement_w_tcds(
                symbols=symbols,
            ),
            MultiSourceExpectation.of_prim__const(
                symbol_references=asrt.matches_sequence([
                    text_printed_by_program.reference_assertion__w_str_rendering,
                    to_upper_transformer.reference_assertion,
                ]),
                primitive=asrt_string_source.pre_post_freeze__matches_str__const_2(
                    expected_output,
                    may_depend_on_external_resources=True,
                    frozen_may_depend_on_external_resources=asrt.anything_goes(),
                )
            )
        )


class TestFailingValidation(unittest.TestCase):
    def test_non_transformer_components(self):
        # ARRANGE #
        relativity_cases = [
            NArrEx(
                'pre SDS validation failure',
                RelOptionType.REL_HDS_CASE,
                ValidationAssertions.pre_sds_fails__w_any_msg(),
            ),
            NArrEx(
                'post SDS validation failure',
                RelOptionType.REL_ACT,
                ValidationAssertions.post_sds_fails__w_any_msg(),
            ),
        ]

        def make_pgm_w_ref_to_executable_file(relativity: RelOptionType) -> ProgramAbsStx:
            return program_abs_stx.ProgramOfExecutableFileCommandLineAbsStx(
                path_abs_stx.RelOptPathAbsStx(relativity, 'non-existing-file')
            )

        def make_pgm_w_ref_to_stdin_file(relativity: RelOptionType) -> ProgramAbsStx:
            return program_abs_stx.FullProgramAbsStx(
                program_abs_stx.ProgramOfSystemCommandLineAbsStx.of_str(
                    'a-system-command'
                ),
                stdin=string_source_abs_stx.StringSourceOfFileAbsStx(
                    path_abs_stx.RelOptPathAbsStx(relativity, 'non-existing-file')
                )
            )

        def make_pgm_w_ref_to_argument_file(relativity: RelOptionType) -> ProgramAbsStx:
            return program_abs_stx.ProgramOfSystemCommandLineAbsStx.of_str(
                'a-system-command',
                [
                    ArgumentOfExistingPathAbsStx(
                        path_abs_stx.RelOptPathAbsStx(relativity, 'non-existing-file')
                    )
                ]
            )

        program_cases = [
            NameAndValue(
                'missing executable file',
                make_pgm_w_ref_to_executable_file,
            ),
            NameAndValue(
                'missing argument file',
                make_pgm_w_ref_to_argument_file,
            ),
            NameAndValue(
                'missing stdin file',
                make_pgm_w_ref_to_stdin_file,
            ),
        ]
        for relativity_case in relativity_cases:
            for program_case in program_cases:
                string_source_syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
                    ProcOutputFile.STDOUT,
                    program_case.value(relativity_case.arrangement),
                    ignore_exit_code=False,
                )

                # ACT & ASSERT #
                checker = integration_check.checker__w_arbitrary_file_relativities()
                with self.subTest(step=relativity_case.name,
                                  program=program_case.name):
                    checker.check__abs_stx__layouts__source_variants__wo_input(
                        self,
                        equivalent_source_variants__for_full_line_expr_parse__s__nsc,
                        OptionallyOnNewLine(string_source_syntax),
                        arrangement_w_tcds(),
                        MultiSourceExpectation(
                            execution=ExecutionExpectation(
                                validation=relativity_case.expectation
                            )
                        )
                    )

    def test_transformer_component(self):
        checker = integration_check.checker__w_arbitrary_file_relativities()
        for validation_case in failing_validation_cases():
            transformer_symbol = validation_case.value.symbol_context
            program_syntax = program_abs_stx.FullProgramAbsStx(
                program_abs_stx.ProgramOfSystemCommandLineAbsStx.of_str(
                    'a-system-command'
                ),
                transformation=transformer_symbol.abstract_syntax,
            )
            string_source_syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
                ProcOutputFile.STDOUT,
                program_syntax,
                ignore_exit_code=False,
            )
            with self.subTest(validation_case.name):
                checker.check__abs_stx__layouts__source_variants__wo_input(
                    self,
                    equivalent_source_variants__for_expr_parse__s__nsc,
                    OptionallyOnNewLine(string_source_syntax),
                    arrangement_wo_tcds(
                        symbols=transformer_symbol.symbol_table
                    ),
                    MultiSourceExpectation(
                        symbol_references=transformer_symbol.references_assertion,
                        execution=ExecutionExpectation(
                            validation=validation_case.value.expectation
                        )
                    )
                )


class TestSyntax(unittest.TestCase):
    def test_string_transformer_should_be_parsed_as_simple_expression(self):
        the_layout = LayoutSpec.of_default()

        output_from_program = 'untransformed output from the program'

        sym_ref_program_syntax = ProgramOfSymbolReferenceAbsStx('PROGRAM_THAT_EXECUTES_PY_FILE')

        str_trans__unused = StringTransformerSymbolReferenceAbsStx('UNUSED_TRANSFORMER')

        program_w_complex_str_trans_wo_parentheses = program_abs_stx.FullProgramAbsStx(
            ProgramOfSymbolReferenceAbsStx(sym_ref_program_syntax.symbol_name),
            transformation=str_trans_abs_stx.StringTransformerCompositionAbsStx(
                [
                    TO_UPPER_TRANSFORMER_SYMBOL.abstract_syntax,
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
