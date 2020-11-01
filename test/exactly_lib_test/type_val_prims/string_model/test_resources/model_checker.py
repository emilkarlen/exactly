import itertools
import tempfile
import unittest
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Callable, List, ContextManager, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_deps.dep_variants.adv.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_val_deps.dep_variants.test_resources import application_environment
from exactly_lib_test.type_val_prims.string_model.test_resources import assertions as asrt_string_model
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
                 contents: ValueAssertion[str],
                 may_depend_on_external_resources: ValueAssertion[bool] = asrt_text_doc.is_any_text(),
                 hard_error: Optional[ValueAssertion[TextRenderer]] = None
                 ):
        self.contents = contents
        self.may_depend_on_external_resources = may_depend_on_external_resources
        self.hard_error = hard_error

    @staticmethod
    def equals(contents: str,
               may_depend_on_external_resources: ValueAssertion[bool],
               ) -> 'Expectation':
        return Expectation(
            contents=asrt.equals(contents),
            may_depend_on_external_resources=may_depend_on_external_resources
        )

    @staticmethod
    def hard_error(expected: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text(),
                   may_depend_on_external_resources: ValueAssertion[bool] = asrt.anything_goes(),
                   ) -> 'Expectation':
        return Expectation(
            contents=asrt.fail('contents should not be accessed due to HARD_ERROR'),
            may_depend_on_external_resources=may_depend_on_external_resources,
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
        self._check_may_depend_on_external_resources()

        cases = contents_cases(self.put)
        for case in cases:
            with self._app_env() as app_env:
                with self.put.subTest(case.name):
                    self._check_getters_sequence(
                        app_env,
                        case.value,
                    )

        self._check_line_sequence_is_valid()

    def check_with_first_access_is_not_write_to(self):
        self._check_may_depend_on_external_resources()

        cases = contents_cases__first_access_is_not_write_to(self.put)
        for case in cases:
            with self._app_env() as app_env:
                with self.put.subTest(case.name):
                    self._check_getters_sequence(
                        app_env,
                        case.value,
                    )

        self._check_line_sequence_is_valid()

    def _check_may_depend_on_external_resources(self):
        # ARRANGE #
        with self.put.subTest('may_depend_on_external_resources'):
            with self._app_env() as app_env:
                with self.model_constructor.new_with(app_env) as model_to_check:
                    self.expectation.may_depend_on_external_resources.apply_without_message(
                        self.put,
                        model_to_check.may_depend_on_external_resources,
                    )

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
                self.expectation.contents.apply_with_message(self.put,
                                                             actual,
                                                             'contents - ' + case.name)


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


def _get_contents_from_str(model: StringModel) -> str:
    return model.as_str


def _get_contents_via_write_to(model: StringModel) -> str:
    with tempfile.SpooledTemporaryFile(mode='r+') as output_file:
        model.write_to(output_file)
        output_file.seek(0)
        return output_file.read()


def _case__from_lines(put: unittest.TestCase) -> NameAndValue:
    return NameAndValue('as_lines', _GetContentsFromLinesWIteratorCheck(put).get_contents)


def _case__from_str() -> NameAndValue:
    return NameAndValue('as_str', _get_contents_from_str)


def _case__from_file() -> NameAndValue:
    return NameAndValue('as_file', _get_contents_from_file)


def _case__from_write_to() -> NameAndValue:
    return NameAndValue('write_to', _get_contents_via_write_to)


def contents_cases__first_access_is_not_write_to(put: unittest.TestCase,
                                                 ) -> List[NameAndValue[List[NameAndValue[ContentsGetter]]]]:
    alternative_str = _case__from_str()
    alternative_lines = _case__from_lines(put)
    alternative_file = _case__from_file()
    alternative_write_to = _case__from_write_to()

    alternatives_after_str = [
        alternative_lines,
        alternative_file,
        alternative_write_to,
    ]

    alternatives_after_lines = [
        alternative_str,
        alternative_file,
        alternative_write_to,
    ]

    alternatives_after_file = [
        alternative_str,
        alternative_lines,
        alternative_write_to,
    ]

    return (
            _sequences_for_alternatives_w_initial(alternative_str, alternatives_after_str) +
            _sequences_for_alternatives_w_initial(alternative_lines, alternatives_after_lines) +
            _sequences_for_alternatives_w_initial(alternative_file, alternatives_after_file)
    )


def contents_cases(put: unittest.TestCase,
                   ) -> List[NameAndValue[List[NameAndValue[ContentsGetter]]]]:
    return _sequences_for_alternatives([
        _case__from_str(),
        _case__from_lines(put),
        _case__from_file(),
        _case__from_write_to(),
    ])


def _sequence_from_getters(sequence: List[NameAndValue[ContentsGetter]],
                           ) -> NameAndValue[List[NameAndValue[ContentsGetter]]]:
    name = ', '.join([
        nav.name
        for nav in sequence
    ])

    return NameAndValue(
        name,
        sequence,
    )


def _sequences_for_alternatives_w_initial(initial: NameAndValue[ContentsGetter],
                                          following_alternatives: List[NameAndValue[ContentsGetter]],
                                          ) -> List[NameAndValue[List[NameAndValue[ContentsGetter]]]]:
    following_variants = itertools.permutations(following_alternatives)

    variants = [
        [initial] + list(following_variant)
        for following_variant in following_variants
    ]

    return list(map(_sequence_from_getters, variants))


def _sequences_for_alternatives(alternatives: List[NameAndValue[ContentsGetter]],
                                ) -> List[NameAndValue[List[NameAndValue[ContentsGetter]]]]:
    variants = itertools.permutations(alternatives)

    return list(map(_sequence_from_getters, variants))
