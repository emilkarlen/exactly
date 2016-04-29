import unittest

from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParserSource
from exactly_lib.instructions.assert_phase import contents as sut
from exactly_lib.instructions.utils import relative_path_options as options
from exactly_lib_test.instructions.assert_phase.test_resources import instruction_check
from exactly_lib_test.instructions.assert_phase.test_resources.contents_resources import \
    ActResultProducerForContentsWithAllReplacedEnvVars, \
    StoreContentsInFileInCurrentDir, WriteFileToHomeDir, WriteFileToCurrentDir, \
    StoreContentsInFileInParentDirOfCwd
from exactly_lib_test.instructions.assert_phase.test_resources.instruction_check import arrangement, \
    Expectation, is_pass
from exactly_lib_test.instructions.test_resources import pfh_check
from exactly_lib_test.instructions.test_resources import svh_check
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.execution.eds_populator import act_dir_contents, tmp_user_dir_contents, \
    multiple
from exactly_lib_test.test_resources.file_structure import DirContents, empty_file, empty_dir, File
from exactly_lib_test.test_resources.parse import new_source, new_source2


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


class TestCaseBaseForParser(instruction_check.TestCaseBase):
    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: ArrangementPostAct,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


class TestFileContentsEmptyValidSyntax(TestCaseBaseForParser):
    def test_fail__when__file_do_not_exist(self):
        self._run(
                new_source2('name-of-non-existing-file empty'),
                arrangement(),
                Expectation(main_result=pfh_check.is_fail())
        )

    def test_fail__when__file_is_directory(self):
        file_name = 'name-of-existing-directory'
        self._run(
                new_source2(file_name + ' empty'),
                arrangement(eds_contents_before_main=act_dir_contents(
                        DirContents([empty_dir(file_name)]))),
                Expectation(main_result=pfh_check.is_fail())
        )

    def test_fail__when__file_exists_but_is_non_empty(self):
        file_name = 'name-of-existing-file'
        self._run(
                new_source2(file_name + ' empty'),
                arrangement(eds_contents_before_main=act_dir_contents(
                        DirContents([File(file_name, 'contents')]))),
                Expectation(main_result=pfh_check.is_fail())
        )

    def test_pass__when__file_exists_and_is_empty(self):
        file_name = 'name-of-existing-file'
        self._run(
                new_source2(file_name + ' empty'),
                arrangement(eds_contents_before_main=act_dir_contents(
                        DirContents([empty_file(file_name)]))),
                is_pass()
        )


class TestFileContentsNonEmptyInvalidSyntax(TestCaseBaseForParser):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        arguments = 'file-name ! empty superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self._run(
                    new_source2(arguments),
                    arrangement(),
                    is_pass(),
            )


class TestFileContentsNonEmptyValidSyntax(TestCaseBaseForParser):
    def test_fail__when__file_do_not_exist(self):
        self._run(
                new_source2('name-of-non-existing-file ! empty'),
                arrangement(),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail__when__file_is_directory(self):
        file_name = 'name-of-existing-directory'
        self._run(
                new_source2(file_name + ' ! empty'),
                arrangement(eds_contents_before_main=act_dir_contents(DirContents(
                        [empty_dir(file_name)]))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail__when__file_exists_but_is_empty(self):
        file_name = 'name-of-existing-file'
        self._run(
                new_source2(file_name + ' ! empty'),
                arrangement(eds_contents_before_main=act_dir_contents(DirContents(
                        [empty_file(file_name)]))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__file_exists_and_is_non_empty(self):
        file_name = 'name-of-existing-file'
        self._run(
                new_source2(file_name + ' ! empty'),
                arrangement(eds_contents_before_main=act_dir_contents(DirContents(
                        [File(file_name, 'contents')]))),
                is_pass(),
        )


class TestFileContentsFileRelHome(TestCaseBaseForParser):
    def test_validation_error__when__comparison_file_does_not_exist(self):
        self._run(
                new_source2('name-of-non-existing-file %s f.txt' % options.REL_HOME_OPTION),
                arrangement(),
                Expectation(validation_pre_eds=svh_check.is_validation_error()),
        )

    def test_validation_error__when__comparison_file_is_a_directory(self):
        self._run(
                new_source2('name-of-non-existing-file --rel-home dir'),
                arrangement(home_dir_contents=DirContents([empty_dir('dir')])),
                Expectation(validation_pre_eds=svh_check.is_validation_error()),
        )

    def test_fail__when__target_file_does_not_exist(self):
        self._run(
                new_source2('name-of-non-existing-file --rel-home f.txt'),
                arrangement(home_dir_contents=DirContents([empty_file('f.txt')])),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail__when__target_file_is_a_directory(self):
        self._run(
                new_source2('dir --rel-home f.txt'),
                arrangement(home_dir_contents=DirContents([empty_file('f.txt')]),
                            eds_contents_before_main=act_dir_contents(
                                    DirContents([empty_dir('dir')]))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail__when__contents_differ(self):
        self._run(
                new_source2('target.txt --rel-home f.txt'),
                arrangement(home_dir_contents=DirContents([empty_file('f.txt')]),
                            eds_contents_before_main=act_dir_contents(
                                    DirContents([File('target.txt', 'non-empty')]))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__contents_equals(self):
        self._run(
                new_source2('target.txt --rel-home f.txt'),
                arrangement(home_dir_contents=DirContents([File('f.txt', 'contents')]),
                            eds_contents_before_main=act_dir_contents(DirContents(
                                    [File('target.txt', 'contents')]))),
                is_pass(),
        )


class TestFileContentsFileRelCwd(TestCaseBaseForParser):
    def test_fail__when__comparison_file_does_not_exist(self):
        self._run(
                new_source2('target --rel-cwd comparison'),
                arrangement(eds_contents_before_main=act_dir_contents(
                        DirContents([empty_file('target')]))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail__when__target_file_does_not_exist(self):
        self._run(
                new_source2('target --rel-cwd comparison'),
                arrangement(eds_contents_before_main=act_dir_contents(
                        DirContents([empty_file('comparison')]))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_validation_error__when__comparison_file_is_a_directory(self):
        self._run(
                new_source2('target --rel-cwd comparison'),
                arrangement(eds_contents_before_main=act_dir_contents(
                        DirContents([empty_file('target'),
                                     empty_dir('comparison')]))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_validation_error__when__target_file_is_a_directory(self):
        self._run(
                new_source2('target --rel-cwd comparison'),
                arrangement(eds_contents_before_main=act_dir_contents(
                        DirContents([empty_dir('target'),
                                     empty_file('comparison')]))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail__when__contents_is_different(self):
        self._run(
                new_source2('target --rel-cwd comparison'),
                arrangement(eds_contents_before_main=act_dir_contents(
                        DirContents([File('target', 'target-contents'),
                                     File('comparison', 'cmp-contents')]))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__contents_is_equal(self):
        self._run(
                new_source2('target --rel-cwd comparison'),
                arrangement(eds_contents_before_main=act_dir_contents(
                        DirContents([File('target', 'contents'),
                                     File('comparison', 'contents')]))),
                is_pass(),
        )


class TestFileContentsFileRelTmp(TestCaseBaseForParser):
    def test_fail__when__target_file_does_not_exist(self):
        self._run(
                new_source2('target --rel-tmp comparison'),
                arrangement(eds_contents_before_main=tmp_user_dir_contents(
                        DirContents([empty_file('comparison')]))),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__contents_is_equal(self):
        self._run(
                new_source2('target --rel-tmp comparison'),
                arrangement(eds_contents_before_main=multiple([
                    act_dir_contents(
                            DirContents([File('target', 'contents')])),
                    tmp_user_dir_contents(
                            DirContents([File('comparison', 'contents')])),
                ])),
                is_pass(),
        )


class TestTargetFileRelTmp(TestCaseBaseForParser):
    def test_fail__when__target_file_does_not_exist(self):
        self._run(
                new_source2('--rel-tmp target --rel-home comparison'),
                arrangement(home_dir_contents=DirContents([empty_file('comparison')])),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_fail__when__contents_is_unequal(self):
        self._run(
                new_source2('--rel-tmp target --rel-home comparison'),
                arrangement(home_dir_contents=DirContents([File('comparison', 'comparison-contents')]),
                            eds_contents_before_main=tmp_user_dir_contents(
                                    DirContents([File('target', 'target-contents')]))),
                Expectation(main_result=pfh_check.is_fail())
        )

    def test_pass__when__contents_is_equal(self):
        self._run(
                new_source2('--rel-tmp target --rel-home comparison'),
                arrangement(home_dir_contents=DirContents([File('comparison', 'contents')]),
                            eds_contents_before_main=tmp_user_dir_contents(
                                    DirContents([File('target', 'contents')]))),
                is_pass(),
        )


class TestReplacedEnvVars(TestCaseBaseForParser):
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
        self._run(
                new_source('instruction-name',
                           '{} --with-replaced-env-vars --rel-home {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                              self.COMPARISON_SOURCE_FILE_NAME)),
                arrangement(act_result_producer=act_result_producer),
                is_pass(),
        )

    def test_fail__when__contents_not_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
                StoreContentsInFileInCurrentDir(self.COMPARISON_TARGET_FILE_NAME),
                source_file_writer=WriteFileToHomeDir(self.COMPARISON_SOURCE_FILE_NAME),
                source_should_contain_expected_value=False)
        self._run(
                new_source2('{} --with-replaced-env-vars --rel-home {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                               self.COMPARISON_SOURCE_FILE_NAME)),
                arrangement(act_result_producer=act_result_producer),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__contents_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
                StoreContentsInFileInCurrentDir(self.COMPARISON_TARGET_FILE_NAME),
                source_file_writer=WriteFileToCurrentDir(self.COMPARISON_SOURCE_FILE_NAME),
                source_should_contain_expected_value=True)
        self._run(
                new_source2('{} --with-replaced-env-vars --rel-cwd {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                              self.COMPARISON_SOURCE_FILE_NAME)),
                arrangement(act_result_producer=act_result_producer),
                is_pass(),
        )

    def test_fail__when__contents_not_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
                StoreContentsInFileInCurrentDir(self.COMPARISON_TARGET_FILE_NAME),
                source_file_writer=WriteFileToCurrentDir(self.COMPARISON_SOURCE_FILE_NAME),
                source_should_contain_expected_value=False)
        self._run(
                new_source2('{} --with-replaced-env-vars --rel-cwd {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                              self.COMPARISON_SOURCE_FILE_NAME)),
                arrangement(act_result_producer=act_result_producer),
                Expectation(main_result=pfh_check.is_fail()),
        )

    def test_pass__when__contents_equals_but_src_does_not_reside_inside_act_dir__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
                StoreContentsInFileInParentDirOfCwd(self.COMPARISON_TARGET_FILE_NAME),
                source_file_writer=WriteFileToHomeDir(self.COMPARISON_SOURCE_FILE_NAME),
                source_should_contain_expected_value=True)
        self._run(
                new_source2('../{} --with-replaced-env-vars --rel-home {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                                  self.COMPARISON_SOURCE_FILE_NAME)),
                arrangement(act_result_producer=act_result_producer),
                is_pass(),
        )


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestParse),
        unittest.makeSuite(TestFileContentsEmptyInvalidSyntax),
        unittest.makeSuite(TestFileContentsEmptyValidSyntax),
        unittest.makeSuite(TestFileContentsNonEmptyInvalidSyntax),
        unittest.makeSuite(TestFileContentsNonEmptyValidSyntax),
        unittest.makeSuite(TestFileContentsFileRelHome),
        unittest.makeSuite(TestFileContentsFileRelCwd),
        unittest.makeSuite(TestFileContentsFileRelTmp),
        unittest.makeSuite(TestTargetFileRelTmp),
        unittest.makeSuite(TestReplacedEnvVars),
        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
