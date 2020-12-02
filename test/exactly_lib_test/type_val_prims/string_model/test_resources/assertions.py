import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import ContextManager, Iterator, IO, Sequence

from exactly_lib.type_val_prims.string_model.string_model import StringModel
from exactly_lib.util.file_utils.dir_file_space import DirFileSpace
from exactly_lib_test.test_case.test_resources.hard_error_assertion import RaisesHardError
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase, MessageBuilder, \
    ValueAssertion
from exactly_lib_test.type_val_prims.string_model.test_resources import properties_access
from exactly_lib_test.type_val_prims.string_model.test_resources.properties_access import \
    get_may_depend_on_external_resources
from exactly_lib_test.type_val_prims.string_model.test_resources.string_model_base import StringModelTestImplBase
from exactly_lib_test.util.description_tree.test_resources import rendering_assertions as asrt_trace_rendering


class StringModelLinesAreValidAssertion(ValueAssertionBase[StringModel]):
    def _apply(self,
               put: unittest.TestCase,
               value: StringModel,
               message_builder: MessageBuilder,
               ):
        model_checker = StringModelThatThatChecksLines(put, value)
        self._check_lines_by_iterating_over_them(model_checker)

    @staticmethod
    def _check_lines_by_iterating_over_them(model_checker: StringModel):
        with model_checker.as_lines as lines:
            for _ in lines:
                pass


class WithLinesCheck(ValueAssertionBase[StringModel]):
    def __init__(self, on_checked_model: ValueAssertion[StringModel]):
        self._on_checked_model = on_checked_model

    def _apply(self,
               put: unittest.TestCase,
               value: StringModel,
               message_builder: MessageBuilder,
               ):
        checked_model = StringModelThatThatChecksLines(put, value)
        self._on_checked_model.apply(put, checked_model, message_builder)


class StringModelThatThatChecksLines(StringModelTestImplBase):
    def __init__(self,
                 put: unittest.TestCase,
                 checked: StringModel,
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
                   ) -> ValueAssertion[StringModel]:
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


def matches__str(contents: ValueAssertion[str],
                 may_depend_on_external_resources: ValueAssertion[bool],
                 ) -> ValueAssertion[StringModel]:
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


def matches__str__const(contents: str,
                        may_depend_on_external_resources: bool,
                        ) -> ValueAssertion[StringModel]:
    return matches__str(asrt.equals(contents), asrt.equals(may_depend_on_external_resources))


def matches__lines__check_just_as_lines(lines: Sequence[str],
                                        ) -> ValueAssertion[StringModel]:
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
                               ) -> ValueAssertion[StringModel]:
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
                    RaisesHardError(
                        contents_case.value
                    )
                )
                for contents_case in properties_access.ALL_CASES__WO_LINES_ITER_CHECK
            ]),
        ),
    ])


def non_contents_assertion(may_depend_on_external_resources: ValueAssertion[bool]) -> ValueAssertion[StringModel]:
    return asrt.and_([
        asrt.sub_component(
            'structure',
            properties_access.get_structure,
            asrt_trace_rendering.matches_node_renderer(),
        ),
        asrt.sub_component(
            'may_depend_on_external_resources',
            get_may_depend_on_external_resources,
            may_depend_on_external_resources,
        ),
    ])


def contents_variants_assertion__str(expected: ValueAssertion[str]) -> ValueAssertion[StringModel]:
    return asrt.and_([
        asrt.sub_component(
            variant.name,
            variant.value,
            expected,
        )
        for variant in properties_access.contents_cases__str()
    ])


def contents_variants_assertion__lines(expected: ValueAssertion[Sequence[str]]) -> ValueAssertion[StringModel]:
    return asrt.and_([
        asrt.sub_component(
            variant.name,
            variant.value,
            expected,
        )
        for variant in properties_access.contents_cases__lines_sequence()
    ])
