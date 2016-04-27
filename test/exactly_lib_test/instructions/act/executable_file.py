import os
import types

from exactly_lib.instructions.act import executable_file as sut
from exactly_lib_test.instructions.act.test_resources.instruction_check import *
from exactly_lib_test.instructions.test_resources import svh_check__va
from exactly_lib_test.test_resources.file_structure import DirContents, executable_file
from exactly_lib_test.test_resources.file_utils import absolute_path_to_executable_file


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValidation),
        unittest.makeSuite(TestStatementGeneration),
    ])


class TestBase(TestCaseBase):
    def _check(self,
               source: str,
               arrangement: Arrangement,
               expectation: Expectation):
        super()._check(sut.ExecutableFileInstruction(source),
                       arrangement,
                       expectation)


class TestValidation(TestBase):
    def test_fails_when_command_is_relative_but_does_not_exist_relative_home__no_arguments(self):
        self._check('relative-path-of-non-existing-program',
                    Arrangement(),
                    Expectation(validation_pre_eds=svh_check__va.is_validation_error()))

    def test_fails_when_command_is_relative_but_does_not_exist_relative_home__with_arguments(self):
        relative_path = 'relative-path-of-existing-program'
        self._check('%s argument-to-program' % relative_path,
                    Arrangement(),
                    Expectation(validation_pre_eds=svh_check__va.is_validation_error()))


class TestStatementGeneration(TestBase):
    def test_absolute_path_is_absolute__sans_arguments(self):
        with absolute_path_to_executable_file() as absolute_path:
            source = str(absolute_path)
            self._check(source,
                        Arrangement(),
                        Expectation(main_side_effects_on_script_source=_contains_single_line(source)))

    def test_absolute_path_is_absolute__with_arguments(self):
        with absolute_path_to_executable_file() as absolute_path:
            source = '%s argument1 argument2' % str(absolute_path)
            self._check(source,
                        Arrangement(),
                        Expectation(main_side_effects_on_script_source=_contains_single_line(source)))

    def test_that_relative_path_is_transformed_to_absolute_path__sans_arguments(self):
        relative_path = 'relative-path-of-existing-program'
        source = relative_path
        self._check(source,
                    Arrangement(home_dir_contents=DirContents([
                        executable_file(relative_path, '')])),
                    Expectation(main_side_effects_on_script_source=_contains_single_line__with_home_prepended(source)))

    def test_that_relative_path_is_transformed_to_absolute_path__with_arguments(self):
        relative_path = 'relative-path-of-existing-program'
        source = '%s argument-to-program' % relative_path
        self._check(source,
                    Arrangement(home_dir_contents=DirContents([
                        executable_file(relative_path, '')])),
                    Expectation(main_side_effects_on_script_source=_contains_single_line__with_home_prepended(source)))


class LineCheckInfo(tuple):
    def __new__(cls,
                home_and_eds: HomeAndEds,
                source_line: str):
        return tuple.__new__(cls, (home_and_eds,
                                   source_line))

    @property
    def home_and_eds(self) -> HomeAndEds:
        return self[0]

    @property
    def source_line(self) -> str:
        return self[1]


def _contains_single_line(line: str) -> va.ValueAssertion:
    return ContainsSingleLine(LineChecker(lambda x: line))


def _contains_single_line__with_home_prepended(line: str) -> va.ValueAssertion:
    def prepend_home(home_and_eds: HomeAndEds) -> str:
        return str(home_and_eds.home_dir_path) + os.path.sep + line

    return ContainsSingleLine(LineChecker(prepend_home))


class ContainsSingleLine(va.ValueAssertion):
    def __init__(self,
                 line_assertion: va.ValueAssertion):
        self.line_assertion = line_assertion

    def apply(self,
              put: unittest.TestCase,
              value: SourceBuilderCheckInfo,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        source_builder = value.source_builder
        put.assertEqual(1,
                        len(source_builder.source_lines),
                        'Number of source lines')
        self.line_assertion.apply(put,
                                  LineCheckInfo(value.home_and_eds,
                                                source_builder.source_lines[0]),
                                  va.sub_component_builder('line[0]',
                                                           message_builder))


class LineChecker(va.ValueAssertion):
    def __init__(self,
                 get_expected: types.FunctionType):
        self.get_expected = get_expected

    def apply(self,
              put: unittest.TestCase,
              value: LineCheckInfo,
              message_builder: va.MessageBuilder = va.MessageBuilder()):
        va.Equals(self.get_expected(value.home_and_eds)).apply(put, value.source_line)
