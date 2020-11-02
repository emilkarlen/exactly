import pathlib
import unittest

from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.tcfs.relative_path_options import REL_OPTIONS_MAP
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase


class AssertCwdIsSubDirOf(ValueAssertionBase):
    def __init__(self, relativity: RelOptionType,
                 expected_sub_dir_of_act_dir: pathlib.PurePath):
        self.relativity = relativity
        self.expected_sub_dir_of_act_dir = expected_sub_dir_of_act_dir

    def _apply(self,
               put: unittest.TestCase,
               value: TestCaseDs,
               message_builder: asrt.MessageBuilder):
        relativity_root = REL_OPTIONS_MAP[self.relativity].root_resolver.from_tcds(value)
        put.assertEqual(relativity_root / self.expected_sub_dir_of_act_dir,
                        pathlib.Path.cwd(),
                        message_builder.apply('CWD expected to be sub-dir of ' + str(self.relativity)))
