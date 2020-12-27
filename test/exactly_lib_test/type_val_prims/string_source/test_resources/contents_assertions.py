import unittest
from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, IO, Sequence, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_case.test_resources.hard_error_assertion import RaisesHardErrorAsLastAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase, MessageBuilder, \
    ValueAssertion
from exactly_lib_test.type_val_prims.string_source.test_resources import properties_access
from exactly_lib_test.type_val_prims.string_source.test_resources.properties_access import \
    get_may_depend_on_external_resources, ContentsAsStrGetter


class StringSourceContentsLinesAreValidAssertion(ValueAssertionBase[StringSourceContents]):
    def _apply(self,
               put: unittest.TestCase,
               value: StringSourceContents,
               message_builder: MessageBuilder,
               ):
        source_checker = StringSourceContentsThatThatChecksLines(put, value)
        self._check_lines_by_iterating_over_them(source_checker)

    @staticmethod
    def _check_lines_by_iterating_over_them(model_checker: StringSourceContents):
        with model_checker.as_lines as lines:
            for _ in lines:
                pass


class WithLinesCheck(ValueAssertionBase[StringSourceContents]):
    def __init__(self, on_checked_model: ValueAssertion[StringSourceContents]):
        self._on_checked_model = on_checked_model

    def _apply(self,
               put: unittest.TestCase,
               value: StringSourceContents,
               message_builder: MessageBuilder,
               ):
        checked_contents = StringSourceContentsThatThatChecksLines(put, value)
        self._on_checked_model.apply(put, checked_contents, message_builder)


class StringSourceContentsThatThatChecksLines(StringSourceContents):
    def __init__(self,
                 put: unittest.TestCase,
                 checked: StringSourceContents,
                 ):
        self._put = put
        self._checked = checked

    @property
    def may_depend_on_external_resources(self) -> bool:
        return self._checked.may_depend_on_external_resources

    @property
    def as_str(self) -> str:
        return self._checked.as_str

    @property
    def as_file(self) -> Path:
        return self._checked.as_file

    @property
    @contextmanager
    def as_lines(self) -> ContextManager[Iterator[str]]:
        with self._checked.as_lines as lines:
            yield self._check_and_return_iterator(lines)

    def write_to(self, output: IO):
        self._checked.write_to(output)

    @property
    def tmp_file_space(self) -> DirFileSpace:
        return self._checked.tmp_file_space

    def _check_and_return_iterator(self, lines: Iterator[str]) -> Iterator[str]:
        for line in lines:
            current_line = line
            self._check_any_line(current_line)
            yield current_line
            break
        else:
            return

        for next_line in lines:
            self._check_non_last_line(current_line)
            current_line = next_line
            self._check_any_line(current_line)
            yield current_line

    def _check_any_line(self, line: str):
        if line == '':
            return
        match_idx = line.find('\n\n')
        if match_idx != -1:
            self._put.fail('Multiple new-lines: ' + repr(line))
        match_idx = line.find('\n')
        if match_idx != -1:
            if match_idx != len(line) - 1:
                self._put.fail('New-line is not final char: ' + repr(line))

    def _check_non_last_line(self, line: str):
        if line == '':
            self._put.fail('Non-last line: is empty')
        last_char = line[-1]
        if last_char != '\n':
            self._put.fail('Non-last line: last char is not new-line: ' + repr(line))


def matches__lines(lines: ValueAssertion[Sequence[str]],
                   may_depend_on_external_resources: ValueAssertion[bool],
                   ) -> ValueAssertion[StringSourceContents]:
    return asrt.and_([
        external_dependencies(may_depend_on_external_resources),
        actual_contents__w_lines_check(
            actual_contents_variants_assertion__lines(lines)
        ),
    ])


def matches__str(contents: ValueAssertion[str],
                 may_depend_on_external_resources: ValueAssertion[bool],
                 ) -> ValueAssertion[StringSourceContents]:
    return asrt.and_([
        external_dependencies(may_depend_on_external_resources),
        actual_contents__w_lines_check(
            actual_contents_variants_assertion__str(contents)
        ),
    ])


def actual_contents(expectation: ValueAssertion[StringSourceContents]
                    ) -> ValueAssertion[StringSourceContents]:
    return asrt.named(
        'actual contents',
        expectation,
    )


def actual_contents__w_lines_check(expectation: ValueAssertion[StringSourceContents]
                                   ) -> ValueAssertion[StringSourceContents]:
    return actual_contents(WithLinesCheck(expectation))


def actual_contents_matches__lines__check_just_as_lines(lines: Sequence[str],
                                                        ) -> ValueAssertion[StringSourceContents]:
    return WithLinesCheck(
        asrt.sub_component(
            'as_lines',
            properties_access.get_contents_from_as_lines,
            asrt.equals(lines),
        )
    )


def contents_raises_hard_error(may_depend_on_external_resources: ValueAssertion[bool],
                               ) -> ValueAssertion[StringSourceContents]:
    return asrt.and_([
        external_dependencies(may_depend_on_external_resources),
        actual_contents(
            asrt.and_([
                asrt.named(
                    contents_case.name,
                    RaisesHardErrorAsLastAction(contents_case.value)
                )
                for contents_case in properties_access.ALL_CASES__WO_LINES_ITER_CHECK
            ]),
        ),
    ])


def contents_raises_hard_error__including_ext_deps() -> ValueAssertion[StringSourceContents]:
    return asrt.and_([
        asrt.named(
            'may_have_external_dependencies',
            ext_dependencies_raises_hard_error(),
        ),
        actual_contents(
            asrt.and_([
                asrt.named(
                    contents_case.name,
                    RaisesHardErrorAsLastAction(
                        contents_case.value
                    )
                )
                for contents_case in properties_access.ALL_CASES__WO_LINES_ITER_CHECK
            ]),
        ),
    ])


def ext_dependencies_raises_hard_error() -> ValueAssertion[StringSourceContents]:
    return asrt.named(
        'may_depend_on_external_resources',
        RaisesHardErrorAsLastAction(properties_access.get_may_depend_on_external_resources),
    )


def external_dependencies__const(expected: bool) -> ValueAssertion[StringSourceContents]:
    return external_dependencies(asrt.equals(expected))


def external_dependencies(expectation: ValueAssertion[bool] = asrt.anything_goes()
                          ) -> ValueAssertion[StringSourceContents]:
    return asrt.sub_component(
        'may_depend_on_external_resources',
        get_may_depend_on_external_resources,
        asrt.is_instance_with(bool, expectation),
    )


def actual_contents_variants_assertion__str(expected: ValueAssertion[str]) -> ValueAssertion[StringSourceContents]:
    return asrt.and_([
        asrt.sub_component(
            variant.name,
            variant.value,
            expected,
        )
        for variant in properties_access.contents_cases__str()
    ])


def actual_contents_variants_assertion__lines(expected: ValueAssertion[Sequence[str]]
                                              ) -> ValueAssertion[StringSourceContents]:
    return asrt.and_([
        asrt.sub_component(
            variant.name,
            variant.value,
            expected,
        )
        for variant in properties_access.contents_cases__lines_sequence()
    ])


class Expectation:
    def __init__(self,
                 contents: ValueAssertion[str],
                 may_depend_on_external_resources: ValueAssertion[StringSourceContents] = external_dependencies(),
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
            may_depend_on_external_resources=external_dependencies(may_depend_on_external_resources)
        )

    @staticmethod
    def hard_error(expected: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text(),
                   may_depend_on_external_resources: ValueAssertion[StringSourceContents] = external_dependencies(),
                   ) -> 'Expectation':
        return Expectation(
            contents=asrt.anything_goes(),
            may_depend_on_external_resources=may_depend_on_external_resources,
            hard_error=asrt.is_not_none_and(expected)
        )


class ActualContentsVariantsSequenceAssertion(ValueAssertionBase[StringSourceContents], ABC):
    def __init__(self,
                 expectation: Expectation,
                 contents_getters_cases: Sequence[NameAndValue[ContentsAsStrGetter]],
                 ):
        self._expectation = expectation
        self._contents_getters_cases = contents_getters_cases

    def _apply(self,
               put: unittest.TestCase,
               value: StringSourceContents,
               message_builder: asrt.MessageBuilder,
               ):
        self._check_actual_contents(
            put,
            value,
            message_builder.for_sub_component('actual contents')
        )
        self._check_external_dependencies(
            put,
            value,
            message_builder.for_sub_component('may_depend_on_external_resources')
        )

    def _check_external_dependencies(self,
                                     put: unittest.TestCase,
                                     value: StringSourceContents,
                                     message_builder: asrt.MessageBuilder,
                                     ):
        # ARRANGE #
        expectation = self._expectation
        expectation.may_depend_on_external_resources.apply(put, value, message_builder)

    def _check_actual_contents(self,
                               put: unittest.TestCase,
                               value: StringSourceContents,
                               message_builder: asrt.MessageBuilder,
                               ):
        # ARRANGE #
        expectation = self._expectation
        model_to_check__w_lines_check = StringSourceContentsThatThatChecksLines(put, value)
        for case in self._contents_getters_cases:
            case_msg_builder = message_builder.for_sub_component(case.name)
            # ACT & ASSERT #
            try:
                actual = case.value(model_to_check__w_lines_check)
            except HardErrorException as ex:
                if expectation.hard_error is None:
                    err_msg = case_msg_builder.apply(
                        'Unexpected HARD_ERROR: ' + str(ex)
                    )
                    put.fail(err_msg)
                    return
                else:
                    expectation.hard_error.apply(
                        put,
                        ex.error,
                        case_msg_builder.for_sub_component('HARD_ERROR message'),
                    )
                    raise asrt.StopAssertion()

            if expectation.hard_error is not None:
                put.fail(case_msg_builder.apply('HARD_ERROR not raised'))
            else:
                expectation.contents.apply(put, actual, case_msg_builder)
