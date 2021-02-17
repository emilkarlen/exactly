import unittest
from abc import ABC
from typing import Dict

from exactly_lib.impls.instructions.multi_phase.environ.impl import Phase
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


def suite_for_non_setup_phase(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf, _NON_SETUP_PHASE)


def suite_for_setup_phase(conf: ConfigurationBase) -> unittest.TestSuite:
    return suite_for_cases(conf, _COMMON)


class TestCaseBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType, ABC):
    def __init__(self, conf: ConfigurationBase):
        super().__init__(conf)
        self.conf = conf


class TestSet(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        var_val = NameAndValue('name', 'value')
        instruction_argument = SetVariableArgumentsAbsStx.of_nav(var_val, phase_spec=None)
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


class TestSetOfActForNonSetupPhase(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        var_val = NameAndValue('name', 'value')
        instruction_argument = SetVariableArgumentsAbsStx.of_nav(var_val, phase_spec=Phase.ACT)
        expected_environ = {}

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


class TestSetWhenCurrentEnvironIsNone(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        var_in_default = NameAndValue('var_in_default', 'value of var in default')
        var_to_set = NameAndValue('var_to_set', 'value')
        expected_environ = NameAndValue.as_dict([var_in_default, var_to_set])

        def get_default_environ() -> Dict[str, str]:
            return NameAndValue.as_dict([var_in_default])

        instruction_argument = SetVariableArgumentsAbsStx.of_nav(var_to_set, phase_spec=None)

        def mk_arrangement():
            return self.conf.arrangement(
                environ=None,
                default_environ_getter=get_default_environ,
            )

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
        instruction_argument = UnsetVariableArgumentsAbsStx.of_str(var_name, phase_spec=None)
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


class TestUnsetVarOfActForNonSetupPhase(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        var_name = 'var_to_unset'
        other_var = NameAndValue('other_var', 'val of other var')
        instruction_argument = UnsetVariableArgumentsAbsStx.of_str(var_name, phase_spec=Phase.ACT)
        environ_w_var_to_unset = {var_name: 'value of var to unset',
                                  other_var.name: other_var.value}

        def mk_arrangement():
            return self.conf.arrangement(environ=dict(environ_w_var_to_unset))

        # ACT & ASSERT #
        self.conf.instruction_checker.check_parsing__abs_stx(
            self,
            self.conf.parser(),
            instruction_argument,
            mk_arrangement,
            self.conf.expect_success(
                instruction_settings=asrt_is.matches(environ=asrt.equals(environ_w_var_to_unset))
            )
        )


class TestUnsetExistingVariableWhenEnvironIsNone(TestCaseBase):
    def runTest(self):
        # ARRANGE #
        var_to_unset = NameAndValue('var_to_unset', 'value of var to unset')

        other_var = NameAndValue('other_var', 'val of other var')
        instruction_argument = UnsetVariableArgumentsAbsStx.of_str(var_to_unset.name,
                                                                   phase_spec=None)
        vars_from_defaults_getter = [var_to_unset, other_var]

        environ_wo_var_to_unset = NameAndValue.as_dict([other_var])

        def get_default_environ() -> Dict[str, str]:
            return NameAndValue.as_dict(vars_from_defaults_getter)

        def mk_arrangement():
            return self.conf.arrangement(
                environ=None,
                default_environ_getter=get_default_environ,
            )

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
        instruction_argument = UnsetVariableArgumentsAbsStx.of_str(var_name, phase_spec=None)
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


_COMMON = [
    TestSet,
    TestUnsetExistingVariable,
    TestUnsetNonExistingVariable,
    TestSetWhenCurrentEnvironIsNone,
    TestUnsetExistingVariableWhenEnvironIsNone,
]

_NON_SETUP_PHASE = _COMMON + [
    TestSetOfActForNonSetupPhase,
    TestUnsetVarOfActForNonSetupPhase,
]
