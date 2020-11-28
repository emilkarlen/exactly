import unittest

from exactly_lib.impls.types.string_transformer.sdvs import StringTransformerSdvConstant
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, \
    ExecutionExpectation, \
    MultiSourceExpectation, prim_asrt__constant
from exactly_lib_test.impls.types.program.test_resources import arguments_building as program_args
from exactly_lib_test.impls.types.program.test_resources import program_sdvs
from exactly_lib_test.impls.types.string_model.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_syntax as args
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check
from exactly_lib_test.impls.types.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.string_model.test_resources import assertions as asrt_string_model
from exactly_lib_test.type_val_prims.string_transformer.test_resources import string_transformers, \
    string_transformer_assertions as asrt_string_transformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestOutputModelShouldBeStdoutFromProgram(),
        TestWhenProgramHasTransformerThenResultShouldBeCompositionOfProgramAndTransformer(),
    ])


class TestOutputModelShouldBeStdoutFromProgram(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        py_file = File('stdin-to-upper.py',
                       _PGM_THAT_OUTPUTS_STDIN_IN_UPPER_CASE)

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
        expected_output_model_lines = list(map(str.upper, input_model_lines))

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
                        symbol_references=program_symbol.references_assertion,
                        execution=ExecutionExpectation(
                            main_result=asrt_string_model.matches__lines(
                                asrt.equals(expected_output_model_lines),
                                may_depend_on_external_resources=asrt.equals(True),
                            )
                        ),
                        primitive=prim_asrt__constant(
                            asrt_string_transformer.is_identity_transformer(False)
                        ),
                    ),
                )


class TestWhenProgramHasTransformerThenResultShouldBeCompositionOfProgramAndTransformer(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        py_file = File('stdin-to-upper.py',
                       _PGM_THAT_OUTPUTS_STDIN_IN_UPPER_CASE)

        py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
        py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

        to_upper_program = program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)

        program_symbol = ProgramSymbolContext.of_sdv(
            'PROGRAM_WITH_OUTPUT_TRANSFORMATION',
            to_upper_program.new_with_appended_transformations(
                [StringTransformerSdvConstant(string_transformers.duplicate_words())]
            )
        )

        input_model_lines = [
            'the\n',
            'input\n',
            'model',
        ]
        expected_output_model_lines = [
            'THE THE\n',
            'INPUT INPUT\n',
            'MODEL MODEL',
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
                            main_result=asrt_string_model.matches__lines(
                                asrt.equals(expected_output_model_lines),
                                may_depend_on_external_resources=asrt.equals(True),
                            )
                        ),
                        prim_asrt__constant(
                            asrt_string_transformer.is_identity_transformer(False)
                        ),
                    ),
                )


_PGM_THAT_OUTPUTS_STDIN_IN_UPPER_CASE = """\
import sys

for l in sys.stdin.readlines():
  sys.stdout.write(l.upper())
"""
