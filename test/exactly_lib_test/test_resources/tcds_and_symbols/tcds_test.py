import unittest

from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.common.test_resources import text_doc_assertions
from exactly_lib_test.tcfs.test_resources import hds_populators, sds_populator
from exactly_lib_test.test_resources.tcds_and_symbols.tcds_utils import \
    TcdsAction, \
    tcds_with_act_as_curr_dir
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, anything_goes


class PostActionCheck:
    def apply(self,
              put: unittest.TestCase,
              tcds: TestCaseDs):
        pass


class Arrangement:
    def __init__(self,
                 pre_contents_population_action: TcdsAction = TcdsAction(),
                 hds_contents_before: hds_populators.HdsPopulator = hds_populators.empty(),
                 sds_contents_before: sds_populator.SdsPopulator = sds_populator.empty(),
                 pre_action_action: TcdsAction = TcdsAction(),
                 symbols: SymbolTable = None):
        self.pre_contents_population_action = pre_contents_population_action
        self.hds_contents_before = hds_contents_before
        self.sds_contents_before = sds_contents_before
        self.pre_action_action = pre_action_action
        self.symbols = symbol_table_from_none_or_value(symbols)


class Expectation:
    def __init__(self,
                 expected_action_result: Assertion = anything_goes(),
                 expected_sds_contents_after: Assertion = asrt.anything_goes(),
                 post_action_check: PostActionCheck = PostActionCheck(),
                 acton_raises_hard_error: bool = False):
        self.expected_action_result = expected_action_result
        self.acton_raises_hard_error = acton_raises_hard_error
        self.expected_sds_contents_after = expected_sds_contents_after
        self.post_action_check = post_action_check


class TestCaseBase(unittest.TestCase):
    def _check(self,
               action: TcdsAction,
               arrangement: Arrangement,
               expectation: Expectation):
        check(self,
              action,
              arrangement,
              expectation)


def check(put: unittest.TestCase,
          action: TcdsAction,
          arrangement: Arrangement,
          expectation: Expectation):
    with tcds_with_act_as_curr_dir(pre_contents_population_action=arrangement.pre_contents_population_action,
                                   hds_contents=arrangement.hds_contents_before,
                                   sds_contents=arrangement.sds_contents_before,
                                   symbols=arrangement.symbols,
                                   ) as environment:
        arrangement.pre_action_action.apply(environment)
        try:
            result = action.apply(environment)
        except HardErrorException as ex:
            if expectation.acton_raises_hard_error:
                text_doc_assertions.assert_is_valid_text_renderer(put, ex.error)
        else:
            if expectation.acton_raises_hard_error:
                put.fail('action does not raise {}'.format(HardErrorException))

            expectation.expected_action_result.apply(put, result)

        expectation.expected_sds_contents_after.apply(put, environment.sds)
        expectation.post_action_check.apply(put, environment.tcds)
