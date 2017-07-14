import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib_test.test_case_file_structure.test_resources.sds_check import sds_populator
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir_contents
from exactly_lib_test.test_resources.test_case_file_struct_and_symbols.home_and_sds_utils import \
    HomeAndSdsAction, \
    home_and_sds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion, anything_goes
from exactly_lib_test.util.test_resources.symbol_tables import symbol_table_from_none_or_value


class PostActionCheck:
    def apply(self,
              put: unittest.TestCase,
              home_and_sds: HomeAndSds):
        pass


class Arrangement:
    def __init__(self,
                 pre_contents_population_action: HomeAndSdsAction = HomeAndSdsAction(),
                 home_dir_contents_before: DirContents = empty_dir_contents(),
                 sds_contents_before: sds_populator.SdsPopulator = sds_populator.empty(),
                 pre_action_action: HomeAndSdsAction = HomeAndSdsAction(),
                 symbols: SymbolTable = None):
        self.pre_contents_population_action = pre_contents_population_action
        self.home_dir_contents_before = home_dir_contents_before
        self.sds_contents_before = sds_contents_before
        self.pre_action_action = pre_action_action
        self.symbols = symbol_table_from_none_or_value(symbols)


class Expectation:
    def __init__(self,
                 expected_action_result: ValueAssertion = anything_goes(),
                 expected_sds_contents_after: asrt.ValueAssertion = asrt.anything_goes(),
                 post_action_check: PostActionCheck = PostActionCheck()):
        self.expected_action_result = expected_action_result
        self.expected_sds_contents_after = expected_sds_contents_after
        self.post_action_check = post_action_check


class TestCaseBase(unittest.TestCase):
    def _check(self,
               action: HomeAndSdsAction,
               arrangement: Arrangement,
               expectation: Expectation):
        check(self,
              action,
              arrangement,
              expectation)


def check(put: unittest.TestCase,
          action: HomeAndSdsAction,
          arrangement: Arrangement,
          expectation: Expectation):
    with home_and_sds_with_act_as_curr_dir(pre_contents_population_action=arrangement.pre_contents_population_action,
                                           home_dir_contents=arrangement.home_dir_contents_before,
                                           sds_contents=arrangement.sds_contents_before,
                                           symbols=arrangement.symbols,
                                           ) as environment:
        arrangement.pre_action_action.apply(environment)
        result = action.apply(environment)
        expectation.expected_action_result.apply(put, result)
        expectation.expected_sds_contents_after.apply(put, environment.sds)
        expectation.post_action_check.apply(put, environment.sds)
