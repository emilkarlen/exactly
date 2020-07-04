import unittest
from typing import Dict

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.logic.file_matcher import FileMatcherModel
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext, is_reference_to_program
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case_utils.file_matcher.run_program.test_resources import is_result_for_py_interpreter
from exactly_lib_test.test_case_utils.file_matcher.test_resources import argument_building as args
from exactly_lib_test.test_case_utils.file_matcher.test_resources import integration_check
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import PrimAndExeExpectation, Arrangement
from exactly_lib_test.test_case_utils.logic.test_resources.integration_check import arrangement_w_tcds, \
    ParseExpectation
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEnvironmentVarsShouldBePassedToProcess()
    ])


class TestEnvironmentVarsShouldBePassedToProcess(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        program_symbol_name = 'PROGRAM_THAT_EXECUTES_PY_FILE'

        environment_cases = [
            {
                '1': 'one',
            },
            {
                '1': 'one',
                '2': 'two',
            },
        ]

        # ACT && ASSERT #

        integration_check.CHECKER.check_multi(
            self,
            args.RunProgram(
                program_args.symbol_ref_command_elements(
                    program_symbol_name,
                    arguments=[],
                )
            ).as_arguments,
            ParseExpectation(
                source=asrt_source.source_is_at_end,
                symbol_references=asrt.matches_singleton_sequence(
                    is_reference_to_program(program_symbol_name)
                ),
            ),
            integration_check.ARBITRARY_MODEL,
            [
                environment_case_setup(environment_case,
                                       program_symbol_name)
                for environment_case in environment_cases
            ],
        )


def environment_case_setup(environment: Dict[str, str],
                           program_symbol_name: str,
                           ) -> NExArr[PrimAndExeExpectation[MatcherWTrace[FileMatcherModel], MatchingResult],
                                       Arrangement]:
    py_file = File('environment-vars-checker.py',
                   py_pgm_that_exists_with_zero_exit_code_iff_environment_vars_not_included(environment))

    py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
    py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

    program_symbol = ProgramSymbolContext.of_sdv(
        program_symbol_name,
        program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
    )

    return NExArr(
        'Environment: {}'.format(repr(environment)),
        PrimAndExeExpectation.of_exe(
            main_result=is_result_for_py_interpreter(EXIT_CODE_FOR_ASSERTION_BY_PY_PROGRAM_SUCCESSFUL)
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


def py_pgm_that_exists_with_zero_exit_code_iff_environment_vars_not_included(expected: Dict[str, str]) -> str:
    return _PY_PGM_THAT_EXISTS_WITH_ZERO_EXIT_CODE_IFF_ENVIRONMENT_VARS_IS_NOT_INCLUDED.format(
        expected_environment=repr(expected)
    )


EXIT_CODE_FOR_ASSERTION_BY_PY_PROGRAM_SUCCESSFUL = 0

# NOTE: Some env vars (probably for executing python), are included automatically.
# Because of this, we cannot check for equality, but must instead check that
# all given env vars are included in the actual env.
_PY_PGM_THAT_EXISTS_WITH_ZERO_EXIT_CODE_IFF_ENVIRONMENT_VARS_IS_NOT_INCLUDED = """\
import os;
import sys;

expected_env_vars = {expected_environment}

actual_env_vars = dict(os.environ)

for (key, value) in expected_env_vars.items():

  if not key in actual_env_vars:
     sys.stderr.write('Missing key: ' + key)
     sys.exit(1)

  actual_value = actual_env_vars[key]
  if value != actual_value:
     sys.stderr.write('Different value: %s != %s' % (key, actual_value))
     sys.exit(1)

sys.exit(0)
"""
