import unittest

from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib.instructions.assert_phase import contents as sut
from shellcheck_lib.test_case.help.instruction_description import Description
from shellcheck_lib_test.instructions.assert_phase.test_resources import instruction_check
from shellcheck_lib_test.instructions.assert_phase.test_resources.contents_resources import \
    ActResultProducerForContentsWithAllReplacedEnvVars, \
    StoreContentsInFileInCurrentDir, WriteFileToHomeDir, WriteFileToCurrentDir, \
    StoreContentsInFileInParentDirOfCwd
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Flow
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources.check_description import TestDescriptionBase
from shellcheck_lib_test.instructions.test_resources.eds_populator import act_dir_contents, tmp_user_dir_contents, \
    multiple
from shellcheck_lib_test.instructions.test_resources.utils import new_source, new_source2
from shellcheck_lib_test.util.file_structure import DirContents, empty_file, empty_dir, File


class TestParse(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source2(''))


class TestFileContentsEmptyInvalidSyntax(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        arguments = 'file-name empty superfluous-argument'
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source2(arguments))


class TestFileContentsEmptyValidSyntax(instruction_check.TestCaseBase):
    def test_fail__when__file_do_not_exist(self):
        self._chekk(
                Flow(sut.Parser(),
                     expected_main_result=pfh_check.is_fail()),
                new_source2('name-of-non-existing-file empty'))

    def test_fail__when__file_is_directory(self):
        file_name = 'name-of-existing-directory'
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(
                             DirContents([empty_dir(file_name)])),
                     expected_main_result=pfh_check.is_fail()),
                new_source2(file_name + ' empty'))

    def test_fail__when__file_exists_but_is_non_empty(self):
        file_name = 'name-of-existing-file'
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(
                             DirContents([File(file_name, 'contents')])),
                     expected_main_result=pfh_check.is_fail()
                     ),
                new_source2(file_name + ' empty'))

    def test_pass__when__file_exists_and_is_empty(self):
        file_name = 'name-of-existing-file'
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(
                             DirContents([empty_file(file_name)])),
                     ),
                new_source2(file_name + ' empty'))


class TestFileContentsNonEmptyInvalidSyntax(instruction_check.TestCaseBase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        arguments = 'file-name ! empty superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self._chekk(
                    Flow(sut.Parser()),
                    new_source2(arguments))


class TestFileContentsNonEmptyValidSyntax(instruction_check.TestCaseBase):
    def test_fail__when__file_do_not_exist(self):
        self._chekk(
                Flow(sut.Parser(),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2('name-of-non-existing-file ! empty'))

    def test_fail__when__file_is_directory(self):
        file_name = 'name-of-existing-directory'
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(DirContents(
                             [empty_dir(file_name)])),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2(file_name + ' ! empty'))

    def test_fail__when__file_exists_but_is_empty(self):
        file_name = 'name-of-existing-file'
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(DirContents(
                             [empty_file(file_name)])),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2(file_name + ' ! empty'))

    def test_pass__when__file_exists_and_is_non_empty(self):
        file_name = 'name-of-existing-file'
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(DirContents(
                             [File(file_name, 'contents')])),
                     ),
                new_source2(file_name + ' ! empty'))


class TestFileContentsFileRelHome(instruction_check.TestCaseBase):
    def test_validation_error__when__comparison_file_does_not_exist(self):
        self._chekk(
                Flow(sut.Parser(),
                     expected_validation_result=svh_check.is_validation_error(),
                     ),
                new_source2('name-of-non-existing-file --rel-home f.txt'))

    def test_validation_error__when__comparison_file_is_a_directory(self):
        self._chekk(
                Flow(sut.Parser(),
                     home_dir_contents=DirContents([empty_dir('dir')]),
                     expected_validation_result=svh_check.is_validation_error(),
                     ),
                new_source2('name-of-non-existing-file --rel-home dir'))

    def test_fail__when__target_file_does_not_exist(self):
        self._chekk(
                Flow(sut.Parser(),
                     home_dir_contents=DirContents([empty_file('f.txt')]),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2('name-of-non-existing-file --rel-home f.txt'))

    def test_fail__when__target_file_is_a_directory(self):
        self._chekk(
                Flow(sut.Parser(),
                     home_dir_contents=DirContents([empty_file('f.txt')]),
                     eds_contents_before_main=act_dir_contents(
                             DirContents([empty_dir('dir')])),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2('dir --rel-home f.txt'))

    def test_fail__when__contents_differ(self):
        self._chekk(
                Flow(sut.Parser(),
                     home_dir_contents=DirContents([empty_file('f.txt')]),
                     eds_contents_before_main=act_dir_contents(
                             DirContents([File('target.txt', 'non-empty')])),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2('target.txt --rel-home f.txt'))

    def test_pass__when__contents_equals(self):
        self._chekk(
                Flow(sut.Parser(),
                     home_dir_contents=DirContents([File('f.txt', 'contents')]),
                     eds_contents_before_main=act_dir_contents(DirContents(
                             [File('target.txt', 'contents')])),
                     ),
                new_source2('target.txt --rel-home f.txt'))


class TestFileContentsFileRelCwd(instruction_check.TestCaseBase):
    def test_fail__when__comparison_file_does_not_exist(self):
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(
                             DirContents([empty_file('target')])),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2('target --rel-cwd comparison'))

    def test_fail__when__target_file_does_not_exist(self):
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(
                             DirContents([empty_file('comparison')])),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2('target --rel-cwd comparison'))

    def test_validation_error__when__comparison_file_is_a_directory(self):
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(
                             DirContents([empty_file('target'),
                                          empty_dir('comparison')])),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2('target --rel-cwd comparison'))

    def test_validation_error__when__target_file_is_a_directory(self):
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(
                             DirContents([empty_dir('target'),
                                          empty_file('comparison')])),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2('target --rel-cwd comparison'))

    def test_fail__when__contents_is_different(self):
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(
                             DirContents([File('target', 'target-contents'),
                                          File('comparison', 'cmp-contents')])),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2('target --rel-cwd comparison'))

    def test_pass__when__contents_is_equal(self):
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=act_dir_contents(
                             DirContents([File('target', 'contents'),
                                          File('comparison', 'contents')])),
                     ),
                new_source2('target --rel-cwd comparison'))


class TestFileContentsFileRelTmp(instruction_check.TestCaseBase):
    def test_fail__when__target_file_does_not_exist(self):
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=tmp_user_dir_contents(
                             DirContents([empty_file('comparison')])),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2('target --rel-tmp comparison'))

    def test_pass__when__contents_is_equal(self):
        self._chekk(
                Flow(sut.Parser(),
                     eds_contents_before_main=multiple([
                         act_dir_contents(
                                 DirContents([File('target', 'contents')])),
                         tmp_user_dir_contents(
                                 DirContents([File('comparison', 'contents')])),
                     ])),
                new_source2('target --rel-tmp comparison'))


class TestTargetFileRelTmp(instruction_check.TestCaseBase):
    def test_fail__when__target_file_does_not_exist(self):
        self._chekk(
                Flow(sut.Parser(),
                     home_dir_contents=DirContents([empty_file('comparison')]),
                     expected_main_result=pfh_check.is_fail(),
                     ),
                new_source2('--rel-tmp target --rel-home comparison'))

    def test_fail__when__contents_is_unequal(self):
        self._chekk(
                Flow(sut.Parser(),
                     home_dir_contents=DirContents([File('comparison', 'comparison-contents')]),
                     eds_contents_before_main=tmp_user_dir_contents(
                             DirContents([File('target', 'target-contents')])),
                     expected_main_result=pfh_check.is_fail()),
                new_source2('--rel-tmp target --rel-home comparison'))

    def test_pass__when__contents_is_equal(self):
        self._chekk(
                Flow(sut.Parser(),
                     home_dir_contents=DirContents([File('comparison', 'contents')]),
                     eds_contents_before_main=tmp_user_dir_contents(
                             DirContents([File('target', 'contents')]))),
                new_source2('--rel-tmp target --rel-home comparison'))


class TestReplacedEnvVars(instruction_check.TestCaseBase):
    COMPARISON_SOURCE_FILE_NAME = 'with-replaced-env-vars.txt'
    COMPARISON_TARGET_FILE_NAME = 'file-with-env-var-values-in-it-from-act-phase.txt'

    def __init__(self,
                 method_name):
        super().__init__(method_name)

    def test_pass__when__contents_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
                StoreContentsInFileInCurrentDir(self.COMPARISON_TARGET_FILE_NAME),
                source_file_writer=WriteFileToHomeDir(self.COMPARISON_SOURCE_FILE_NAME),
                source_should_contain_expected_value=True)
        self._chekk(
                Flow(sut.Parser(),
                     act_result_producer=act_result_producer),
                new_source('instruction-name',
                           '{} --with-replaced-env-vars --rel-home {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                              self.COMPARISON_SOURCE_FILE_NAME))
        )

    def test_fail__when__contents_not_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
                StoreContentsInFileInCurrentDir(self.COMPARISON_TARGET_FILE_NAME),
                source_file_writer=WriteFileToHomeDir(self.COMPARISON_SOURCE_FILE_NAME),
                source_should_contain_expected_value=False)
        self._chekk(
                Flow(sut.Parser(),
                     act_result_producer=act_result_producer,
                     expected_main_result=pfh_check.is_fail()),
                new_source('instruction-name',
                           '{} --with-replaced-env-vars --rel-home {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                              self.COMPARISON_SOURCE_FILE_NAME))
        )

    def test_pass__when__contents_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
                StoreContentsInFileInCurrentDir(self.COMPARISON_TARGET_FILE_NAME),
                source_file_writer=WriteFileToCurrentDir(self.COMPARISON_SOURCE_FILE_NAME),
                source_should_contain_expected_value=True)
        self._chekk(
                Flow(sut.Parser(),
                     act_result_producer=act_result_producer),
                new_source2('{} --with-replaced-env-vars --rel-cwd {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                              self.COMPARISON_SOURCE_FILE_NAME))
        )

    def test_fail__when__contents_not_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
                StoreContentsInFileInCurrentDir(self.COMPARISON_TARGET_FILE_NAME),
                source_file_writer=WriteFileToCurrentDir(self.COMPARISON_SOURCE_FILE_NAME),
                source_should_contain_expected_value=False)
        self._chekk(
                Flow(sut.Parser(),
                     act_result_producer=act_result_producer,
                     expected_main_result=pfh_check.is_fail()),
                new_source2('{} --with-replaced-env-vars --rel-cwd {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                              self.COMPARISON_SOURCE_FILE_NAME))
        )

    def test_pass__when__contents_equals_but_src_does_not_reside_inside_act_dir__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
                StoreContentsInFileInParentDirOfCwd(self.COMPARISON_TARGET_FILE_NAME),
                source_file_writer=WriteFileToHomeDir(self.COMPARISON_SOURCE_FILE_NAME),
                source_should_contain_expected_value=True)
        self._chekk(
                Flow(sut.Parser(),
                     act_result_producer=act_result_producer),
                new_source2('../{} --with-replaced-env-vars --rel-home {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                                  self.COMPARISON_SOURCE_FILE_NAME))
        )


class TestDescription(TestDescriptionBase):
    def _description(self) -> Description:
        return sut.TheDescription('instruction name')


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestFileContentsEmptyInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsEmptyValidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsNonEmptyInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsNonEmptyValidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsFileRelHome))
    ret_val.addTest(unittest.makeSuite(TestFileContentsFileRelCwd))
    ret_val.addTest(unittest.makeSuite(TestFileContentsFileRelTmp))
    ret_val.addTest(unittest.makeSuite(TestTargetFileRelTmp))
    ret_val.addTest(unittest.makeSuite(TestReplacedEnvVars))
    ret_val.addTest(unittest.makeSuite(TestDescription))
    return ret_val


if __name__ == '__main__':
    unittest.main()
