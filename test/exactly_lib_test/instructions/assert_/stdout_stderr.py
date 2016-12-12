import unittest

from exactly_lib.instructions.assert_ import stdout_stderr as sut
from exactly_lib.instructions.assert_.utils.file_contents.parsing import EQUALS_ARGUMENT, MATCHES_ARGUMENT
from exactly_lib.instructions.utils.arg_parse.relative_path_options import REL_HOME_OPTION
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParser, SingleInstructionParserSource
from exactly_lib.util.string import lines_content
from exactly_lib_test.instructions.assert_.test_resources import instruction_check
from exactly_lib_test.instructions.assert_.test_resources.contents_resources import \
    ActResultProducerForContentsWithAllReplacedEnvVars, \
    OutputContentsToStdout, WriteFileToHomeDir, ActResultContentsSetup, OutputContentsToStderr, WriteFileToCurrentDir
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import ActResultProducer, \
    arrangement, Expectation, is_pass
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementPostAct
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check, svh_check
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.test_resources.execution.sds_populator import act_dir_contents, tmp_user_dir_contents
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.file_structure import DirContents, empty_dir, File
from exactly_lib_test.test_resources.parse import new_source2, argument_list_source
from exactly_lib_test.test_resources.test_case_base_with_short_description import \
    TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType


class TestWithParserBase(instruction_check.TestCaseBase):
    def _new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def _run(self,
             source: SingleInstructionParserSource,
             arrangement: ArrangementPostAct,
             expectation: Expectation):
        self._check(self._new_parser(), source, arrangement, expectation)


class TestConfiguration:
    def new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def act_result(self,
                   exit_code: int = 0,
                   contents_of_tested_file: str = '',
                   contents_of_other_file: str = '') -> ActResult:
        raise NotImplementedError()


class TestConfigurationForStdout(TestConfiguration):
    def new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def act_result(self,
                   exit_code: int = 0,
                   contents_of_tested_file: str = '',
                   contents_of_other_file: str = '') -> ActResult:
        return ActResult(exitcode=exit_code,
                         stdout_contents=contents_of_tested_file,
                         stderr_contents=contents_of_other_file)


class TestConfigurationForStderr(TestConfiguration):
    def new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def act_result(self,
                   exit_code: int = 0,
                   contents_of_tested_file: str = '',
                   contents_of_other_file: str = '') -> ActResult:
        return ActResult(exitcode=exit_code,
                         stderr_contents=contents_of_tested_file,
                         stdout_contents=contents_of_other_file)


class TestWithConfigurationBase(TestCaseBaseWithShortDescriptionOfTestClassAndAnObjectType):
    def __init__(self, configuration: TestConfiguration):
        super().__init__(configuration)
        self.configuration = configuration

    def _check(self,
               source: SingleInstructionParserSource,
               arrangement: ArrangementPostAct,
               expectation: Expectation):
        instruction_check.check(self, self.configuration.new_parser(), source, arrangement, expectation)

    def _act_result_producer(self,
                             exit_code: int = 0,
                             contents_of_tested_file: str = '',
                             contents_of_other_file: str = '') -> ActResultProducer:
        act_result = self.configuration.act_result(exit_code=exit_code,
                                                   contents_of_tested_file=contents_of_tested_file,
                                                   contents_of_other_file=contents_of_other_file)
        return ActResultProducer(act_result)


class FileContentsEmptyInvalidSyntax(TestWithParserBase):
    def _new_parser(self) -> SingleInstructionParser:
        raise NotImplementedError()

    def that_when_superfluous_arguments_then_exception_is_raised(self):
        arguments = 'empty superfluous-argument'
        parser = self._new_parser()
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.apply(new_source2(arguments))

    def that_when_superfluous_arguments_of_valid_here_document(self):
        source = argument_list_source(['empty', '<<MARKER'],
                                      ['single line',
                                       'MARKER'])
        parser = self._new_parser()
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            parser.apply(source)


class TestFileContentsEmptyInvalidSyntaxFORStdout(FileContentsEmptyInvalidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_superfluous_arguments_then_exception_is_raised()

    def test_when_superfluous_arguments_of_valid_here_document(self):
        self.that_when_superfluous_arguments_of_valid_here_document()


class TestFileContentsEmptyInvalidSyntaxFORStderr(FileContentsEmptyInvalidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_superfluous_arguments_then_exception_is_raised()

    def test_when_superfluous_arguments_of_valid_here_document(self):
        self.that_when_superfluous_arguments_of_valid_here_document()


class FileContentsEmptyValidSyntax(TestWithParserBase):
    def fail__when__file_exists_but_is_non_empty(self, act_result: ActResult):
        self._run(
            new_source2('empty'),
            arrangement(act_result_producer=ActResultProducer(act_result)),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def pass__when__file_exists_and_is_empty(self, act_result: ActResult):
        self._run(
            new_source2('empty'),
            arrangement(act_result_producer=ActResultProducer(act_result)),
            is_pass(),
        )


class TestFileContentsEmptyValidSyntaxFORStdout(FileContentsEmptyValidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def test_fail__when__file_exists_but_is_non_empty(self):
        self.fail__when__file_exists_but_is_non_empty(ActResult(stdout_contents='contents',
                                                                stderr_contents=''))

    def test_pass__when__file_exists_and_is_empty(self):
        self.pass__when__file_exists_and_is_empty(ActResult(stderr_contents='non-empty'))


class TestFileContentsEmptyValidSyntaxFORStderr(FileContentsEmptyValidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def test_fail__when__file_exists_but_is_non_empty(self):
        self.fail__when__file_exists_but_is_non_empty(ActResult(stdout_contents='',
                                                                stderr_contents='contents'))

    def test_pass__when__file_exists_and_is_empty(self):
        self.pass__when__file_exists_and_is_empty(ActResult(stdout_contents='non-empty'))


class FileContentsNonEmptyInvalidSyntax(TestWithParserBase):
    def that_when_no_arguments_then_exception_is_raised(self):
        arguments = '! empty superfluous-argument'
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self._new_parser().apply(new_source2(arguments))

    def that_when_superfluous_arguments_of_valid_here_document(self):
        source = argument_list_source(['!', 'empty', '<<MARKER'],
                                      ['single line',
                                       'MARKER'])
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self._new_parser().apply(source)


class TestFileContentsNonEmptyInvalidSyntaxFORStdout(FileContentsNonEmptyInvalidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_no_arguments_then_exception_is_raised()

    def test_that_when_superfluous_arguments_of_valid_here_document(self):
        self.that_when_superfluous_arguments_of_valid_here_document()


class TestFileContentsNonEmptyInvalidSyntaxFORStderr(FileContentsNonEmptyInvalidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def test_that_when_no_arguments_then_exception_is_raised(self):
        self.that_when_no_arguments_then_exception_is_raised()

    def test_that_when_superfluous_arguments_of_valid_here_document(self):
        self.that_when_superfluous_arguments_of_valid_here_document()


class FileContentsNonEmptyValidSyntax(TestWithParserBase):
    def fail__when__file_exists_but_is_empty(self, act_result: ActResult):
        self._run(
            new_source2('! empty'),
            arrangement(act_result_producer=ActResultProducer(act_result)),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def pass__when__file_exists_and_is_non_empty(self, act_result: ActResult):
        self._run(
            new_source2('! empty'),
            arrangement(act_result_producer=ActResultProducer(act_result)),
            is_pass(),
        )


class TestFileContentsNonEmptyValidSyntaxFORStdout(FileContentsNonEmptyValidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def test_fail__when__file_exists_but_is_empty(self):
        self.fail__when__file_exists_but_is_empty(ActResult(stdout_contents='',
                                                            stderr_contents='non-empty'))

    def test_pass__when__file_exists_and_is_non_empty(self):
        self.pass__when__file_exists_and_is_non_empty(ActResult(stdout_contents='non-empty',
                                                                stderr_contents=''))


class TestFileContentsNonEmptyValidSyntaxFORStderr(FileContentsNonEmptyValidSyntax):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def test_fail__when__file_exists_but_is_empty(self):
        self.fail__when__file_exists_but_is_empty(ActResult(stdout_contents='non-empty',
                                                            stderr_contents=''))

    def test_pass__when__file_exists_and_is_non_empty(self):
        self.pass__when__file_exists_and_is_non_empty(ActResult(stdout_contents='',
                                                                stderr_contents='non-empty'))


class TestParseMatchesWithMissingRegExArgument(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(new_source2(MATCHES_ARGUMENT))


class TestParseMatchesWithSuperfluousArgument(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(new_source2('{} abc superfluous'.format(MATCHES_ARGUMENT)))


class TestParseMatchesWithInvalidRegEx(TestWithConfigurationBase):
    def runTest(self):
        with self.assertRaises(SingleInstructionInvalidArgumentException):
            self.configuration.new_parser().apply(new_source2('{} **'.format(MATCHES_ARGUMENT)))


class TestMatchesShouldFailWhenNoLineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'NO MATCH',
                                         'not match'])
        act_result_producer = self._act_result_producer(contents_of_tested_file=actual_contents)
        reg_ex = '123'
        self._check(
            new_source2("%s '%s'" % (MATCHES_ARGUMENT, reg_ex)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestMatchesShouldPassWhenALineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        act_result_producer = self._act_result_producer(contents_of_tested_file=actual_contents)
        reg_ex = 'ATC'
        self._check(
            new_source2("%s '%s'" % (MATCHES_ARGUMENT, reg_ex)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_pass()),
        )


class TestMatchesShouldPassWhenAWholeLineMatchesRegEx(TestWithConfigurationBase):
    def runTest(self):
        actual_contents = lines_content(['no match',
                                         'MATCH',
                                         'not match'])
        act_result_producer = self._act_result_producer(contents_of_tested_file=actual_contents)
        reg_ex = '^MATCH$'
        self._check(
            new_source2("%s '%s'" % (MATCHES_ARGUMENT, reg_ex)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_pass()),
        )


def suite_for_matches(configuration: TestConfiguration) -> unittest.TestSuite:
    test_cases = [
        TestParseMatchesWithMissingRegExArgument,
        TestParseMatchesWithSuperfluousArgument,
        TestParseMatchesWithInvalidRegEx,
        TestMatchesShouldFailWhenNoLineMatchesRegEx,
        TestMatchesShouldPassWhenALineMatchesRegEx,
        TestMatchesShouldPassWhenAWholeLineMatchesRegEx,
    ]
    return unittest.TestSuite([tc(configuration) for tc in test_cases])


class FileContentsFileRelHome(TestWithParserBase):
    def validation_error__when__comparison_file_does_not_exist(self):
        self._run(
            new_source2('%s %s f.txt' % (EQUALS_ARGUMENT, REL_HOME_OPTION)),
            arrangement(),
            Expectation(validation_pre_sds=svh_check.is_validation_error()),
        )

    def validation_error__when__comparison_file_is_a_directory(self):
        self._run(
            new_source2('%s %s dir' % (EQUALS_ARGUMENT, REL_HOME_OPTION)),
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_dir('dir')]))),
            Expectation(validation_pre_sds=svh_check.is_validation_error()),
        )

    def fail__when__contents_differ(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._run(
            new_source2('%s %s f.txt' % (EQUALS_ARGUMENT, REL_HOME_OPTION)),
            arrangement(act_result_producer=ActResultProducer(act_result),
                        home_dir_contents=DirContents(
                            [File('f.txt', expected_contents)])),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def pass__when__contents_equals(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._run(
            new_source2('%s %s f.txt' % (EQUALS_ARGUMENT, REL_HOME_OPTION)),
            arrangement(home_dir_contents=DirContents([File('f.txt', expected_contents)]),
                        act_result_producer=ActResultProducer(act_result)),
            is_pass(),
        )


class TestFileContentsFileRelHomeFORStdout(FileContentsFileRelHome):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

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
        return sut.ParserForContentsForStderr()

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
        self._run(
            new_source2('%s --rel-cwd f.txt' % EQUALS_ARGUMENT),
            arrangement(),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def fail__when__comparison_file_is_a_directory(self):
        self._run(
            new_source2('%s --rel-cwd dir' % EQUALS_ARGUMENT),
            arrangement(sds_contents_before_main=act_dir_contents(DirContents(
                [empty_dir('dir')]))),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def fail__when__contents_differ(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._run(
            new_source2('%s --rel-cwd f.txt' % EQUALS_ARGUMENT),
            arrangement(
                sds_contents_before_main=act_dir_contents(DirContents(
                    [File('f.txt', expected_contents)])),
                act_result_producer=ActResultProducer(act_result)),
            Expectation(
                main_result=pfh_check.is_fail()),
        )

    def pass__when__contents_equals(self,
                                    act_result: ActResult,
                                    expected_contents: str):
        self._run(
            new_source2('%s --rel-cwd f.txt' % EQUALS_ARGUMENT),
            arrangement(
                sds_contents_before_main=act_dir_contents(DirContents(
                    [File('f.txt', expected_contents)])),
                act_result_producer=ActResultProducer(act_result)),
            is_pass(),
        )


class FileContentsFileRelTmp(TestWithParserBase):
    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        raise NotImplementedError()

    def fail__when__comparison_file_does_not_exist(self):
        self._run(
            new_source2('%s --rel-tmp f.txt' % EQUALS_ARGUMENT),
            arrangement(),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def pass__when__contents_equals(self):
        self._run(
            new_source2('%s --rel-tmp f.txt' % EQUALS_ARGUMENT),
            arrangement(
                sds_contents_before_main=tmp_user_dir_contents(DirContents(
                    [File('f.txt', 'expected contents')])),
                act_result_producer=ActResultProducer(
                    self._act_result_with_contents('expected contents'))),
            is_pass(),
        )


class FileContentsHereDoc(TestWithParserBase):
    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        raise NotImplementedError()

    def pass__when__contents_equals(self):
        self._run(
            argument_list_source([EQUALS_ARGUMENT, '<<EOF'],
                                 ['single line',
                                  'EOF']),
            arrangement(act_result_producer=ActResultProducer(
                self._act_result_with_contents(lines_content(['single line'])))),
            is_pass(),
        )


class TestFileContentsFileRelCwdFORStdout(FileContentsFileRelCwd):
    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

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
        return sut.ParserForContentsForStderr()

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


class TestFileContentsFileRelTmpFORStdout(FileContentsFileRelTmp):
    def test_fail__when__comparison_file_does_not_exist(self):
        self.fail__when__comparison_file_does_not_exist()

    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stdout_contents=contents_on_tested_channel,
                         stderr_contents=contents_on_other_channel)


class TestFileContentsFileRelTmpFORStderr(FileContentsFileRelTmp):
    def test_fail__when__comparison_file_does_not_exist(self):
        self.fail__when__comparison_file_does_not_exist()

    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stderr_contents=contents_on_tested_channel,
                         stdout_contents=contents_on_other_channel)


class FileContentsHereDocFORStdout(FileContentsHereDoc):
    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stdout_contents=contents_on_tested_channel,
                         stderr_contents=contents_on_other_channel)


class FileContentsHereDocFORStderr(FileContentsHereDoc):
    def test_pass__when__contents_equals(self):
        self.pass__when__contents_equals()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()

    def _act_result_with_contents(self,
                                  contents_on_tested_channel: str,
                                  contents_on_other_channel: str = '') -> ActResult:
        return ActResult(stderr_contents=contents_on_tested_channel,
                         stdout_contents=contents_on_other_channel)


class ReplacedEnvVars(TestWithParserBase):
    SOURCE_FILE_NAME = 'with-replaced-env-vars.txt'

    def __init__(self,
                 act_result_contents_setup: ActResultContentsSetup,
                 method_name):
        super().__init__(method_name)
        self._act_result_contents_setup = act_result_contents_setup

    def pass__when__contents_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToHomeDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=True)
        self._run(
            new_source2('--with-replaced-env-vars {} --rel-home {}'.format(EQUALS_ARGUMENT,
                                                                           self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            is_pass(),

        )

    def fail__when__contents_not_equals__rel_home(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToHomeDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=False)
        self._run(
            new_source2('--with-replaced-env-vars {} --rel-home {}'.format(EQUALS_ARGUMENT,
                                                                           self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def pass__when__contents_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToCurrentDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=True)
        self._run(
            new_source2('--with-replaced-env-vars {} --rel-cwd {}'.format(EQUALS_ARGUMENT,
                                                                          self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            is_pass(),
        )

    def fail__when__contents_not_equals__rel_cwd(self):
        act_result_producer = ActResultProducerForContentsWithAllReplacedEnvVars(
            self._act_result_contents_setup,
            source_file_writer=WriteFileToCurrentDir(self.SOURCE_FILE_NAME),
            source_should_contain_expected_value=False)
        self._run(
            new_source2('--with-replaced-env-vars {} --rel-cwd {}'.format(EQUALS_ARGUMENT,
                                                                          self.SOURCE_FILE_NAME)),
            arrangement(act_result_producer=act_result_producer),
            Expectation(main_result=pfh_check.is_fail()),
        )


class TestReplacedEnvVarsFORStdout(ReplacedEnvVars):
    def __init__(self, method_name):
        super().__init__(OutputContentsToStdout(), method_name)

    def test_pass__when__contents_equals__rel_home(self):
        self.pass__when__contents_equals__rel_home()

    def test_fail__when__contents_not_equals__rel_home(self):
        self.fail__when__contents_not_equals__rel_home()

    def test_pass__when__contents_equals__rel_cwd(self):
        self.pass__when__contents_equals__rel_cwd()

    def test_fail__when__contents_not_equals__rel_cwd(self):
        self.fail__when__contents_not_equals__rel_cwd()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStdout()


class TestReplacedEnvVarsFORStderr(ReplacedEnvVars):
    def __init__(self, method_name):
        super().__init__(OutputContentsToStderr(), method_name)

    def test_pass__when__contents_equals__rel_home(self):
        self.pass__when__contents_equals__rel_home()

    def test_fail__when__contents_not_equals__rel_home(self):
        self.fail__when__contents_not_equals__rel_home()

    def test_pass__when__contents_equals__rel_cwd(self):
        self.pass__when__contents_equals__rel_cwd()

    def test_fail__when__contents_not_equals__rel_cwd(self):
        self.fail__when__contents_not_equals__rel_cwd()

    def _new_parser(self) -> SingleInstructionParser:
        return sut.ParserForContentsForStderr()


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([

        unittest.makeSuite(TestFileContentsEmptyInvalidSyntaxFORStdout),
        unittest.makeSuite(TestFileContentsEmptyInvalidSyntaxFORStderr),

        unittest.makeSuite(TestFileContentsEmptyValidSyntaxFORStdout),
        unittest.makeSuite(TestFileContentsEmptyValidSyntaxFORStderr),

        unittest.makeSuite(TestFileContentsNonEmptyInvalidSyntaxFORStdout),
        unittest.makeSuite(TestFileContentsNonEmptyInvalidSyntaxFORStderr),

        unittest.makeSuite(TestFileContentsNonEmptyValidSyntaxFORStdout),
        unittest.makeSuite(TestFileContentsNonEmptyValidSyntaxFORStderr),

        suite_for_matches(TestConfigurationForStdout()),
        suite_for_matches(TestConfigurationForStderr()),

        unittest.makeSuite(TestFileContentsFileRelHomeFORStdout),
        unittest.makeSuite(TestFileContentsFileRelHomeFORStderr),

        unittest.makeSuite(TestFileContentsFileRelCwdFORStdout),
        unittest.makeSuite(TestFileContentsFileRelCwdFORStderr),

        unittest.makeSuite(FileContentsHereDocFORStdout),
        unittest.makeSuite(FileContentsHereDocFORStderr),

        unittest.makeSuite(TestReplacedEnvVarsFORStdout),
        unittest.makeSuite(TestReplacedEnvVarsFORStderr),

        unittest.makeSuite(TestFileContentsFileRelTmpFORStdout),
        unittest.makeSuite(TestFileContentsFileRelTmpFORStderr),

        suite_for_instruction_documentation(sut.TheInstructionDocumentation('instruction name', 'file')),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
