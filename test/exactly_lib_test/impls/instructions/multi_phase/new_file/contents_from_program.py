import unittest
from typing import List, Callable, Dict, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.impls.instructions.multi_phase.new_file import parse as sut
from exactly_lib.symbol.sdv_structure import SymbolContainer, SymbolReference
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import abstract_syntax as instr_abs_stx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import common_test_cases
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import integration_check, parse_check
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.abstract_syntax import \
    ExplicitContentsVariantAbsStx
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.common_test_cases import \
    InvalidDestinationFileTestCasesData
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.defs import \
    ARBITRARY_ALLOWED_DST_FILE_RELATIVITY
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources.utils import \
    IS_FAILURE, IS_SUCCESS
from exactly_lib_test.impls.instructions.multi_phase.test_resources import instruction_embryo_check as embryo_check
from exactly_lib_test.impls.instructions.multi_phase.test_resources.instruction_embryo_check import \
    MultiSourceExpectation
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.string_transformer.test_resources import abstract_syntaxes as str_trans_abs_stx
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.symbol.test_resources.symbol_context import SymbolContext
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    non_hds_dir_contains_exactly
from exactly_lib_test.test_case.test_resources.arrangements import ArrangementWithSds
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.programs import shell_commands
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt, file_assertions as f_asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.types.path.test_resources import abstract_syntaxes as path_abs_stx
from exactly_lib_test.type_val_deps.types.path.test_resources.path import ConstantSuffixPathDdvSymbolContext
from exactly_lib_test.type_val_deps.types.program.test_resources import abstract_syntaxes as program_abs_stx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntax import PgmAndArgsAbsStx, \
    ProgramOfSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.program.test_resources.abstract_syntaxes import \
    ProgramAbsStx, TransformableProgramAbsStxBuilder, ProgramOfShellCommandLineAbsStx
from exactly_lib_test.type_val_deps.types.string.test_resources.string import StringSymbolContext
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.abstract_syntax import \
    StringTransformerSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext, \
    NON_EXISTING_SYSTEM_PROGRAM
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestCommonFailingScenariosDueToInvalidDestinationFile),
        unittest.makeSuite(TestFailDueInvalidSyntax),
        unittest.makeSuite(TestUnableToExecute),
        unittest.makeSuite(TestNonZeroExitCode),
        unittest.makeSuite(TestSuccessfulScenariosWithProgramFromDifferentChannels),
        TestSymbolUsages(),
        TestFailingValidation(),
    ])


class TestSymbolUsages(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        text_printed_by_program = StringSymbolContext.of_constant('STRING_TO_PRINT_SYMBOL', 'hello world')

        dst_file_symbol = ConstantSuffixPathDdvSymbolContext(
            'DST_FILE_SYMBOL',
            RelOptionType.REL_ACT,
            'dst-file-name.txt',
            sut.REL_OPT_ARG_CONF.options.accepted_relativity_variants,
        )

        to_upper_transformer = TO_UPPER_TRANSFORMER_SYMBOL

        transformed_program_output_contents_syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
            ProcOutputFile.STDOUT,
            program_abs_stx.FullProgramAbsStx(
                program_abs_stx.ProgramOfPythonInterpreterAbsStx.of_execute_python_src_string(
                    py_programs.single_line_pgm_that_prints_to(
                        ProcOutputFile.STDOUT,
                        text_printed_by_program.name__sym_ref_syntax
                    )
                ),
                transformation=to_upper_transformer.abs_stx_of_reference,
            )
        )
        instruction_syntax = instr_abs_stx.with_explicit_contents(
            dst_file_symbol.abs_stx_of_reference,
            transformed_program_output_contents_syntax
        )
        symbols = SymbolContext.symbol_table_of_contexts([
            dst_file_symbol,
            text_printed_by_program,
            to_upper_transformer,
        ])

        # ACT & ASSERT #
        checker = integration_check.checker(False)
        checker.check__abs_stx__std_layouts_and_source_variants(
            self,
            instruction_syntax,
            ArrangementWithSds(
                symbols=symbols,
            ),
            MultiSourceExpectation(
                main_result=IS_SUCCESS,
                symbol_usages=asrt.matches_sequence([
                    dst_file_symbol.reference_assertion__path_or_string,
                    text_printed_by_program.reference_assertion__any_data_type,
                    to_upper_transformer.reference_assertion,
                ]),
            )
        )


class ProgramCase:
    def __init__(self,
                 name: str,
                 source: PgmAndArgsAbsStx,
                 expected_reference: List[Assertion[SymbolReference]]):
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
              additional_symbol_references: List[Assertion[SymbolReference]],
              ):
        expected_file = fs.File('a-file-name.txt', expected_file_contents)

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

            for program_case in program_cases:
                program_syntax_builder = TransformableProgramAbsStxBuilder(program_case.source)
                program_syntax = make_arguments(program_syntax_builder)

                rel_opt_conf = ARBITRARY_ALLOWED_DST_FILE_RELATIVITY

                expected_symbol_references = program_case.expected_references + additional_symbol_references

                instruction_syntax = instr_abs_stx.with_explicit_contents(
                    rel_opt_conf.path_abs_stx_of_name(expected_file.name),
                    string_source_abs_stx.StringSourceOfProgramAbsStx(proc_output_file, program_syntax,
                                                                      ignore_exit_code=False)
                )

                with self.subTest(relativity_option_string=str(rel_opt_conf.option_argument),
                                  program=program_case.name,
                                  output_channel=proc_output_file):
                    integration_check.CHECKER__BEFORE_ACT.check__abs_stx__layout_and_source_variants(
                        self,
                        instruction_syntax,
                        ArrangementWithSds(
                            symbols=symbols,
                        ),
                        MultiSourceExpectation(
                            main_result=IS_SUCCESS,
                            side_effects_on_hds=f_asrt.dir_is_empty(),
                            symbol_usages=asrt.matches_sequence(expected_symbol_references),
                            main_side_effects_on_sds=non_hds_dir_contains_exactly(rel_opt_conf.root_dir__non_hds,
                                                                                  fs.DirContents([expected_file])),
                        )
                    )


class TestFailingValidation(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        cases = [
            NArrEx(
                'pre SDS validation failure SHOULD cause validation error',
                RelOptionType.REL_HDS_CASE,
                embryo_check.MultiSourceExpectation(validation=ValidationAssertions.pre_sds_fails__w_any_msg()),
            ),
            NArrEx(
                'post SDS validation failure SHOULD cause main error',
                RelOptionType.REL_ACT,
                embryo_check.MultiSourceExpectation(main_result=IS_FAILURE),
            ),
        ]
        for case in cases:
            program_with_ref_to_non_existing_file = program_abs_stx.ProgramOfExecutableFileCommandLineAbsStx(
                path_abs_stx.RelOptPathAbsStx(case.arrangement, 'non-existing-file')
            )
            instruction_syntax = instr_abs_stx.with_explicit_contents(
                path_abs_stx.DefaultRelPathAbsStx('dst-file'),
                string_source_abs_stx.StringSourceOfProgramAbsStx(ProcOutputFile.STDOUT,
                                                                  program_with_ref_to_non_existing_file,
                                                                  ignore_exit_code=False)
            )
            # ACT & ASSERT #
            for phase_is_after_act in [False, True]:
                checker = integration_check.checker(phase_is_after_act)
                with self.subTest(phase_is_after_act=phase_is_after_act,
                                  step=case.name):
                    checker.check__abs_stx__std_layouts_and_source_variants(
                        self,
                        instruction_syntax,
                        ArrangementWithSds(),
                        case.expectation,
                    )


class TestUnableToExecute(unittest.TestCase):
    def test_WHEN_program_is_non_non_existing_system_command_THEN_result_SHOULD_be_error_message(self):
        failing_program_builder = program_abs_stx.TransformableProgramAbsStxBuilder(
            program_abs_stx.ProgramOfSystemCommandLineAbsStx.of_str(NON_EXISTING_SYSTEM_PROGRAM)
        )
        transformer = TO_UPPER_TRANSFORMER_SYMBOL
        symbols = transformer.symbol_table

        cases = failing_program_builder.with_and_without_transformer_cases(transformer.abs_stx_of_reference)

        for transformation_case in cases:
            instruction_syntax = instr_abs_stx.with_explicit_contents(
                path_abs_stx.DefaultRelPathAbsStx('dst-file'),
                string_source_abs_stx.StringSourceOfProgramAbsStx(
                    ProcOutputFile.STDOUT,
                    transformation_case.value,
                    ignore_exit_code=False)
            )
            for phase_is_after_act in [False, True]:
                checker = integration_check.checker(phase_is_after_act)
                with self.subTest(phase_is_after_act=phase_is_after_act,
                                  transformation=transformation_case.name):
                    checker.check__abs_stx__std_layouts_and_source_variants(
                        self,
                        instruction_syntax,
                        ArrangementWithSds(
                            symbols=symbols,
                        ),
                        MultiSourceExpectation(
                            symbol_usages=asrt.anything_goes(),
                            main_result=IS_FAILURE,
                        )
                    )


class TestNonZeroExitCode(unittest.TestCase):
    def test_result_SHOULD_be_failure_WHEN_non_zero_exit_code_and_exit_code_is_not_ignored(self):
        self._check_exit_codes(
            exit_code_cases=[1, 69],
            ignore_exit_code=False,
            main_result=IS_FAILURE,
            expected_output_dir_contents=self._dir_is_empty
        )

    def test_result_SHOULD_be_success_WHEN_any_zero_exit_code_and_exit_code_is_ignored(self):
        self._check_exit_codes(
            exit_code_cases=[0, 1, 2, 69],
            ignore_exit_code=True,
            main_result=IS_SUCCESS,
            expected_output_dir_contents=self._dir_contains_exactly_created_file,
        )

    def _check_exit_codes(self,
                          exit_code_cases: List[int],
                          ignore_exit_code: bool,
                          main_result: Assertion[Optional[TextRenderer]],
                          expected_output_dir_contents: Callable[[str, str], DirContents],
                          ):
        # ARRANGE #
        destination_file_name = 'dst-file.txt'

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
        dst_file_rel_conf = ARBITRARY_ALLOWED_DST_FILE_RELATIVITY

        for output_file in ProcOutputFile:
            for exit_code in exit_code_cases:
                py_file = File('exit-with-hard-coded-exit-code.py',
                               py_programs.py_pgm_with_stdout_stderr_exit_code(
                                   exit_code=exit_code,
                                   stdout_output=program_output[ProcOutputFile.STDOUT],
                                   stderr_output=program_output[ProcOutputFile.STDERR],
                               ),
                               )

                py_file_conf = py_file_rel_conf.named_file_conf(py_file.name)
                dst_file_conf = dst_file_rel_conf.named_file_conf(destination_file_name)

                program_symbol = ProgramSymbolContext.of_sdv(
                    sym_ref_program.symbol_name,
                    program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
                )

                for program_case in program_cases:
                    instruction_syntax = instr_abs_stx.with_explicit_contents(
                        dst_file_conf.abstract_syntax,
                        string_source_abs_stx.StringSourceOfProgramAbsStx(
                            output_file,
                            program_case.syntax,
                            ignore_exit_code=ignore_exit_code)
                    )
                    expected_program_output = program_case.adapt_expected_program_output(program_output[output_file])
                    symbol_contexts = [program_symbol] + program_case.additional_symbols
                    # ACT && ASSERT #
                    for phase_is_after_act in [False, True]:
                        checker = integration_check.checker(phase_is_after_act)
                        with self.subTest(exit_code=exit_code,
                                          output_file=output_file,
                                          program=program_case.name,
                                          phase_is_after_act=phase_is_after_act):
                            checker.check__abs_stx__std_layouts_and_source_variants(
                                self,
                                instruction_syntax,
                                ArrangementWithSds(
                                    symbols=SymbolContext.symbol_table_of_contexts(symbol_contexts),
                                    tcds_contents=py_file_rel_conf.populator_for_relativity_option_root(
                                        DirContents([py_file])
                                    )
                                ),
                                MultiSourceExpectation(
                                    symbol_usages=SymbolContext.usages_assertion_of_contexts(symbol_contexts),
                                    main_result=main_result,
                                    main_side_effects_on_sds=dst_file_rel_conf.assert_root_dir_contains_exactly(
                                        expected_output_dir_contents(
                                            dst_file_conf.name,
                                            expected_program_output)
                                    ),
                                ),
                            )

    @staticmethod
    def _dir_is_empty(file_name: str, contents_on_output_channel: str) -> DirContents:
        return DirContents.empty()

    @staticmethod
    def _dir_contains_exactly_created_file(file_name: str, contents_on_output_channel: str) -> DirContents:
        return DirContents([File(file_name, contents_on_output_channel)])


class TestCommonFailingScenariosDueToInvalidDestinationFile(
    common_test_cases.TestCommonFailingScenariosDueToInvalidDestinationFileBase):
    def _file_contents_cases(self) -> InvalidDestinationFileTestCasesData:
        arbitrary_transformer = TO_UPPER_TRANSFORMER_SYMBOL

        symbols = arbitrary_transformer.symbol_table

        shell_contents_arguments_constructor = TransformableProgramAbsStxBuilder(
            ProgramOfShellCommandLineAbsStx.of_plain_string(
                shell_commands.command_that_exits_with_code(0)
            )
        )

        file_contents_cases = [
            NameAndValue(
                'contents of output from shell command / without transformation',
                _mk_explicit_contents(
                    shell_contents_arguments_constructor.without_transformation()
                )
            ),
            NameAndValue(
                'contents of output from shell command / with transformation',
                _mk_explicit_contents(
                    shell_contents_arguments_constructor.with_transformation(
                        arbitrary_transformer.abs_stx_of_reference)
                )
            ),
        ]

        return InvalidDestinationFileTestCasesData(
            file_contents_cases,
            symbols)


class TestFailDueInvalidSyntax(unittest.TestCase):
    def test_superfluous_arguments(self):
        program_w_superfluous_argument = program_abs_stx.FullProgramAbsStx(
            program_abs_stx.ARBITRARY_TRANSFORMABLE_PROGRAM,
            transformation=str_trans_abs_stx.StringTransformerCompositionAbsStx(
                [
                    StringTransformerSymbolReferenceAbsStx('str_trans_sym_1'),
                    StringTransformerSymbolReferenceAbsStx('str_trans_sym_1'),
                ],
                within_parens=False,
                allow_elements_on_separate_lines=False,
            )
        )
        for phase_is_after_act in [False, True]:
            for output_file in ProcOutputFile:
                for ignore_exit_code in [False, True]:
                    instruction_syntax = instr_abs_stx.with_explicit_contents(
                        ARBITRARY_ALLOWED_DST_FILE_RELATIVITY.path_abs_stx_of_name('dst-file'),
                        string_source_abs_stx.StringSourceOfProgramAbsStx(
                            output_file,
                            program_w_superfluous_argument,
                            ignore_exit_code=ignore_exit_code)
                    )
                    with self.subTest(output_file=output_file,
                                      phase_is_after_act=phase_is_after_act,
                                      ignore_exit_code=ignore_exit_code):
                        parse_check.check_invalid_syntax__abs_stx(
                            self,
                            instruction_syntax,
                        )


TO_UPPER_TRANSFORMER_SYMBOL = StringTransformerSymbolContext.of_primitive(
    'TO_UPPER_TRANSFORMER_SYMBOL',
    string_transformers.to_uppercase(),
)


def _mk_explicit_contents(program: ProgramAbsStx) -> ExplicitContentsVariantAbsStx:
    return ExplicitContentsVariantAbsStx(
        string_source_abs_stx.StringSourceOfProgramAbsStx(
            ProcOutputFile.STDOUT,
            program,
        )
    )
