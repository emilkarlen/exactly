from pathlib import Path
import unittest

from shellcheck_lib.execution import environment_variables
from shellcheck_lib.general import file_utils
from shellcheck_lib.instructions.assert_phase import contents as sut
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from shellcheck_lib_test.instructions.assert_phase.test_resources.contents_resources import \
    ActResultProducerForContentsWithAllEnvVarsBase
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Flow, ActEnvironment
from shellcheck_lib_test.instructions.assert_phase.test_resources import instruction_check
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources.eds_populator import FilesInActDir
from shellcheck_lib_test.instructions.utils import new_source, ActResult
from shellcheck_lib_test.util.file_structure import DirContents, empty_file, empty_dir, File


class TestParse(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name',
                                     ''))


class TestFileContentsEmptyInvalidSyntax(unittest.TestCase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        arguments = 'file-name empty superfluous-argument'
        parser = sut.Parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name',
                                     arguments))


class TestFileContentsEmptyValidSyntax(instruction_check.TestCaseBase):
    def test_fail__when__file_do_not_exist(self):
        self._check(
            Flow(sut.Parser(),
                 expected_main_result=pfh_check.is_fail()),
            new_source('instruction-name', 'name-of-non-existing-file empty'))

    def test_fail__when__file_is_directory(self):
        file_name = 'name-of-existing-directory'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_dir(file_name)])),
                 expected_main_result=pfh_check.is_fail()),
            new_source('instruction-name',
                       file_name + ' empty'))

    def test_fail__when__file_exists_but_is_non_empty(self):
        file_name = 'name-of-existing-file'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([File(file_name, 'contents')])),
                 expected_main_result=pfh_check.is_fail()
                 ),
            new_source('instruction-name',
                       file_name + ' empty'))

    def test_pass__when__file_exists_and_is_empty(self):
        file_name = 'name-of-existing-file'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_file(file_name)])),
                 ),
            new_source('instruction-name',
                       file_name + ' empty'))


class TestFileContentsNonEmptyInvalidSyntax(instruction_check.TestCaseBase):
    def test_that_when_no_arguments_then_exception_is_raised(self):
        arguments = 'file-name ! empty superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self._check(
                Flow(sut.Parser()),
                new_source('instruction-name',
                           arguments))


class TestFileContentsNonEmptyValidSyntax(instruction_check.TestCaseBase):
    def test_fail__when__file_do_not_exist(self):
        self._check(
            Flow(sut.Parser(),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       'name-of-non-existing-file ! empty'))

    def test_fail__when__file_is_directory(self):
        file_name = 'name-of-existing-directory'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_dir(file_name)])),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       file_name + ' ! empty'))

    def test_fail__when__file_exists_but_is_empty(self):
        file_name = 'name-of-existing-file'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_file(file_name)])),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       file_name + ' ! empty'))

    def test_pass__when__file_exists_and_is_non_empty(self):
        file_name = 'name-of-existing-file'
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([File(file_name, 'contents')])),
                 ),
            new_source('instruction-name',
                       file_name + ' ! empty'))


class TestFileContentsFileRelHome(instruction_check.TestCaseBase):
    def test_validation_error__when__comparison_file_does_not_exist(self):
        self._check(
            Flow(sut.Parser(),
                 expected_validation_result=svh_check.is_validation_error(),
                 ),
            new_source('instruction-name',
                       'name-of-non-existing-file --rel-home f.txt'))

    def test_validation_error__when__comparison_file_is_a_directory(self):
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents([empty_dir('dir')]),
                 expected_validation_result=svh_check.is_validation_error(),
                 ),
            new_source('instruction-name',
                       'name-of-non-existing-file --rel-home dir'))

    def test_fail__when__target_file_does_not_exist(self):
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents([empty_file('f.txt')]),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       'name-of-non-existing-file --rel-home f.txt'))

    def test_fail__when__target_file_is_a_directory(self):
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents([empty_file('f.txt')]),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_dir('dir')])),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       'dir --rel-home f.txt'))

    def test_fail__when__contents_differ(self):
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents([empty_file('f.txt')]),
                 eds_contents_before_main=FilesInActDir(DirContents([File('target.txt', 'non-empty')])),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       'target.txt --rel-home f.txt'))

    def test_pass__when__contents_equals(self):
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents([File('f.txt', 'contents')]),
                 eds_contents_before_main=FilesInActDir(DirContents([File('target.txt', 'contents')])),
                 ),
            new_source('instruction-name',
                       'target.txt --rel-home f.txt'))


class TestFileContentsFileRelCwd(instruction_check.TestCaseBase):
    def test_fail__when__comparison_file_does_not_exist(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_file('target')])),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       'target --rel-cwd comparison'))

    def test_fail__when__target_file_does_not_exist(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_file('comparison')])),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       'target --rel-cwd comparison'))

    def test_validation_error__when__comparison_file_is_a_directory(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_file('target'),
                                                                     empty_dir('comparison')])),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       'target --rel-cwd comparison'))

    def test_validation_error__when__target_file_is_a_directory(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_dir('target'),
                                                                     empty_file('comparison')])),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       'target --rel-cwd comparison'))

    def test_fail__when__contents_is_different(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([File('target', 'target-contents'),
                                                                     File('comparison', 'cmp-contents')])),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       'target --rel-cwd comparison'))

    def test_pass__when__contents_is_equal(self):
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([File('target', 'contents'),
                                                                     File('comparison', 'contents')])),
                 ),
            new_source('instruction-name',
                       'target --rel-cwd comparison'))


class ActResultProducerForContentsWithAllEnvVars(ActResultProducerForContentsWithAllEnvVarsBase):
    def __init__(self, output_file_path: Path):
        super().__init__()
        self.output_file_path = output_file_path

    def apply(self, act_environment: ActEnvironment) -> ActResult:
        home_and_eds = act_environment.home_and_eds
        env_vars_dict = environment_variables.all_environment_variables(home_and_eds.home_dir_path,
                                                                        home_and_eds.eds)
        values_in_determined_order = list(map(env_vars_dict.get, self.sorted_env_var_keys))
        contents = self._content_from_values(values_in_determined_order)
        file_utils.write_new_text_file(self.output_file_path,
                                       contents)
        return ActResult()


class TestReplacedEnvVars(instruction_check.TestCaseBase):
    COMPARISON_SOURCE_FILE_NAME = 'with-replaced-env-vars.txt'
    COMPARISON_TARGET_FILE_NAME = 'file-with-env-var-values-in-it-from-act-phase.txt'

    def __init__(self,
                 method_name):
        super().__init__(method_name)

    def test_pass__when__contents_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllEnvVars(Path(self.COMPARISON_TARGET_FILE_NAME))
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents([
                     File(self.COMPARISON_SOURCE_FILE_NAME,
                          act_result_producer.expected_contents_after_replacement)]),
                 act_result_producer=act_result_producer),
            new_source('instruction-name',
                       '{} --with-replaced-env-vars --rel-home {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                          self.COMPARISON_SOURCE_FILE_NAME))
        )

    def test_fail__when__contents_not_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllEnvVars(Path(self.COMPARISON_TARGET_FILE_NAME))
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents(
                     [File(self.COMPARISON_SOURCE_FILE_NAME,
                           act_result_producer.unexpected_contents_after_replacement)]),
                 act_result_producer=act_result_producer,
                 expected_main_result=pfh_check.is_fail()),
            new_source('instruction-name',
                       '{} --with-replaced-env-vars --rel-home {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                          self.COMPARISON_SOURCE_FILE_NAME))
        )

    def test_pass__when__contents_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllEnvVars(Path(self.COMPARISON_TARGET_FILE_NAME))
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(
                     DirContents([File(self.COMPARISON_SOURCE_FILE_NAME,
                                       act_result_producer.expected_contents_after_replacement)])),
                 act_result_producer=act_result_producer),
            new_source('instruction-name',
                       '{} --with-replaced-env-vars --rel-cwd {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                         self.COMPARISON_SOURCE_FILE_NAME))
        )

    def test_fail__when__contents_not_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllEnvVars(Path(self.COMPARISON_TARGET_FILE_NAME))
        self._check(
            Flow(sut.Parser(),
                 eds_contents_before_main=FilesInActDir(
                     DirContents([File(self.COMPARISON_SOURCE_FILE_NAME,
                                       act_result_producer.unexpected_contents_after_replacement)])),
                 act_result_producer=act_result_producer,
                 expected_main_result=pfh_check.is_fail()),
            new_source('instruction-name',
                       '{} --with-replaced-env-vars --rel-cwd {}'.format(self.COMPARISON_TARGET_FILE_NAME,
                                                                         self.COMPARISON_SOURCE_FILE_NAME))
        )

    def test_pass__when__contents_equals_but_src_does_not_reside_inside_act_dir__rel_home(self):
        target_path = Path('..') / self.COMPARISON_TARGET_FILE_NAME
        act_result_producer = ActResultProducerForContentsWithAllEnvVars(target_path)
        self._check(
            Flow(sut.Parser(),
                 home_dir_contents=DirContents([
                     File(self.COMPARISON_SOURCE_FILE_NAME,
                          act_result_producer.expected_contents_after_replacement)]),
                 act_result_producer=act_result_producer),
            new_source('instruction-name',
                       '{} --with-replaced-env-vars --rel-home {}'.format(str(target_path),
                                                                          self.COMPARISON_SOURCE_FILE_NAME))
        )


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestParse))
    ret_val.addTest(unittest.makeSuite(TestFileContentsEmptyInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsEmptyValidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsNonEmptyInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsNonEmptyValidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFileContentsFileRelHome))
    ret_val.addTest(unittest.makeSuite(TestFileContentsFileRelCwd))
    ret_val.addTest(unittest.makeSuite(TestReplacedEnvVars))
    return ret_val


if __name__ == '__main__':
    unittest.main()
