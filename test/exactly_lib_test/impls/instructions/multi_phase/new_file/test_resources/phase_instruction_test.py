import unittest

from exactly_lib.impls.instructions.multi_phase.new_file import parse, defs
from exactly_lib.tcfs.path_relativity import RelOptionType, RelHdsOptionType, RelNonHdsOptionType
from exactly_lib.test_case.phases.common import TestCaseInstructionWithSymbols
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources import \
    configuration as tc_configuration
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase, TestCaseWithConfiguration
from exactly_lib_test.impls.instructions.multi_phase.new_file.test_resources import abstract_syntax as instr_abs_stx
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__consume_last_line__abs_stx
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes as string_source_abs_stx
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.impls.types.test_resources.path_arg_with_relativity import PathArgumentWithRelativity
from exactly_lib_test.impls.types.test_resources.relativity_options import conf_rel_any, conf_rel_hds, \
    conf_rel_non_hds
from exactly_lib_test.symbol.test_resources import symbol_reference_assertions as asrt_sym_ref
from exactly_lib_test.tcfs.test_resources.sds_check.sds_contents_check import \
    non_hds_dir_contains_exactly
from exactly_lib_test.test_resources.files import file_structure as fs
from exactly_lib_test.test_resources.files.file_structure import DirContents, File
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.source import layout as tokens_layout
from exactly_lib_test.test_resources.source.abstract_syntax import AbstractSyntax
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR
from exactly_lib_test.test_resources.test_utils import NArrEx
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.data.test_resources.concrete_restriction_assertion import \
    equals_data_type_reference_restrictions
from exactly_lib_test.type_val_deps.types.path.test_resources import abstract_syntaxes as path_abs_stx
from exactly_lib_test.type_val_deps.types.path.test_resources.abstract_syntax import PathSymbolReferenceAbsStx
from exactly_lib_test.type_val_deps.types.path.test_resources.path import path_or_string_reference_restrictions
from exactly_lib_test.type_val_deps.types.program.test_resources import abstract_syntaxes as program_abs_stx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources import abstract_syntax as str_trans_abs_stx
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.assertions import \
    is_reference_to_string_transformer__usage
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.string_transformers import \
    StringTransformerSdvConstantTestImpl
from exactly_lib_test.type_val_deps.types.string_transformer.test_resources.symbol_context import \
    StringTransformerSymbolContext
from exactly_lib_test.type_val_prims.string_transformer.test_resources.string_transformers import \
    to_uppercase


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    test_case_constructors = [
        TestSymbolUsages,
        TestContentsFromExistingFile_Successfully,

        TestContentsFromOutputOfProgram_Successfully,

        TestValidation,
        TestHardError_DueTo_NonZeroExitCodeFromProgram,
        TestContentsFromOutputOfProgram_SuccessfullyWithIgnoredNonZeroExitCode,
    ]
    if conf.phase_is_after_act():
        test_case_constructors.append(TestParseShouldSucceedWhenRelativityOfSourceIsRelResult)
    else:
        test_case_constructors.append(TestParseShouldFailWhenRelativityOfSourceIsRelResult)

    return tc_configuration.suite_for_cases(conf, test_case_constructors)


class TestSymbolUsages(TestCaseWithConfiguration):
    def runTest(self):
        to_upper_transformer = NameAndValue('TRANSFORMER_SYMBOL',
                                            StringTransformerSdvConstantTestImpl(to_uppercase()))

        src_file = fs.File('src-file.txt', 'contents of source file')
        src_file_symbol = NameAndValue('SRC_FILE_SYMBOL', src_file.name)

        expected_dst_file = fs.File('dst-file-name.txt', src_file.contents.upper())
        dst_file_symbol = NameAndValue('DST_FILE_SYMBOL', expected_dst_file.name)

        transformed_file_syntax = string_source_abs_stx.TransformedStringSourceAbsStx(
            string_source_abs_stx.StringSourceOfFileAbsStx(
                PathSymbolReferenceAbsStx(src_file_symbol.name)),
            str_trans_abs_stx.StringTransformerSymbolReferenceAbsStx(to_upper_transformer.name)
        )
        instruction_syntax = instr_abs_stx.with_explicit_contents(
            PathSymbolReferenceAbsStx(dst_file_symbol.name),
            transformed_file_syntax,
        )

        # ACT #
        for layout_case in tokens_layout.STANDARD_LAYOUT_SPECS:
            with self.subTest(layout_case.name):
                instruction = self.conf.parse_checker.parse__abs_stx(self,
                                                                     instruction_syntax,
                                                                     layout_case.value)
                assert isinstance(instruction, TestCaseInstructionWithSymbols)  # Sanity check

                # ASSERT #

                expected_symbol_usages = [

                    asrt_sym_ref.matches_reference_2(
                        dst_file_symbol.name,
                        equals_data_type_reference_restrictions(
                            path_or_string_reference_restrictions(
                                parse.REL_OPT_ARG_CONF.options.accepted_relativity_variants)
                        )
                    ),

                    asrt_sym_ref.matches_reference_2(
                        src_file_symbol.name,
                        equals_data_type_reference_restrictions(
                            path_or_string_reference_restrictions(
                                defs.src_rel_opt_arg_conf_for_phase(
                                    self.conf.phase_is_after_act()).accepted_relativity_variants))
                    ),

                    is_reference_to_string_transformer__usage(to_upper_transformer.name),
                ]
                expected_symbol_references = asrt.matches_sequence(expected_symbol_usages)
                expected_symbol_references.apply_without_message(self,
                                                                 instruction.symbol_usages())


class TestParseShouldFailWhenRelativityOfSourceIsRelResult(TestCaseWithConfiguration):
    def runTest(self):
        # ARRANGE #
        instruction_syntax = instruction_syntax_for_src_file_rel_result()
        # ACT #
        self.conf.parse_checker.check_invalid_syntax__abs_stx(self, instruction_syntax)


class TestParseShouldSucceedWhenRelativityOfSourceIsRelResult(TestCaseWithConfiguration):
    def runTest(self):
        # ARRANGE #
        instruction_syntax = instruction_syntax_for_src_file_rel_result()

        for layout_case in tokens_layout.STANDARD_LAYOUT_SPECS:
            with self.subTest(layout_case.name):
                # ACT #
                instruction = self.conf.parse_checker.parse__abs_stx(self,
                                                                     instruction_syntax,
                                                                     layout_case.value)
                # ASSERT #
                assert isinstance(instruction, TestCaseInstructionWithSymbols)  # Sanity check


class TestContentsFromExistingFile_Successfully(TestCaseWithConfiguration):
    def runTest(self):
        # ARRANGE #

        src_file = fs.File('source-file.txt', 'contents of source file')
        src_rel_opt_conf = conf_rel_hds(RelHdsOptionType.REL_HDS_CASE)

        expected_file = fs.File('a-file-name.txt', src_file.contents.upper())
        dst_rel_opt_conf = conf_rel_non_hds(RelNonHdsOptionType.REL_ACT)

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'TRANSFORMER_SYMBOL',
            to_uppercase(),
        )
        symbols = to_upper_transformer.symbol_table

        transformed_file_syntax = string_source_abs_stx.TransformedStringSourceAbsStx(
            string_source_abs_stx.StringSourceOfFileAbsStx(
                src_rel_opt_conf.path_abs_stx_of_name(src_file.name)),
            to_upper_transformer.abstract_syntax,
        )
        instruction_syntax = instr_abs_stx.with_explicit_contents(
            dst_rel_opt_conf.path_abs_stx_of_name(expected_file.name),
            transformed_file_syntax,
        )

        expected_non_hds_contents = dst_rel_opt_conf.assert_root_dir_contains_exactly(fs.DirContents([expected_file]))

        # ACT & ASSERT #

        for source_case in equivalent_source_variants__with_source_check__consume_last_line__abs_stx(
                instruction_syntax):
            with self.subTest(source_case.name):
                self.conf.run_test(
                    self,
                    source_case.value.source,
                    self.conf.arrangement(
                        pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                        tcds_contents=src_rel_opt_conf.populator_for_relativity_option_root(
                            DirContents([src_file])),
                        symbols=symbols,
                    ),
                    self.conf.expect_success(
                        source=source_case.value.expectation,
                        symbol_usages=asrt.matches_sequence([
                            to_upper_transformer.reference_assertion,
                        ]),
                        main_side_effects_on_sds=expected_non_hds_contents,
                    )
                )


class TestContentsFromOutputOfProgram_Successfully(TestCaseWithConfiguration):
    def runTest(self):
        text_printed_by_program = 'single line of output'

        expected_file_contents = text_printed_by_program.upper()
        expected_file = fs.File('dst-file.txt', expected_file_contents)

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'TO_UPPER_CASE',
            to_uppercase(),
        )
        symbols = to_upper_transformer.symbol_table

        dst_rel_opt_conf = conf_rel_non_hds(RelNonHdsOptionType.REL_TMP)

        program_syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
            ProcOutputFile.STDOUT,
            program_abs_stx.FullProgramAbsStx(
                program_abs_stx.ProgramOfPythonInterpreterAbsStx.of_execute_python_src_string(
                    py_programs.single_line_pgm_that_prints_to(
                        ProcOutputFile.STDOUT,
                        text_printed_by_program
                    )
                ),
                transformation=to_upper_transformer.abstract_syntax,
            )
        )
        instruction_syntax = instr_abs_stx.with_explicit_contents(
            dst_rel_opt_conf.path_abs_stx_of_name(expected_file.name),
            program_syntax,
        )

        for source_case in equivalent_source_variants__with_source_check__consume_last_line__abs_stx(
                instruction_syntax):
            with self.subTest(source_case.name):
                self.conf.run_test(
                    self,
                    source_case.value.source,
                    self.conf.arrangement(
                        pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                        symbols=symbols
                    ),
                    self.conf.expect_success(
                        source=source_case.value.expectation,
                        symbol_usages=asrt.matches_sequence([
                            to_upper_transformer.reference_assertion,
                        ]),
                        main_side_effects_on_sds=non_hds_dir_contains_exactly(
                            dst_rel_opt_conf.root_dir__non_hds,
                            fs.DirContents([expected_file])),
                    ))


class TestContentsFromOutputOfProgram_SuccessfullyWithIgnoredNonZeroExitCode(TestCaseWithConfiguration):
    def runTest(self):
        non_zero_exit_code = 1
        text_printed_by_program = 'the output from the program'

        py_file = File('exit-with-hard-coded-exit-code.py',
                       py_programs.py_pgm_with_stdout_stderr_exit_code(
                           stdout_output=text_printed_by_program,
                           stderr_output='',
                           exit_code=non_zero_exit_code,
                       ),
                       )

        expected_file = fs.File(
            'dst-file.txt',
            text_printed_by_program.upper(),
        )

        to_upper_transformer = StringTransformerSymbolContext.of_primitive(
            'TO_UPPER_CASE',
            to_uppercase(),
        )
        symbols = to_upper_transformer.symbol_table

        py_src_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_HDS_CASE)
        dst_file_rel_opt_conf = conf_rel_non_hds(RelNonHdsOptionType.REL_TMP)

        program_string_source_syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
            ProcOutputFile.STDOUT,
            program_abs_stx.FullProgramAbsStx(
                program_abs_stx.ProgramOfPythonInterpreterAbsStx.of_execute_python_src_file(
                    py_src_file_rel_opt_conf.path_abs_stx_of_name(py_file.name)
                ),
                transformation=to_upper_transformer.abstract_syntax,
            ),
            ignore_exit_code=True,
        )
        instruction_syntax = instr_abs_stx.with_explicit_contents(
            dst_file_rel_opt_conf.path_abs_stx_of_name(expected_file.name),
            program_string_source_syntax,
        )

        for source_case in equivalent_source_variants__with_source_check__consume_last_line__abs_stx(
                instruction_syntax):
            with self.subTest(source_case.name):
                self.conf.run_test(
                    self,
                    source_case.value.source,
                    self.conf.arrangement(
                        pre_contents_population_action=SETUP_CWD_INSIDE_SDS_BUT_NOT_A_SDS_DIR,
                        symbols=symbols,
                        tcds_contents=py_src_file_rel_opt_conf.populator_for_relativity_option_root(
                            DirContents([py_file])
                        )
                    ),
                    self.conf.expect_success(
                        source=source_case.value.expectation,
                        symbol_usages=asrt.matches_sequence([
                            to_upper_transformer.reference_assertion,
                        ]),
                        main_side_effects_on_sds=non_hds_dir_contains_exactly(dst_file_rel_opt_conf.root_dir__non_hds,
                                                                              fs.DirContents([expected_file])),
                    )
                )


class TestHardError_DueTo_NonZeroExitCodeFromProgram(TestCaseWithConfiguration):
    def runTest(self):
        non_zero_exit_code = 1
        program_string_source_syntax = string_source_abs_stx.StringSourceOfProgramAbsStx(
            ProcOutputFile.STDOUT,
            program_abs_stx.ProgramOfPythonInterpreterAbsStx.of_execute_python_src_string(
                py_programs.single_line_pgm_that_exists_with(non_zero_exit_code)
            ),
            ignore_exit_code=False,
        )
        instruction_syntax = instr_abs_stx.with_explicit_contents(
            conf_rel_non_hds(RelNonHdsOptionType.REL_TMP).path_abs_stx_of_name('dst.txt'),
            program_string_source_syntax,
        )

        for source_case in equivalent_source_variants__with_source_check__consume_last_line__abs_stx(
                instruction_syntax):
            with self.subTest(source_case.name):
                self.conf.run_test(
                    self,
                    source_case.value.source,
                    self.conf.arrangement(),
                    self.conf.expect_hard_error_of_main__any(),
                )


class TestValidation(TestCaseWithConfiguration):
    def runTest(self):
        # ARRANGE #
        dst_file = PathArgumentWithRelativity('dst-file.txt',
                                              conf_rel_any(RelOptionType.REL_TMP))

        cases = [
            NArrEx(
                'pre sds validation failure SHOULD cause validation error',
                RelOptionType.REL_HDS_CASE,
                self.conf.expect_failing_validation_pre_sds(),
            ),
            NArrEx(
                'post sds validation failure SHOULD cause main hard error',
                RelOptionType.REL_ACT,
                self.conf.expect_hard_error_of_main__any(),
            ),
        ]
        for case in cases:
            src_file_rel_conf = conf_rel_any(case.arrangement)
            instruction_syntax = instr_abs_stx.with_explicit_contents(
                dst_file.argument_abs_stx,
                string_source_abs_stx.StringSourceOfFileAbsStx(
                    src_file_rel_conf.path_abs_stx_of_name('non-existing-source-file.txt')
                ),
            )

            for source_case in equivalent_source_variants__with_source_check__consume_last_line__abs_stx(
                    instruction_syntax):
                with self.subTest(validation_case=case.name,
                                  source_case=source_case.name):
                    # ACT & ASSERT#
                    self.conf.run_test(
                        self,
                        source_case.value.source,
                        arrangement=
                        self.conf.arrangement(),
                        expectation=
                        case.expectation,
                    )


def instruction_syntax_for_src_file_rel_result() -> AbstractSyntax:
    src_file_arg = path_abs_stx.PathWConstNameAbsStx.of_rel_opt(RelOptionType.REL_RESULT, 'src-file.txt')
    dst_file_arg = path_abs_stx.PathWConstNameAbsStx.of_rel_opt(RelOptionType.REL_ACT, 'dst-file.txt')

    return instr_abs_stx.with_explicit_contents(
        dst_file_arg,
        string_source_abs_stx.StringSourceOfFileAbsStx(src_file_arg),
    )
