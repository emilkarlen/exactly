import pathlib
import unittest

from shellcheck_lib.test_case.phases.common import HomeAndEds
from shellcheck_lib_test.instructions.test_resources.assertion_utils.side_effects import SideEffectsCheck
from shellcheck_lib_test.test_resources import value_assertion as va


class AssertCwdIsSubDirOfActDir(va.ValueAssertion):
    def __init__(self, expected_sub_dir_of_act_dir: pathlib.PurePath):
        self.expected_sub_dir_of_act_dir = expected_sub_dir_of_act_dir

    def apply(self,
              put: unittest.TestCase,
              value: HomeAndEds,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        put.assertEqual(value.eds.act_dir / self.expected_sub_dir_of_act_dir,
                        pathlib.Path.cwd(),
                        message_builder.apply('CWD expected to be sub-dir of EDS/act'))


class SideEffectsCheckAsVa(va.ValueAssertion):
    def __init__(self,
                 other: SideEffectsCheck):
        self.other = other

    def apply(self,
              put: unittest.TestCase,
              value: HomeAndEds,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        self.other.apply(put, value)
