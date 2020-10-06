import unittest
from typing import List

from exactly_lib.symbol.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.type_system.logic.string_transformer import StringTransformer
from exactly_lib_test.section_document.test_resources import parse_source_assertions as asrt_source
from exactly_lib_test.symbol.data.test_resources.list_ import ListSymbolContext
from exactly_lib_test.symbol.data.test_resources.symbol_reference_assertions import is_reference_to_data_type_symbol
from exactly_lib_test.symbol.test_resources.program import ProgramSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolContext
from exactly_lib_test.test_case_utils.logic.test_resources.intgr_arr_exp import Arrangement, arrangement_w_tcds, \
    ParseExpectation, ExecutionExpectation, PrimAndExeExpectation, prim_asrt__constant
from exactly_lib_test.test_case_utils.program.test_resources import arguments_building as program_args, program_sdvs
from exactly_lib_test.test_case_utils.string_models.test_resources import model_constructor
from exactly_lib_test.test_case_utils.string_transformers.test_resources import argument_syntax as args
from exactly_lib_test.test_case_utils.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case_utils.test_resources import relativity_options as rel_opt
from exactly_lib_test.test_resources.files.file_structure import File, DirContents
from exactly_lib_test.test_resources.test_utils import NExArr
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_system.logic.string_model.test_resources import assertions as asrt_string_model
from exactly_lib_test.type_system.logic.string_transformer.test_resources import \
    string_transformer_assertions as asrt_string_transformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestProgramArgumentsShouldBeGivenToProcess()
    ])


class TestProgramArgumentsShouldBeGivenToProcess(unittest.TestCase):
    def runTest(self):
        # ARRANGE #

        py_file = File('print-arguments-on-stdout.py',
                       _PY_PROGRAM_THAT_PRINTS_ONE_ARGUMENT_PER_LINE_ON_STDOUT,
                       )
        py_file_rel_opt_conf = rel_opt.conf_rel_any(RelOptionType.REL_TMP)

        py_file_conf = py_file_rel_opt_conf.named_file_conf(py_file.name)

        program_symbol = ProgramSymbolContext.of_sdv(
            'PROGRAM_SYMBOL_NAME',
            program_sdvs.interpret_py_source_file_that_must_exist(py_file_conf.path_sdv)
        )

        command_line_arg_list_symbol_name = 'COMMAND_LINE_ARGUMENTS_LIST'

        command_line_arguments_cases = [
            [],
            ['one'],
            ['one', 'two'],
        ]

        def arguments_case(command_line_arguments: List[str],
                           ) -> NExArr[PrimAndExeExpectation[StringTransformer, StringModel],
                                       Arrangement]:
            arg_list_symbol = ListSymbolContext.of_constants(
                command_line_arg_list_symbol_name,
                command_line_arguments
            )

            symbols = [
                program_symbol,
                arg_list_symbol,
            ]

            expected_lines_on_stdout = asrt.matches_sequence([
                asrt.equals(arg + '\n')
                for arg in command_line_arguments
            ])

            return NExArr(
                'Arguments: ' + repr(command_line_arguments),
                PrimAndExeExpectation(
                    ExecutionExpectation(
                        main_result=asrt_string_model.model_lines_sequence_matches(
                            expected_lines_on_stdout
                        )
                    ),
                    prim_asrt__constant(
                        asrt_string_transformer.is_identity_transformer(False)
                    ),
                ),
                arrangement_w_tcds(
                    symbols=SymbolContext.symbol_table_of_contexts(symbols),
                    tcds_contents=py_file_rel_opt_conf.populator_for_relativity_option_root(
                        DirContents([py_file])
                    ),
                ),
            )

        for with_ignored_exit_code in [False, True]:
            with self.subTest(with_ignored_exit_code=with_ignored_exit_code):
                # ACT && ASSERT #

                integration_check.CHECKER__PARSE_FULL.check_multi(
                    self,
                    args.syntax_for_run(
                        program_args.symbol_ref_command_elements(
                            program_symbol.name,
                            arguments=[symbol_reference_syntax_for_name(command_line_arg_list_symbol_name)],
                        ),
                        ignore_exit_code=with_ignored_exit_code,
                    ),
                    ParseExpectation(
                        source=asrt_source.is_at_end_of_line(1),
                        symbol_references=asrt.matches_sequence([
                            program_symbol.reference_assertion,
                            is_reference_to_data_type_symbol(command_line_arg_list_symbol_name),
                        ]),
                    ),
                    model_constructor.arbitrary(self),
                    [
                        arguments_case(command_line_arguments)
                        for command_line_arguments in command_line_arguments_cases
                    ],
                )


_PY_PROGRAM_THAT_PRINTS_ONE_ARGUMENT_PER_LINE_ON_STDOUT = """\
import sys

for arg in sys.argv[1:]:
  print(arg)
"""
