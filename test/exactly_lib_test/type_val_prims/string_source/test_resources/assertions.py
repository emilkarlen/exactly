import unittest
from abc import ABC
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, IO, Sequence, Optional

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_prims.string_source.string_source import StringSource
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
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_base import StringSourceTestImplBase
from exactly_lib_test.util.description_tree.test_resources import rendering_assertions as asrt_trace_rendering


class StringSourceLinesAreValidAssertion(ValueAssertionBase[StringSource]):
    def _apply(self,
               put: unittest.TestCase,
               value: StringSource,
               message_builder: MessageBuilder,
               ):
        source_checker = StringSourceThatThatChecksLines(put, value)
        self._check_lines_by_iterating_over_them(source_checker)

    @staticmethod
    def _check_lines_by_iterating_over_them(model_checker: StringSource):
        with model_checker.as_lines as lines:
            for _ in lines:
                pass


class WithLinesCheck(ValueAssertionBase[StringSource]):
    def __init__(self, on_checked_model: ValueAssertion[StringSource]):
        self._on_checked_model = on_checked_model

    def _apply(self,
               put: unittest.TestCase,
               value: StringSource,
               message_builder: MessageBuilder,
               ):
        checked_source = StringSourceThatThatChecksLines(put, value)
        self._on_checked_model.apply(put, checked_source, message_builder)


class StringSourceThatThatChecksLines(StringSourceTestImplBase):
    def __init__(self,
                 put: unittest.TestCase,
                 checked: StringSource,
                 ):
        self._put = put
        self._checked = checked

    def freeze(self):
        self._checked.freeze()

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
    def _tmp_file_space(self) -> DirFileSpace:
        return self._checked._tmp_file_space

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
                   ) -> ValueAssertion[StringSource]:
    return asrt.and_([
        asrt.named(
            'non-contents properties',
            non_contents_assertion(may_depend_on_external_resources)
        ),
        asrt.named(
            'contents',
            WithLinesCheck(contents_variants_assertion__lines(lines))
        ),
    ])


def matches__lines__pre_post_freeze__identical(lines: ValueAssertion[Sequence[str]],
                                               may_depend_on_external_resources: ValueAssertion[bool],
                                               ) -> ValueAssertion[StringSource]:
    return before_and_after_freeze(
        matches__lines(lines, may_depend_on_external_resources)
    )


def matches__lines__pre_post_freeze__any_frozen_ext_deps(lines: ValueAssertion[Sequence[str]],
                                                         may_depend_on_external_resources: ValueAssertion[bool],
                                                         ) -> ValueAssertion[StringSource]:
    return matches__lines__pre_post_freeze(
        lines,
        may_depend_on_external_resources,
        frozen_may_depend_on_external_resources=asrt.anything_goes(),
    )


def matches__lines__pre_post_freeze(lines: ValueAssertion[Sequence[str]],
                                    may_depend_on_external_resources: ValueAssertion[bool],
                                    frozen_may_depend_on_external_resources: ValueAssertion[bool],
                                    ) -> ValueAssertion[StringSource]:
    return before_and_after_freeze_2(
        matches__lines(lines, may_depend_on_external_resources),
        matches__lines(lines, frozen_may_depend_on_external_resources),
    )


def matches__str(contents: ValueAssertion[str],
                 may_depend_on_external_resources: ValueAssertion[bool],
                 ) -> ValueAssertion[StringSource]:
    return asrt.and_([
        asrt.named(
            'non-contents properties',
            non_contents_assertion(may_depend_on_external_resources),
        ),
        asrt.named(
            'contents',
            WithLinesCheck(contents_variants_assertion__str(contents)),
        ),
    ])


def before_and_after_freeze(expectation: ValueAssertion[StringSource],
                            ) -> ValueAssertion[StringSource]:
    return before_and_after_freeze_2(expectation, expectation)


def before_and_after_freeze_2(before_freeze: ValueAssertion[StringSource],
                              after_freeze: ValueAssertion[StringSource],
                              ) -> ValueAssertion[StringSource]:
    return asrt.and_([
        asrt.named(
            'before freeze',
            before_freeze,
        ),
        asrt.named(
            'after freeze',
            asrt.after_manipulation(
                _freeze_string_source,
                after_freeze,
            ),
        ),
    ])


def matches__str__before_and_after_freeze(contents: ValueAssertion[str],
                                          may_depend_on_external_resources: ValueAssertion[bool],
                                          frozen_may_depend_on_external_resources: ValueAssertion[bool],
                                          ) -> ValueAssertion[StringSource]:
    return before_and_after_freeze_2(
        matches__str(contents, may_depend_on_external_resources),
        matches__str(contents, frozen_may_depend_on_external_resources),
    )


def matches__str__before_and_after_freeze__const(contents: str,
                                                 may_depend_on_external_resources: bool,
                                                 ) -> ValueAssertion[StringSource]:
    return matches__str__before_and_after_freeze(
        asrt.equals(contents),
        asrt.equals(may_depend_on_external_resources),
        asrt.equals(may_depend_on_external_resources),
    )


def matches__str__before_and_after_freeze__const_2(contents: str,
                                                   may_depend_on_external_resources: bool,
                                                   frozen_may_depend_on_external_resources: ValueAssertion[bool],
                                                   ) -> ValueAssertion[StringSource]:
    return matches__str__before_and_after_freeze(
        asrt.equals(contents),
        asrt.equals(may_depend_on_external_resources),
        asrt.is_instance_with(bool, frozen_may_depend_on_external_resources),
    )


def matches__lines__check_just_as_lines(lines: Sequence[str],
                                        ) -> ValueAssertion[StringSource]:
    return asrt.and_([
        asrt.sub_component(
            'structure',
            properties_access.get_structure,
            asrt_trace_rendering.matches_node_renderer(),
        ),
        WithLinesCheck(
            asrt.sub_component(
                'as_lines',
                properties_access.get_contents_from_as_lines,
                asrt.equals(lines),
            )
        ),
    ])


def contents_raises_hard_error(may_depend_on_external_resources: ValueAssertion[bool],
                               ) -> ValueAssertion[StringSource]:
    return asrt.and_([
        asrt.named(
            'non-contents properties',
            non_contents_assertion(may_depend_on_external_resources),
        ),
        asrt.named(
            'contents',
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


def contents_and_ext_dep_raises_hard_error() -> ValueAssertion[StringSource]:
    return asrt.and_([
        asrt.named(
            'non-contents properties',
            non_contents_assertion_2(
                ext_dependencies_raises_hard_error()
            ),
        ),
        asrt.named(
            'contents',
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


def non_contents_assertion(may_depend_on_external_resources: ValueAssertion[bool]) -> ValueAssertion[StringSource]:
    return non_contents_assertion_2(
        asrt.sub_component(
            'may_depend_on_external_resources',
            get_may_depend_on_external_resources,
            may_depend_on_external_resources,
        )
    )


def non_contents_assertion_2(may_depend_on_external_resources: ValueAssertion[StringSource],
                             ) -> ValueAssertion[StringSource]:
    return asrt.and_([
        asrt.sub_component(
            'structure',
            properties_access.get_structure,
            asrt_trace_rendering.matches_node_renderer(),
        ),
        asrt.named('external dependencies',
                   may_depend_on_external_resources),
    ])


def ext_dependencies_raises_hard_error() -> ValueAssertion[StringSource]:
    return asrt.named(
        'may_depend_on_external_resources',
        RaisesHardErrorAsLastAction(_get_may_depend_on_external_resources),
    )


def ext_dependencies_gives(expected: bool) -> ValueAssertion[StringSource]:
    return ext_dependencies(asrt.equals(expected))


def ext_dependencies(expectation: ValueAssertion[bool] = asrt.is_instance(bool)) -> ValueAssertion[StringSource]:
    return asrt.sub_component(
        'may_depend_on_external_resources',
        get_may_depend_on_external_resources,
        expectation,
    )


def structure_assertion() -> ValueAssertion[StringSource]:
    return asrt.sub_component(
        'structure',
        properties_access.get_structure,
        asrt_trace_rendering.matches_node_renderer(),
    )


def contents_variants_assertion__str(expected: ValueAssertion[str]) -> ValueAssertion[StringSource]:
    return asrt.and_([
        asrt.sub_component(
            variant.name,
            variant.value,
            expected,
        )
        for variant in properties_access.contents_cases__str()
    ])


def contents_variants_assertion__lines(expected: ValueAssertion[Sequence[str]]) -> ValueAssertion[StringSource]:
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
                 may_depend_on_external_resources: ValueAssertion[StringSource] = ext_dependencies(),
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
            may_depend_on_external_resources=ext_dependencies(may_depend_on_external_resources)
        )

    @staticmethod
    def hard_error(expected: ValueAssertion[TextRenderer] = asrt_text_doc.is_any_text(),
                   may_depend_on_external_resources: ValueAssertion[StringSource] = ext_dependencies(),
                   ) -> 'Expectation':
        return Expectation(
            contents=asrt.anything_goes(),
            may_depend_on_external_resources=may_depend_on_external_resources,
            hard_error=asrt.is_not_none_and(expected)
        )


class ContentsVariantsSequenceAssertion(ValueAssertionBase[StringSource], ABC):
    def __init__(self,
                 expectation: Expectation,
                 contents_getters_cases: Sequence[NameAndValue[ContentsAsStrGetter]],
                 ):
        self._expectation = expectation
        self._contents_getters_cases = contents_getters_cases

    def _apply(self,
               put: unittest.TestCase,
               value: StringSource,
               message_builder: asrt.MessageBuilder,
               ):
        # ARRANGE #
        expectation = self._expectation
        model_to_check__w_lines_check = StringSourceThatThatChecksLines(put, value)
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


def _freeze_string_source(x: StringSource):
    x.freeze()


def _get_may_depend_on_external_resources(x: StringSource) -> bool:
    return x.may_depend_on_external_resources
