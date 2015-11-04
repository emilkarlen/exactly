import unittest

from shellcheck_lib.execution import environment_variables
from shellcheck_lib.instructions.assert_phase import stdout_stderr
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParser
from shellcheck_lib_test.instructions.assert_phase.test_resources.contents_resources import \
    ActResultProducerForContentsWithAllEnvVarsBase
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Flow, ActResultProducer, \
    ActEnvironment
from shellcheck_lib_test.instructions.assert_phase.test_resources import instruction_check
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources.eds_populator import FilesInActDir
from shellcheck_lib_test.instructions.utils import new_source, ActResult
from shellcheck_lib_test.util.file_structure import DirContents, empty_dir, File


class TestWithParserBase(instruction_check.TestCaseBase):
    def _new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()


class FileContentsEmptyInvalidSyntax(TestWithParserBase):
    def _new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def that_when_no_arguments_then_exception_is_raised(self):
        arguments = 'empty superfluous-argument'
        parser = self._new_parser()
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.apply(new_source('instruction-name',
                                    arguments))


class TestFileContentsEmptyInvalidSyntaxFORStdout(FileContentsEmptyInvalidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStdout()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_no_arguments_then_exception_is_raised()


class TestFileContentsEmptyInvalidSyntaxFORStderr(FileContentsEmptyInvalidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStderr()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_no_arguments_then_exception_is_raised()


class FileContentsEmptyValidSyntax(TestWithParserBase):
    def fail__when__file_exists_but_is_non_empty(self, act_result: ActResult):
        self._check(
            Flow(self._new_parser(),
                 act_result_producer=ActResultProducer(ActResult(stdout_contents='contents',
                                                                 stderr_contents='contents')),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       'empty'))

    def pass__when__file_exists_and_is_empty(self, act_result: ActResult):
        self._check(
            Flow(self._new_parser()),
            new_source('instruction-name',
                       'empty'))


class TestFileContentsEmptyValidSyntaxFORStdout(FileContentsEmptyValidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStdout()

    def test_fail__when__file_exists_but_is_non_empty(self):
        self.fail__when__file_exists_but_is_non_empty(ActResult(stdout_contents='contents',
                                                                stderr_contents=''))

    def test_pass__when__file_exists_and_is_empty(self):
        self.pass__when__file_exists_and_is_empty(ActResult(stderr_contents='non-empty'))


class TestFileContentsEmptyValidSyntaxFORStderr(FileContentsEmptyValidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStderr()

    def test_fail__when__file_exists_but_is_non_empty(self):
        self.fail__when__file_exists_but_is_non_empty(ActResult(stdout_contents='',
                                                                stderr_contents='contents'))

    def test_pass__when__file_exists_and_is_empty(self):
        self.pass__when__file_exists_and_is_empty(ActResult(stdout_contents='non-empty'))


class FileContentsNonEmptyInvalidSyntax(TestWithParserBase):
    def that_when_no_arguments_then_exception_is_raised(self):
        arguments = '! empty superfluous-argument'
        parser = self._new_parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name',
                                     arguments))


class TestFileContentsNonEmptyInvalidSyntaxFORStdout(FileContentsNonEmptyInvalidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStdout()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_no_arguments_then_exception_is_raised()


class TestFileContentsNonEmptyInvalidSyntaxFORStderr(FileContentsNonEmptyInvalidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStderr()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_no_arguments_then_exception_is_raised()


class FileContentsNonEmptyValidSyntax(TestWithParserBase):
    def fail__when__file_exists_but_is_empty(self, act_result: ActResult):
        self._check(
            Flow(self._new_parser(),
                 act_result_producer=ActResultProducer(act_result),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       '! empty'))

    def pass__when__file_exists_and_is_non_empty(self, act_result: ActResult):
        self._check(
            Flow(self._new_parser(),
                 act_result_producer=ActResultProducer(act_result)),
            new_source('instruction-name',
                       '! empty'))


class TestFileContentsNonEmptyValidSyntaxFORStdout(FileContentsNonEmptyValidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStdout()

    def test_fail__when__file_exists_but_is_empty(self):
        self.fail__when__file_exists_but_is_empty(ActResult(stdout_contents='',
                                                            stderr_contents='non-empty'))

    def test_pass__when__file_exists_and_is_non_empty(self):
        self.pass__when__file_exists_and_is_non_empty(ActResult(stdout_contents='non-empty',
                                                                stderr_contents=''))


class TestFileContentsNonEmptyValidSyntaxFORStderr(FileContentsNonEmptyValidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStderr()

    def test_fail__when__file_exists_but_is_empty(self):
        self.fail__when__file_exists_but_is_empty(ActResult(stdout_contents='non-empty',
                                                            stderr_contents=''))

    def test_pass__when__file_exists_and_is_non_empty(self):
        self.pass__when__file_exists_and_is_non_empty(ActResult(stdout_contents='',
                                                                stderr_contents='non-empty'))


class FileContentsFileRelHome(TestWithParserBase):
    def validation_error__when__comparison_file_does_not_exist(self):
        self._check(
            Flow(self._new_parser(),
                 expected_validation_result=svh_check.is_validation_error(),
                 ),
            new_source('instruction-name',
                       '--rel-home f.txt'))

    def validation_error__when__comparison_file_is_a_directory(self):
        self._check(
            Flow(self._new_parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_dir('dir')])),
                 expected_validation_result=svh_check.is_validation_error(),
                 ),
            new_source('instruction-name',
                       '--rel-home dir'))

    def fail__when__contents_differ(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._check(
            Flow(self._new_parser(),
                 act_result_producer=ActResultProducer(act_result),
                 home_dir_contents=DirContents(
                     [File('f.txt', expected_contents)]),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       '--rel-home f.txt'))

    def pass__when__contents_equals(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._check(
            Flow(self._new_parser(),
                 home_dir_contents=DirContents([File('f.txt', expected_contents)]),
                 act_result_producer=ActResultProducer(act_result)),
            new_source('instruction-name',
                       '--rel-home f.txt'))


class TestFileContentsFileRelHomeFORStdout(FileContentsFileRelHome):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStdout()

    def test_validation_error__when__comparison_file_does_not_exist(self):
        self.validation_error__when__comparison_file_does_not_exist()

    def test_validation_error__when__comparison_file_is_a_directory(self):
        self.validation_error__when__comparison_file_is_a_directory()

    def test_fail__when__contents_differ(self):
        self.fail__when__contents_differ(ActResult(stdout_contents='un-expected',
                                                   stderr_contents='expected'),
                                         'expected')

    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals(ActResult(stdout_contents='expected',
                                                   stderr_contents='un-expected'),
                                         'expected')


class TestFileContentsFileRelHomeFORStderr(FileContentsFileRelHome):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStderr()

    def test_validation_error__when__comparison_file_does_not_exist(self):
        self.validation_error__when__comparison_file_does_not_exist()

    def test_validation_error__when__comparison_file_is_a_directory(self):
        self.validation_error__when__comparison_file_is_a_directory()

    def test_fail__when__contents_differ(self):
        self.fail__when__contents_differ(ActResult(stdout_contents='expected',
                                                   stderr_contents='un-expected'),
                                         'expected')

    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals(ActResult(stdout_contents='un-expected',
                                                   stderr_contents='expected'),
                                         'expected')


class FileContentsFileRelCwd(TestWithParserBase):
    def fail__when__comparison_file_does_not_exist(self):
        self._check(
            Flow(self._new_parser(),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       '--rel-cwd f.txt'))

    def fail__when__comparison_file_is_a_directory(self):
        self._check(
            Flow(self._new_parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_dir('dir')])),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       '--rel-cwd dir'))

    def fail__when__contents_differ(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._check(
            Flow(self._new_parser(),
                 eds_contents_before_main=FilesInActDir(
                     DirContents([File('f.txt', expected_contents)])),
                 act_result_producer=ActResultProducer(act_result),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       '--rel-cwd f.txt'))

    def pass__when__contents_equals(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._check(
            Flow(self._new_parser(),
                 eds_contents_before_main=FilesInActDir(
                     DirContents([File('f.txt', expected_contents)])),
                 act_result_producer=ActResultProducer(act_result),
                 ),
            new_source('instruction-name',
                       '--rel-cwd f.txt'))


class TestFileContentsFileRelCwdFORStdout(FileContentsFileRelCwd):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStdout()

    def test_fail__when__comparison_file_does_not_exist(self):
        self.fail__when__comparison_file_does_not_exist()

    def test_fail__when__comparison_file_is_a_directory(self):
        self.fail__when__comparison_file_is_a_directory()

    def test_fail__when__contents_differ(self):
        self.fail__when__contents_differ(ActResult(stdout_contents='un-expected',
                                                   stderr_contents='expected'),
                                         'expected')

    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals(ActResult(stdout_contents='expected',
                                                   stderr_contents='un-expected'),
                                         'expected')


class TestFileContentsFileRelCwdFORStderr(FileContentsFileRelCwd):
    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStderr()

    def test_validation_error__when__comparison_file_does_not_exist(self):
        self.fail__when__comparison_file_does_not_exist()

    def test_validation_error__when__comparison_file_is_a_directory(self):
        self.fail__when__comparison_file_is_a_directory()

    def test_fail__when__contents_differ(self):
        self.fail__when__contents_differ(ActResult(stdout_contents='expected',
                                                   stderr_contents='un-expected'),
                                         'expected')

    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals(ActResult(stdout_contents='un-expected',
                                                   stderr_contents='expected'),
                                         'expected')


class ActResultProducerForContentsWithAllEnvVars(ActResultProducerForContentsWithAllEnvVarsBase):
    def __init__(self, is_produce_to_stdout: bool):
        super().__init__()
        self.is_produce_to_stdout = is_produce_to_stdout

    def apply(self, act_environment: ActEnvironment) -> ActResult:
        home_and_eds = act_environment.home_and_eds
        env_vars_dict = environment_variables.all_environment_variables(home_and_eds.home_dir_path,
                                                                        home_and_eds.eds)
        values_in_determined_order = list(map(env_vars_dict.get, self.sorted_env_var_keys))
        contents = self._content_from_values(values_in_determined_order)
        return self._result_with(contents)

    def _result_with(self, contents: str) -> ActResult:
        stdout_contents = ''
        stderr_contents = ''
        if self.is_produce_to_stdout:
            stdout_contents = contents
        else:
            stderr_contents = contents
        return ActResult(stdout_contents=stdout_contents,
                         stderr_contents=stderr_contents)


class ReplacedEnvVars(TestWithParserBase):
    SOURCE_FILE_NAME = 'with-replaced-env-vars.txt'

    def __init__(self,
                 is_produce_to_stdout: bool,
                 method_name):
        super().__init__(method_name)
        self.act_result_producer = ActResultProducerForContentsWithAllEnvVars(is_produce_to_stdout)

    def pass__when__contents_equals__rel_home(self):
        self._check(
            Flow(self._new_parser(),
                 home_dir_contents=DirContents([
                     File(self.SOURCE_FILE_NAME,
                          self.act_result_producer.expected_contents_after_replacement)]),
                 act_result_producer=self.act_result_producer),
            new_source('instruction-name',
                       '--with-replaced-env-vars --rel-home {}'.format(self.SOURCE_FILE_NAME))
        )

    def fail__when__contents_not_equals__rel_home(self):
        self._check(
            Flow(self._new_parser(),
                 home_dir_contents=DirContents(
                     [File(self.SOURCE_FILE_NAME,
                           self.act_result_producer.unexpected_contents_after_replacement)]),
                 act_result_producer=self.act_result_producer,
                 expected_main_result=pfh_check.is_fail()),
            new_source('instruction-name',
                       '--with-replaced-env-vars --rel-home {}'.format(self.SOURCE_FILE_NAME))
        )

    def pass__when__contents_equals__rel_cwd(self):
        self._check(
            Flow(self._new_parser(),
                 eds_contents_before_main=FilesInActDir(
                     DirContents([File(self.SOURCE_FILE_NAME,
                                       self.act_result_producer.expected_contents_after_replacement)])),
                 act_result_producer=self.act_result_producer),
            new_source('instruction-name',
                       '--with-replaced-env-vars --rel-cwd {}'.format(self.SOURCE_FILE_NAME))
        )

    def fail__when__contents_not_equals__rel_cwd(self):
        self._check(
            Flow(self._new_parser(),
                 eds_contents_before_main=FilesInActDir(
                     DirContents([File(self.SOURCE_FILE_NAME,
                                       self.act_result_producer.unexpected_contents_after_replacement)])),
                 act_result_producer=self.act_result_producer,
                 expected_main_result=pfh_check.is_fail()),
            new_source('instruction-name',
                       '--with-replaced-env-vars --rel-cwd {}'.format(self.SOURCE_FILE_NAME))
        )


class ReplacedEnvVarsFORStdout(ReplacedEnvVars):
    def __init__(self, method_name):
        super().__init__(True, method_name)

    def test_pass__when__contents_equals__rel_home(self):
        self.pass__when__contents_equals__rel_home()

    def test_fail__when__contents_not_equals__rel_home(self):
        self.fail__when__contents_not_equals__rel_home()

    def test_pass__when__contents_equals__rel_cwd(self):
        self.pass__when__contents_equals__rel_cwd()

    def test_fail__when__contents_not_equals__rel_cwd(self):
        self.fail__when__contents_not_equals__rel_cwd()

    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStdout()


class ReplacedEnvVarsFORStderr(ReplacedEnvVars):
    def __init__(self, method_name):
        super().__init__(False, method_name)

    def test_pass__when__contents_equals__rel_home(self):
        self.pass__when__contents_equals__rel_home()

    def test_fail__when__contents_not_equals__rel_home(self):
        self.fail__when__contents_not_equals__rel_home()

    def test_pass__when__contents_equals__rel_cwd(self):
        self.pass__when__contents_equals__rel_cwd()

    def test_fail__when__contents_not_equals__rel_cwd(self):
        self.fail__when__contents_not_equals__rel_cwd()

    def _new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStderr()


def suite():
    ret_val = unittest.TestSuite()

    ret_val.addTest(unittest.makeSuite(TestFileContentsEmptyInvalidSyntaxFORStdout))
    ret_val.addTest(unittest.makeSuite(TestFileContentsEmptyInvalidSyntaxFORStderr))

    ret_val.addTest(unittest.makeSuite(TestFileContentsEmptyValidSyntaxFORStdout))
    ret_val.addTest(unittest.makeSuite(TestFileContentsEmptyValidSyntaxFORStderr))

    ret_val.addTest(unittest.makeSuite(TestFileContentsNonEmptyInvalidSyntaxFORStdout))
    ret_val.addTest(unittest.makeSuite(TestFileContentsNonEmptyInvalidSyntaxFORStderr))

    ret_val.addTest(unittest.makeSuite(TestFileContentsNonEmptyValidSyntaxFORStdout))
    ret_val.addTest(unittest.makeSuite(TestFileContentsNonEmptyValidSyntaxFORStderr))

    ret_val.addTest(unittest.makeSuite(TestFileContentsFileRelHomeFORStdout))
    ret_val.addTest(unittest.makeSuite(TestFileContentsFileRelHomeFORStderr))

    ret_val.addTest(unittest.makeSuite(TestFileContentsFileRelCwdFORStdout))
    ret_val.addTest(unittest.makeSuite(TestFileContentsFileRelCwdFORStderr))

    ret_val.addTest(unittest.makeSuite(ReplacedEnvVarsFORStdout))
    ret_val.addTest(unittest.makeSuite(ReplacedEnvVarsFORStderr))

    return ret_val


if __name__ == '__main__':
    unittest.main()
