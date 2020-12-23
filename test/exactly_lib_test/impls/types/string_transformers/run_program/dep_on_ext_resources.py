import unittest

from exactly_lib.impls.os_services import os_services_access
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import Expectation
from exactly_lib_test.impls.types.logic.test_resources.intgr_arr_exp import arrangement_w_tcds, \
    ExecutionExpectation, \
    prim_asrt__constant, ParseExpectation
from exactly_lib_test.impls.types.program.test_resources import arguments_building as program_args
from exactly_lib_test.impls.types.string_source.test_resources import model_constructor
from exactly_lib_test.impls.types.string_transformers.test_resources import argument_syntax as args
from exactly_lib_test.impls.types.string_transformers.test_resources import integration_check
from exactly_lib_test.test_case.test_resources.arrangements import ProcessExecutionArrangement
from exactly_lib_test.test_case.test_resources.command_executors import CommandExecutorThatJustReturnsConstant
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_deps.types.test_resources.program import ProgramSymbolContext
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_transformer.test_resources import \
    string_transformer_assertions as asrt_string_transformer


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestMayDependOnExternalResourcesShouldBeFalseRegardlessOfSourceModel()
    ])


class TestMayDependOnExternalResourcesShouldBeFalseRegardlessOfSourceModel(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        program_symbol = ProgramSymbolContext.of_arbitrary_value('PROGRAM_SYMBOL')
        executor_that_do_not_run_any_program = CommandExecutorThatJustReturnsConstant(0)

        for may_depend_on_external_resources in [False, True]:
            for with_ignored_exit_code in [False, True]:
                with self.subTest(with_ignored_exit_code=with_ignored_exit_code,
                                  may_depend_on_external_resources=may_depend_on_external_resources):
                    # ACT && ASSERT #
                    pass
                integration_check.CHECKER__PARSE_SIMPLE.check(
                    self,
                    args.syntax_for_run(
                        program_args.symbol_ref_command_elements(program_symbol.name),
                        ignore_exit_code=with_ignored_exit_code,
                    ).as_remaining_source,
                    model_constructor.empty(self,
                                            may_depend_on_external_resources=may_depend_on_external_resources),
                    arrangement_w_tcds(
                        symbols=program_symbol.symbol_table,
                        process_execution=ProcessExecutionArrangement(
                            os_services=os_services_access.new_for_cmd_exe(executor_that_do_not_run_any_program)
                        ),
                    ),
                    Expectation(
                        ParseExpectation(
                            symbol_references=program_symbol.references_assertion,
                        ),
                        ExecutionExpectation(
                            main_result=asrt_string_source.matches__lines__pre_post_freeze(
                                asrt.anything_goes(),
                                may_depend_on_external_resources=asrt.equals(True),
                                frozen_may_depend_on_external_resources=asrt.anything_goes(),
                            )
                        ),
                        prim_asrt__constant(
                            asrt_string_transformer.is_identity_transformer(False)
                        ),
                    ),
                )
