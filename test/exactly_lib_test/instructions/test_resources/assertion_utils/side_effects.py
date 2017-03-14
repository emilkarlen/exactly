import pathlib
import unittest

from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib_test.test_resources.value_assertions import value_assertion as va


class AssertCwdIsSubDirOfActDir(va.ValueAssertion):
    def __init__(self, expected_sub_dir_of_act_dir: pathlib.PurePath):
        self.expected_sub_dir_of_act_dir = expected_sub_dir_of_act_dir

    def apply(self,
              put: unittest.TestCase,
              value: HomeAndSds,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        put.assertEqual(value.sds.act_dir / self.expected_sub_dir_of_act_dir,
                        pathlib.Path.cwd(),
                        message_builder.apply('CWD expected to be sub-dir of SDS/act'))
