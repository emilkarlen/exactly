import tempfile
import unittest
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, List, ContextManager, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.tcfs.test_resources import application_environment
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.string_model.test_resources import assertions as asrt_string_model
from exactly_lib_test.util.file_utils.test_resources import tmp_file_spaces

ContentsGetter = Callable[[StringModel], str]


class ModelConstructor(ABC):
    @abstractmethod
    def new_with(self, app_env: ApplicationEnvironment) -> ContextManager[StringModel]:
        pass


@contextmanager
def _get_dir_file_space_with_existing_dir() -> ContextManager[DirFileSpace]:
    with tempfile.TemporaryDirectory(prefix='exactly') as tmp_dir_name:
        yield tmp_file_spaces.tmp_dir_file_space_for_test(Path(tmp_dir_name))


class Expectation:
    def __init__(self,
                 expected: ValueAssertion[str],
                 hard_error: Optional[ValueAssertion[TextRenderer]] = None
                 ):
        self.expected = expected
        self.hard_error = hard_error

    @staticmethod
    def equals(expected: str) -> 'Expectation':
        return Expectation(
            expected=asrt.equals(expected)
        )

    @staticmethod
    def hard_error(expected: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text()) -> 'Expectation':
        return Expectation(
            expected=asrt.fail('contents should not be accessed due to HARD_ERROR'),
            hard_error=asrt.is_not_none_and(expected)
        )


class Checker:
    def __init__(self,
                 put: unittest.TestCase,
                 model_constructor: ModelConstructor,
                 expectation: Expectation,
                 get_dir_file_space: Callable[[], ContextManager[DirFileSpace]] = _get_dir_file_space_with_existing_dir
                 ):
        self.put = put
        self.model_constructor = model_constructor
        self.expectation = expectation
        self.get_dir_file_space = get_dir_file_space

    def check(self):
        for case in contents_cases(self.put):
            with self._app_env() as app_env:
                with self.put.subTest(case.name):
                    self._check_getters_sequence(
                        app_env,
                        case.value,
                    )
        self._check_line_sequence_is_valid()

    def check_with_first_access_is_not_write_to(self):
        for case in contents_cases__first_access_is_not_write_to(self.put):
            with self._app_env() as app_env:
                with self.put.subTest(case.name):
                    self._check_getters_sequence(
                        app_env,
                        case.value,
                    )
        self._check_line_sequence_is_valid()

    def _check_line_sequence_is_valid(self):
        if self.expectation.hard_error is not None:
            return
        # ARRANGE #
        with self.put.subTest('check line sequence is valid'):
            with self._app_env() as app_env:
                with self.model_constructor.new_with(app_env) as model_to_check:
                    assertion = asrt_string_model.StringModelLinesAreValidAssertion()
                    # ACT & ASSERT #
                    assertion.apply_with_message(self.put, model_to_check, 'line sequence')

    @contextmanager
    def _app_env(self) -> ContextManager[ApplicationEnvironment]:
        with self.get_dir_file_space() as dir_file_space:
            yield application_environment.application_environment_for_test(
                dir_file_space
            )

    def _check_getters_sequence(self,
                                app_env: ApplicationEnvironment,
                                contents_getters_cases: List[NameAndValue[ContentsGetter]],
                                ):
        # ARRANGE #
        with self.model_constructor.new_with(app_env) as model_to_check:
            for case in contents_getters_cases:
                # ACT #
                try:
                    actual = case.value(model_to_check)
                except HardErrorException as ex:
                    if self.expectation.hard_error is None:
                        self.put.fail('Unexpected HARD_ERROR: ' + str(ex))
                        return
                    else:
                        self.expectation.hard_error.apply_with_message(self.put,
                                                                       ex.error,
                                                                       'HARD_ERROR message')
                        return

                        # ASSERT #
                self.expectation.expected.apply_with_message(self.put,
                                                             actual,
                                                             'contents - ' + case.name)


def _get_contents_from_lines(model: StringModel) -> str:
    with model.as_lines as lines:
        return ''.join(lines)


class _GetContentsFromLinesWIteratorCheck:
    def __init__(self, put: unittest.TestCase):
        self._put = put

    def get_contents(self, model: StringModel) -> str:
        with model.as_lines as lines_iterator:
            lines = list(lines_iterator)

            lines_after_first_iteration = list(lines_iterator)
            self._put.assertEqual([], lines_after_first_iteration,
                                  'as_lines: lines after first iteration should be empty')
            return ''.join(lines)


def _get_contents_from_file(model: StringModel) -> str:
    with model.as_file.open() as model_file:
        return model_file.read()


def _get_contents_via_write_to(model: StringModel) -> str:
    with tempfile.SpooledTemporaryFile(mode='r+') as output_file:
        model.write_to(output_file)
        output_file.seek(0)
        return output_file.read()


def _case__from_lines(put: unittest.TestCase) -> NameAndValue:
    return NameAndValue('as_lines', _GetContentsFromLinesWIteratorCheck(put).get_contents)


def _case__from_file() -> NameAndValue:
    return NameAndValue('as_file', _get_contents_from_file)


def _case__from_write_to() -> NameAndValue:
    return NameAndValue('write_to', _get_contents_via_write_to)


def contents_cases__first_access_is_not_write_to(put: unittest.TestCase,
                                                 ) -> List[NameAndValue[List[NameAndValue[ContentsGetter]]]]:
    case__from_lines = _case__from_lines(put)
    return [
        NameAndValue(
            'file, lines, write_to',
            [
                _case__from_file(),
                case__from_lines,
                _case__from_write_to(),
            ],
        ),
        NameAndValue(
            'file, write_to, lines',
            [
                _case__from_file(),
                _case__from_write_to(),
                case__from_lines,
            ],
        ),
        NameAndValue(
            'lines, file, write_to',
            [
                case__from_lines,
                _case__from_file(),
                _case__from_write_to(),
            ],
        ),
        NameAndValue(
            'lines, write_to, file',
            [
                case__from_lines,
                _case__from_write_to(),
                _case__from_file(),
            ],
        ),
    ]


def contents_cases(put: unittest.TestCase,
                   ) -> List[NameAndValue[List[NameAndValue[ContentsGetter]]]]:
    case__from_lines = _case__from_lines(put)
    first_access_is__write_to = [
        NameAndValue(
            'write_to, lines, file',
            [
                _case__from_write_to(),
                case__from_lines,
                _case__from_file(),
            ],
        ),
        NameAndValue(
            'write_to, file, lines',
            [
                _case__from_write_to(),
                _case__from_file(),
                case__from_lines,
            ],
        ),
    ]
    return contents_cases__first_access_is_not_write_to(put) + first_access_is__write_to
