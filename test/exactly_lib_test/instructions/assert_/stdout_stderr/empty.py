import unittest

from exactly_lib.instructions.assert_ import stdout_stderr as sut
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException, SingleInstructionParser
from exactly_lib_test.instructions.assert_.stdout_stderr.test_resources import TestWithParserBase
from exactly_lib_test.instructions.assert_.test_resources.instruction_check import arrangement, Expectation, is_pass
from exactly_lib_test.instructions.test_resources.arrangements import ActResultProducerFromActResult
from exactly_lib_test.instructions.test_resources.assertion_utils import pfh_check
from exactly_lib_test.test_resources.execution.utils import ActResult
from exactly_lib_test.test_resources.parse import new_source2, argument_list_source


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
            arrangement(act_result_producer=ActResultProducerFromActResult(act_result)),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def pass__when__file_exists_and_is_empty(self, act_result: ActResult):
        self._run(
            new_source2('empty'),
            arrangement(act_result_producer=ActResultProducerFromActResult(act_result)),
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
            arrangement(act_result_producer=ActResultProducerFromActResult(act_result)),
            Expectation(main_result=pfh_check.is_fail()),
        )

    def pass__when__file_exists_and_is_non_empty(self, act_result: ActResult):
        self._run(
            new_source2('! empty'),
            arrangement(act_result_producer=ActResultProducerFromActResult(act_result)),
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
    ])
