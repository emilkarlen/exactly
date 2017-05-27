import types
import unittest

from exactly_lib.symbol.value_resolvers.path_resolving_environment import PathResolvingEnvironmentPreSds
from exactly_lib.test_case.phases.common import InstructionEnvironmentForPostSdsStep
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.symbol.test_resources.value_structure_assertions import equals_symbol_table


def get_symbol_table_from_instruction_environment_that_is_first_arg(environment: InstructionEnvironmentForPostSdsStep,
                                                                    *args, **kwargs):
    return environment.symbols


def get_symbol_table_from_path_resolving_environment_that_is_first_arg(environment: PathResolvingEnvironmentPreSds,
                                                                       *args, **kwargs):
    return environment.symbols


def do_fail_if_symbol_table_does_not_equal(put: unittest.TestCase,
                                           expected: SymbolTable,
                                           get_actual_symbol_table) -> types.FunctionType:
    def ret_val(*args, **kwargs):
        actual_symbol_table = get_actual_symbol_table(*args, **kwargs)
        assertion = equals_symbol_table(expected)
        assertion.apply_with_message(put, actual_symbol_table, 'symbol table')

    return ret_val
