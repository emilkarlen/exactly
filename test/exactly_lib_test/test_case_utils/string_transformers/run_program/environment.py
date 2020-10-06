import unittest
from typing import List, Dict

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, ParseExpectation, \
    ExecutionExpectation, PrimAndExeExpectation, prim_asrt__constant
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.string_models.test_resources import model_constructor
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase, MessageBuilder
from exactly_lib_test.type_system.logic.string_model.test_resources import assertions as asrt_string_model
from exactly_lib_test.type_system.logic.string_transformer.test_resources import \
    string_transformer_assertions as asrt_string_transformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestStdinShouldBeContentsOfModel()
    ])


class TestStdinShouldBeContentsOfModel(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        py_file = File('output-env-vars.py',
                       _PGM_THAT_OUTPUTS_ENVIRONMENT_VARS)

        py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
        py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

        program_symbol = ProgramSymbolContext.of_sdv(
            'PROGRAM_THAT_EXECUTES_PY_FILE',
            program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
        )
        environment_cases = [
            {
                '1': 'one',
            },
            {
                '1': 'one',
                '2': 'two',
            },
        ]

        for with_ignored_exit_code in [False, True]:
            with self.subTest(with_ignored_exit_code=with_ignored_exit_code):
                # ACT && ASSERT #

                integration_check.CHECKER__PARSE_FULL.check_multi(
                    self,
                    args.syntax_for_run(
                        program_args.symbol_ref_command_elements(program_symbol.name),
                        ignore_exit_code=with_ignored_exit_code,
                    ),
                    ParseExpectation(
                        source=asrt_source.is_at_end_of_line(1),
                        symbol_references=program_symbol.references_assertion,
                    ),
                    model_constructor.arbitrary(self),
                    [
                        NExArr(
                            'Environment: {}'.format(repr(environment)),
                            PrimAndExeExpectation(
                                ExecutionExpectation(
                                    main_result=asrt_string_model.model_lines_lists_matches(
                                        _AssertLinesRepresentSubSetOfDict(environment)
                                    )
                                ),
                                prim_asrt__constant(
                                    asrt_string_transformer.is_identity_transformer(False)
                                ),
                            ),
                            arrangement_w_tcds(
                                tcds_contents=py_file_rel_opt_conf.populator_for_relativity_option_root(
                                    DirContents([py_file])
                                ),
                                symbols=program_symbol.symbol_table,
                                process_execution=ProcessExecutionArrangement(
                                    process_execution_settings=ProcessExecutionSettings.with_environ(environment)
                                )
                            )

                        )
                        for environment in environment_cases
                    ],
                )


class _AssertLinesRepresentSubSetOfDict(ValueAssertionBase[List[str]]):
    def __init__(self, expected_sub_set: Dict[str, str]):
        self.expected_sub_set = expected_sub_set

    def _apply(self,
               put: unittest.TestCase,
               value: List[str],
               message_builder: MessageBuilder,
               ):
        key_msg = message_builder.apply('key')
        val_msg = message_builder.apply('value')

        actual_as_dict = self._dict_from_lines(value)

        for ek, ev in self.expected_sub_set.items():
            put.assertIn(ek, actual_as_dict,
                         key_msg)
            put.assertEqual(ev, actual_as_dict[ek],
                            val_msg)

    @staticmethod
    def _dict_from_lines(key_val_lines: List[str]) -> Dict[str, str]:
        key_val_list = [
            line.rstrip('\n').split('=', maxsplit=1)
            for line in key_val_lines
        ]
        return dict(key_val_list)


_PGM_THAT_OUTPUTS_ENVIRONMENT_VARS = """\
import os

for k, v in os.environ.items():
  print(k + '=' + v)
"""
