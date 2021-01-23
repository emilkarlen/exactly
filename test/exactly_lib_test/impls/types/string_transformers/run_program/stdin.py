import unittest

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, Expectation, MultiSourceExpectation
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import prim_asrt__constant
from exactly_lib_test.impls.types.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__for_expr_parse__s__nsc
from exactly_lib_test.impls.types.program.parse_program.test_resources import pgm_and_args_cases
from exactly_lib_test.impls.types.program.test_resources import arguments_building as program_args
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.program.test_resources.stdin_test_setups import SingleStdinOfProgramTestSetup, \
    MultipleStdinOfProgramTestSetup, StdinCheckWithProgramWExitCode0ForSuccess
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_syntax as args
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check
from exactly_lib_test.impls.types.string_transformers.test_resources.abstract_syntaxes import RunProgramAbsStx
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_source.test_resources import contents_assertions as asrt_contents
from exactly_lib_test.type_val_prims.string_transformer.test_resources import \
    string_transformer_assertions as asrt_string_transformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestStdinIsGivenToCommandExecutor),
        TestNonEmptyStdinViaExecution(),
        TestStdinShouldBeContentsOfModel()
    ])


class TestStdinIsGivenToCommandExecutor(unittest.TestCase):
    def test_stdin_contains_model_contents_WHEN_program_do_not_define_stdin(self):
        # ARRANGE #
        test_setup = SingleStdinOfProgramTestSetup(self, exit_code=0)

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            with self.subTest(pgm_and_args_case.name):
                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_FULL.check__abs_stx(
                    self,
                    RunProgramAbsStx(
                        pgm_and_args_case.pgm_and_args,
                    ),
                    model_constructor.of_str(self, test_setup.STRING_SOURCE_CONTENTS),
                    arrangement_w_tcds(
                        symbols=pgm_and_args_case.symbol_table,
                        process_execution=test_setup.proc_exe_env__w_stdin_check,
                        tcds_contents=pgm_and_args_case.tcds,
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=pgm_and_args_case.references_assertion,
                        ),
                        execution=EXECUTION_OUTPUT_IS_EMPTY,
                        primitive=PRIMITIVE_IS_NOT_IDENTITY_TRANSFORMATION,
                    )
                )

    def test_stdin_is_concatenation_of_model_and_program_stdin_WHEN_program_defines_single_stdin(self):
        # ARRANGE #
        model_contents = '\n'.join(('the', 'contents', 'of', 'the', 'model'))
        test_setup = SingleStdinOfProgramTestSetup(self, exit_code=0,
                                                   additional_stdin=model_contents)

        for pgm_and_args_case in pgm_and_args_cases.cases_w_and_wo_argument_list__including_program_reference():
            with self.subTest(pgm_and_args_case.name):
                # ACT & ASSERT #
                integration_check.CHECKER__PARSE_FULL.check__abs_stx__std_layouts__mk_source_variants(
                    self,
                    equivalent_source_variants__for_expr_parse__s__nsc,
                    RunProgramAbsStx(
                        test_setup.program_w_stdin_syntax(pgm_and_args_case.pgm_and_args),
                    ),
                    model_constructor.of_str(self, model_contents),
                    arrangement_w_tcds(
                        symbols=pgm_and_args_case.symbol_table,
                        process_execution=test_setup.proc_exe_env__w_stdin_check,
                        tcds_contents=pgm_and_args_case.tcds,
                    ),
                    MultiSourceExpectation(
                        symbol_references=pgm_and_args_case.references_assertion,
                        execution=EXECUTION_OUTPUT_IS_EMPTY,
                        primitive=PRIMITIVE_IS_NOT_IDENTITY_TRANSFORMATION,
                    ),
                )

    def test_stdin_is_concatenation_of_model_and_program_stdin_WHEN_program_defines_multiple_stdin(self):
        # ARRANGE #
        model_contents = '\n'.join(('the', 'contents', 'of', 'the', 'model'))
        test_setup = MultipleStdinOfProgramTestSetup(self, exit_code=0,
                                                     additional_stdin=model_contents)
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check__abs_stx__std_layouts__mk_source_variants(
            self,
            equivalent_source_variants__for_expr_parse__s__nsc,
            RunProgramAbsStx(
                test_setup.program_w_stdin_syntax,
            ),
            model_constructor.of_str(self, model_contents),
            arrangement_w_tcds(
                symbols=test_setup.program_symbol.symbol_table,
                process_execution=test_setup.proc_exe_env__w_stdin_check,
            ),
            MultiSourceExpectation(
                symbol_references=test_setup.program_symbol.references_assertion,
                execution=EXECUTION_OUTPUT_IS_EMPTY,
                primitive=PRIMITIVE_IS_NOT_IDENTITY_TRANSFORMATION,
            ),
        )


class TestNonEmptyStdinViaExecution(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        model_contents = '\n'.join(('the', 'contents', 'of', 'the', 'model'))
        test_setup = StdinCheckWithProgramWExitCode0ForSuccess()
        # ACT & ASSERT #
        integration_check.CHECKER__PARSE_FULL.check__abs_stx(
            self,
            RunProgramAbsStx(
                test_setup.program_that_checks_stdin__syntax('the contents of stdin',
                                                             model_contents),
            ),
            model_constructor.of_str(self, model_contents),
            arrangement_w_tcds(
                tcds_contents=test_setup.tcds_contents,
            ),
            Expectation(
                execution=EXECUTION_OUTPUT_IS_EMPTY,
                primitive=PRIMITIVE_IS_NOT_IDENTITY_TRANSFORMATION,
            ),
        )


class TestStdinShouldBeContentsOfModel(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        py_file = File('copy_-stdin.py',
                       py_programs.py_pgm_that_copies_stdin_to_stdout())

        py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
        py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

        program_symbol = ProgramSymbolContext.of_sdv(
            'PROGRAM_THAT_EXECUTES_PY_FILE',
            program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
        )

        input_model_lines = [
            'the\n',
            'input\n',
            'model',
        ]
        for with_ignored_exit_code in [False, True]:
            with self.subTest(with_ignored_exit_code=with_ignored_exit_code):
                # ACT && ASSERT #

                integration_check.CHECKER__PARSE_FULL.check__w_source_variants_for_full_line_parser(
                    self,
                    args.syntax_for_run(
                        program_args.symbol_ref_command_elements(program_symbol.name),
                        ignore_exit_code=with_ignored_exit_code,
                    ),
                    model_constructor.of_lines(self, input_model_lines),
                    arrangement_w_tcds(
                        tcds_contents=py_file_rel_opt_conf.populator_for_relativity_option_root(
                            DirContents([py_file])
                        ),
                        symbols=program_symbol.symbol_table,
                    ),
                    MultiSourceExpectation(
                        program_symbol.references_assertion,
                        ExecutionExpectation(
                            main_result=asrt_string_source.pre_post_freeze__matches_lines(
                                asrt.equals(input_model_lines),
                                may_depend_on_external_resources=asrt.equals(True),
                                frozen_may_depend_on_external_resources=asrt.anything_goes(),
                            )
                        ),
                        PRIMITIVE_IS_NOT_IDENTITY_TRANSFORMATION,
                    ),
                )


EXECUTION_OUTPUT_IS_EMPTY = ExecutionExpectation(
    main_result=asrt_string_source.pre_post_freeze__identical(
        asrt_contents.matches__str(asrt.equals(''))
    )
)

PRIMITIVE_IS_NOT_IDENTITY_TRANSFORMATION = prim_asrt__constant(
    asrt_string_transformer.is_identity_transformer(False)
)
