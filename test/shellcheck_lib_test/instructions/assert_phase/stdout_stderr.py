import unittest

from shellcheck_lib.instructions.assert_phase import stdout_stderr
from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParser
from shellcheck_lib_test.instructions.assert_phase.test_resources.instruction_check import Flow, ActResultProducer
from shellcheck_lib_test.instructions.assert_phase.test_resources import instruction_check
from shellcheck_lib_test.instructions.test_resources import pfh_check
from shellcheck_lib_test.instructions.test_resources import svh_check
from shellcheck_lib_test.instructions.test_resources.eds_populator import FilesInActDir
from shellcheck_lib_test.instructions.utils import new_source, ActResult
from shellcheck_lib_test.util.file_structure import DirContents, empty_dir, File


class TestWithParserBase(instruction_check.TestCaseBase):
    def new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()


class FileContentsEmptyInvalidSyntax(TestWithParserBase):
    def new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def that_when_no_arguments_then_exception_is_raised(self):
        arguments = 'empty superfluous-argument'
        parser = self.new_parser()
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.apply(new_source('instruction-name',
                                    arguments))


class TestFileContentsEmptyInvalidSyntaxFORStdout(FileContentsEmptyInvalidSyntax):
    def new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStdout()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_no_arguments_then_exception_is_raised()


class TestFileContentsEmptyInvalidSyntaxFORStderr(FileContentsEmptyInvalidSyntax):
    def new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStderr()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_no_arguments_then_exception_is_raised()


class FileContentsEmptyValidSyntax(TestWithParserBase):
    def fail__when__file_exists_but_is_non_empty(self, act_result: ActResult):
        self._check(
            Flow(self.new_parser(),
                 act_result_producer=ActResultProducer(ActResult(stdout_contents='contents',
                                                                 stderr_contents='contents')),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       'empty'))

    def pass__when__file_exists_and_is_empty(self, act_result: ActResult):
        self._check(
            Flow(self.new_parser()),
            new_source('instruction-name',
                       'empty'))


class TestFileContentsEmptyValidSyntaxFORStdout(FileContentsEmptyValidSyntax):
    def new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStdout()

    def test_fail__when__file_exists_but_is_non_empty(self):
        self.fail__when__file_exists_but_is_non_empty(ActResult(stdout_contents='contents',
                                                                stderr_contents=''))

    def test_pass__when__file_exists_and_is_empty(self):
        self.pass__when__file_exists_and_is_empty(ActResult(stderr_contents='non-empty'))


class TestFileContentsEmptyValidSyntaxFORStderr(FileContentsEmptyValidSyntax):
    def new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStderr()

    def test_fail__when__file_exists_but_is_non_empty(self):
        self.fail__when__file_exists_but_is_non_empty(ActResult(stdout_contents='',
                                                                stderr_contents='contents'))

    def test_pass__when__file_exists_and_is_empty(self):
        self.pass__when__file_exists_and_is_empty(ActResult(stdout_contents='non-empty'))


class FileContentsNonEmptyInvalidSyntax(TestWithParserBase):
    def that_when_no_arguments_then_exception_is_raised(self):
        arguments = '! empty superfluous-argument'
        parser = self.new_parser()
        self.assertRaises(SingleInstructionInvalidArgumentException,
                          parser.apply,
                          new_source('instruction-name',
                                     arguments))


class TestFileContentsNonEmptyInvalidSyntaxFORStdout(FileContentsNonEmptyInvalidSyntax):
    def new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStdout()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_no_arguments_then_exception_is_raised()


class TestFileContentsNonEmptyInvalidSyntaxFORStderr(FileContentsNonEmptyInvalidSyntax):
    def new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStderr()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_no_arguments_then_exception_is_raised()


class FileContentsNonEmptyValidSyntax(TestWithParserBase):
    def fail__when__file_exists_but_is_empty(self, act_result: ActResult):
        self._check(
            Flow(self.new_parser(),
                 act_result_producer=ActResultProducer(act_result),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       '! empty'))

    def pass__when__file_exists_and_is_non_empty(self, act_result: ActResult):
        self._check(
            Flow(self.new_parser(),
                 act_result_producer=ActResultProducer(act_result)),
            new_source('instruction-name',
                       '! empty'))


class TestFileContentsNonEmptyValidSyntaxFORStdout(FileContentsNonEmptyValidSyntax):
    def new_parser(self) -> SingleInstructionParser:
        return stdout_stderr.ParserForContentsForStdout()

    def test_fail__when__file_exists_but_is_empty(self):
        self.fail__when__file_exists_but_is_empty(ActResult(stdout_contents='',
                                                            stderr_contents='non-empty'))

    def test_pass__when__file_exists_and_is_non_empty(self):
        self.pass__when__file_exists_and_is_non_empty(ActResult(stdout_contents='non-empty',
                                                                stderr_contents=''))


class TestFileContentsNonEmptyValidSyntaxFORStderr(FileContentsNonEmptyValidSyntax):
    def new_parser(self) -> SingleInstructionParser:
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
            Flow(self.new_parser(),
                 expected_validation_result=svh_check.is_validation_error(),
                 ),
            new_source('instruction-name',
                       '--rel-home f.txt'))

    def validation_error__when__comparison_file_is_a_directory(self):
        self._check(
            Flow(self.new_parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_dir('dir')])),
                 expected_validation_result=svh_check.is_validation_error(),
                 ),
            new_source('instruction-name',
                       '--rel-home dir'))

    def fail__when__contents_differ(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._check(
            Flow(self.new_parser(),
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
            Flow(self.new_parser(),
                 home_dir_contents=DirContents([File('f.txt', expected_contents)]),
                 act_result_producer=ActResultProducer(act_result)),
            new_source('instruction-name',
                       '--rel-home f.txt'))


class TestFileContentsFileRelHomeFORStdout(FileContentsFileRelHome):
    def new_parser(self) -> SingleInstructionParser:
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
    def new_parser(self) -> SingleInstructionParser:
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
            Flow(self.new_parser(),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       '--rel-cwd f.txt'))

    def fail__when__comparison_file_is_a_directory(self):
        self._check(
            Flow(self.new_parser(),
                 eds_contents_before_main=FilesInActDir(DirContents([empty_dir('dir')])),
                 expected_main_result=pfh_check.is_fail(),
                 ),
            new_source('instruction-name',
                       '--rel-cwd dir'))

    def fail__when__contents_differ(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._check(
            Flow(self.new_parser(),
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
            Flow(self.new_parser(),
                 eds_contents_before_main=FilesInActDir(
                     DirContents([File('f.txt', expected_contents)])),
                 act_result_producer=ActResultProducer(act_result),
                 ),
            new_source('instruction-name',
                       '--rel-cwd f.txt'))


class TestFileContentsFileRelCwdFORStdout(FileContentsFileRelCwd):
    def new_parser(self) -> SingleInstructionParser:
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
    def new_parser(self) -> SingleInstructionParser:
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
    return ret_val


if __name__ == '__main__':
    unittest.main()
