import pathlib
import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.instructions.assert_phase import change_dir as sut
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import TestCaseBase, \
    Arrangement, Expectation
from shellcheck_lib_test.instructions.multi_phase_instructions.change_dir import AssertCwdIsSubDirOfEds
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents
from shellcheck_lib_test.instructions.test_resources.utils import new_source2
from shellcheck_lib_test.util.file_structure import DirContents, empty_dir, Dir, empty_file


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


class TestCasesThatTestIntegrationByAFewRandomTests(TestCaseBaseForParser):
    def test_creation_of_directory_with_multiple_path_components(self):
        self._run(
                new_source2('first-component/second-component'),
                Arrangement(
                        eds_contents_before_main=act_dir_contents(DirContents([
                            Dir('first-component', [
                                empty_dir('second-component')
                            ])]))),
                Expectation(
                        side_effects_check=AssertCwdIsSubDirOfEds(pathlib.Path('first-component') / 'second-component')
                ))

    def test_argument_exists_as_non_directory__single_path_component(self):
        self._run(
                new_source2('file'),
                Arrangement(
                        eds_contents_before_main=act_dir_contents(DirContents([
                            empty_file('file')]))),
                Expectation(
                        main_result=pfh_check.is_hard_error())
        )


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestCasesThatTestIntegrationByAFewRandomTests))
    return ret_val


if __name__ == '__main__':
    unittest.main()
