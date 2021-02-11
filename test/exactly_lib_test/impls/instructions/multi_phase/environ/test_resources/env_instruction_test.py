import unittest

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.instructions.multi_phase.environ.test_resources.abstract_syntax import \
    SetVariableArgumentsAbsStx, UnsetVariableArgumentsAbsStx
from exactly_lib_test.impls.instructions.multi_phase.instruction_integration_test_resources.configuration import \
    ConfigurationBase, \
    suite_for_cases
from exactly_lib_test.test_case.test_resources import instr_settings_assertions as asrt_is
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite_for(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf,
                           [
                               TestSet,
                               TestUnsetExistingVariable,
                               TestUnsetNonExistingVariable,
                           ])


class TestCaseBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, conf: ConfigurationBase):
        super().__init__(conf)
        self.conf = conf


class TestSet(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        var_val = NameAndValue('name', 'value')
        instruction_argument = SetVariableArgumentsAbsStx.of_nav(var_val)
        expected_environ = {var_val.name: var_val.value}

        empty_environ = {}

        def mk_arrangement():
            return self.conf.arrangement(environ=dict(empty_environ))

        # ACT & ASSERT #
        self.conf.instruction_checker.check_parsing__abs_stx(
            self,
            self.conf.parser(),
            instruction_argument,
            mk_arrangement,
            self.conf.expect_success(
                instruction_settings=asrt_is.matches(environ=asrt.equals(expected_environ))
            )
        )


class TestUnsetExistingVariable(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        var_name = 'var_to_unset'
        other_var = NameAndValue('other_var', 'val of other var')
        instruction_argument = UnsetVariableArgumentsAbsStx(var_name)
        environ_w_var_to_unset = {var_name: 'value of var to unset',
                                  other_var.name: other_var.value}
        environ_wo_var_to_unset = {other_var.name: other_var.value}

        def mk_arrangement():
            return self.conf.arrangement(environ=dict(environ_w_var_to_unset))

        # ACT & ASSERT #
        self.conf.instruction_checker.check_parsing__abs_stx(
            self,
            self.conf.parser(),
            instruction_argument,
            mk_arrangement,
            self.conf.expect_success(
                instruction_settings=asrt_is.matches(environ=asrt.equals(environ_wo_var_to_unset))
            )
        )


class TestUnsetNonExistingVariable(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        var_name = 'var_to_unset'
        instruction_argument = UnsetVariableArgumentsAbsStx(var_name)
        environ_wo_var_to_unset = {'other_var': 'val of other var'}

        def mk_arrangement():
            return self.conf.arrangement(environ=dict(environ_wo_var_to_unset))

        # ACT & ASSERT #
        self.conf.instruction_checker.check_parsing__abs_stx(
            self,
            self.conf.parser(),
            instruction_argument,
            mk_arrangement,
            self.conf.expect_success(
                instruction_settings=asrt_is.matches(environ=asrt.equals(environ_wo_var_to_unset))
            )
        )
