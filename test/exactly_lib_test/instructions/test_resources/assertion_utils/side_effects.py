import pathlib
import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType
from exactly_lib.test_case_file_structure.relative_path_options import REL_OPTIONS_MAP
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


class AssertCwdIsSubDirOf(ValueAssertion):
    def __init__(self, relativity: RelOptionType,
                 expected_sub_dir_of_act_dir: pathlib.PurePath):
        self.relativity = relativity
        self.expected_sub_dir_of_act_dir = expected_sub_dir_of_act_dir

    def apply(self,
              put: unittest.TestCase,
              value: HomeAndSds,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        relativity_root = REL_OPTIONS_MAP[self.relativity].root_resolver.from_home_and_sds(value)
        put.assertEqual(relativity_root / self.expected_sub_dir_of_act_dir,
                        pathlib.Path.cwd(),
                        message_builder.apply('CWD expected to be sub-dir of ' + str(self.relativity)))
