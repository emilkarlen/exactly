from typing import List, Dict, Sequence

from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTrace
from exactly_lib.type_system.logic.matching_result import MatchingResult
from exactly_lib.util.process_execution.execution_elements import ProcessExecutionSettings
from exactly_lib_test.symbol.data.test_resources.list_ import ListSymbolContext
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.symbol.test_resources.string import StringIntConstantSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_w_tcds, \
    PrimAndExeExpectation
from exactly_lib_test.test_case_utils.matcher.test_resources.run_program import py_programs as py_run_programs, \
    assertions as asrt_run
from exactly_lib_test.test_case_utils.program.test_resources import program_sdvs
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.test_utils import NExArr


def argument_list_exe_case(command_line_arguments: List[str],
                           expected_program_arguments: List[str],
                           program_symbol_name: str,
                           list_arg_symbol_name: str,
                           ) -> NExArr[PrimAndExeExpectation[MatcherWTrace, MatchingResult],
                                       Arrangement]:
    py_file = File(
        'arguments-checker.py',
        py_run_programs.pgm_that_exists_with_zero_exit_code_iff_arguments_are_expected(expected_program_arguments)
    )

    py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
    py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

    program_symbol = ProgramSymbolContext.of_sdv(
        program_symbol_name,
        program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
    )

    arg_list_symbol = ListSymbolContext.of_constants(
        list_arg_symbol_name,
        command_line_arguments
    )

    return NExArr(
        'Command line arguments: {}'.format(
            repr(command_line_arguments),
        ),
        PrimAndExeExpectation.of_exe(
            main_result=asrt_run.is_result_for_py_interpreter(py_run_programs.EXIT_CODE_FOR_SUCCESS)
        ),
        arrangement_w_tcds(
            tcds_contents=py_file_rel_opt_conf.populator_for_relativity_option_root(
                DirContents([py_file])
            ),
            symbols=SymbolContext.symbol_table_of_contexts([
                program_symbol,
                arg_list_symbol,
            ]),
        )
    )


def environment_exe_case(environment: Dict[str, str],
                         program_symbol_name: str,
                         ) -> NExArr[PrimAndExeExpectation[MatcherWTrace, MatchingResult],
                                     Arrangement]:
    py_file = File(
        'environment-vars-checker.py',
        py_programs.pgm_that_exists_with_zero_exit_code_iff_environment_vars_not_included(environment)
    )

    py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
    py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

    program_symbol = ProgramSymbolContext.of_sdv(
        program_symbol_name,
        program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
    )

    return NExArr(
        'Environment: {}'.format(repr(environment)),
        PrimAndExeExpectation.of_exe(
            main_result=asrt_run.is_result_for_py_interpreter(
                py_run_programs.EXIT_CODE_FOR_SUCCESS)
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


def exit_code_exe_cases(program_symbol_name: str,
                        exit_code_symbol_name: str,
                        ) -> Sequence[NExArr[PrimAndExeExpectation[MatcherWTrace, MatchingResult],
                                             Arrangement]]:
    py_file = File('exit-with-value-on-command-line.py',
                   py_programs.py_pgm_that_exits_with_1st_value_on_command_line(''))

    py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)
    py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

    program_symbol = ProgramSymbolContext.of_sdv(
        program_symbol_name,
        program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
    )

    def case(exit_code_from_program: int) -> NExArr[PrimAndExeExpectation[MatcherWTrace, MatchingResult],
                                                    Arrangement]:
        exit_code_symbol = StringIntConstantSymbolContext(exit_code_symbol_name,
                                                          exit_code_from_program)

        return NExArr(
            'Exit code {}'.format(exit_code_from_program),
            PrimAndExeExpectation.of_exe(
                main_result=asrt_run.is_result_for_py_interpreter(exit_code_from_program)
            ),
            arrangement_w_tcds(
                tcds_contents=py_file_rel_opt_conf.populator_for_relativity_option_root(
                    DirContents([py_file])
                ),
                symbols=SymbolContext.symbol_table_of_contexts([
                    program_symbol,
                    exit_code_symbol,
                ]),
            )
        )

    exit_code_from_program_cases = [0, 1, 3, 69, 72]

    return [
        case(exit_code_from_program)
        for exit_code_from_program in exit_code_from_program_cases
    ]
