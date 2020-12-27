import unittest
from typing import Sequence

from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.type_val_prims.string_source.structure_builder import StringSourceStructureBuilder
from exactly_lib_test.test_case.test_resources.hard_error_assertion import RaisesHardErrorAsLastAction
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertionBase, MessageBuilder, \
    ValueAssertion
from exactly_lib_test.type_val_prims.string_source.test_resources import contents_assertions as asrt_str_src_contents
from exactly_lib_test.type_val_prims.string_source.test_resources import properties_access, contents_assertions
from exactly_lib_test.type_val_prims.string_source.test_resources.string_source_base import StringSourceTestImplBase
from exactly_lib_test.util.description_tree.test_resources import rendering_assertions as asrt_trace_rendering


class StringSourceLinesAreValidAssertion(ValueAssertionBase[StringSource]):
    def _apply(self,
               put: unittest.TestCase,
               value: StringSource,
               message_builder: MessageBuilder,
               ):
        source_checker = contents_assertions.StringSourceContentsThatThatChecksLines(put, value.contents())
        self._check_lines_by_iterating_over_them(source_checker)

    @staticmethod
    def _check_lines_by_iterating_over_them(model: StringSourceContents):
        with model.as_lines as lines:
            for _ in lines:
                pass


class StringSourceThatThatChecksLines(StringSourceTestImplBase):
    def __init__(self,
                 put: unittest.TestCase,
                 checked: StringSource,
                 ):
        self._put = put
        self._checked = checked

    def new_structure_builder(self) -> StringSourceStructureBuilder:
        return self._checked.new_structure_builder()

    def freeze(self):
        self._checked.freeze()

    def contents(self) -> StringSourceContents:
        return contents_assertions.StringSourceContentsThatThatChecksLines(self._put, self._checked.contents())


def matches__str(contents: ValueAssertion[str],
                 may_depend_on_external_resources: ValueAssertion[bool],
                 ) -> ValueAssertion[StringSource]:
    return asrt.and_([
        has_valid_structure_description(),
        contents_matches(
            asrt.and_([
                asrt_str_src_contents.WithLinesCheck(
                    asrt_str_src_contents.actual_contents_variants_assertion__str(contents)
                ),
                asrt_str_src_contents.external_dependencies(may_depend_on_external_resources),
            ]),
        ),
    ])


def matches__lines__check_just_as_lines(lines: Sequence[str],
                                        ) -> ValueAssertion[StringSource]:
    return asrt.and_([
        has_valid_structure_description(),
        contents_matches(
            asrt_str_src_contents.WithLinesCheck(
                asrt.sub_component(
                    'as_lines',
                    properties_access.get_contents_from_as_lines,
                    asrt.equals(lines),
                )
            ),
        )
    ])


def contents_raises_hard_error(may_depend_on_external_resources: ValueAssertion[bool],
                               ) -> ValueAssertion[StringSource]:
    return asrt.and_([
        has_valid_structure_description(),
        contents_matches(
            asrt.and_(
                [asrt_str_src_contents.external_dependencies(may_depend_on_external_resources)] +
                [
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
        has_valid_structure_description(),
        contents_matches(
            asrt.and_(
                [asrt_str_src_contents.ext_dependencies_raises_hard_error()]
                +
                [
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


def has_valid_structure_description() -> ValueAssertion[StringSource]:
    return asrt.sub_component(
        'structure',
        properties_access.get_structure,
        asrt_trace_rendering.matches_node_renderer(),
    )


def contents_matches(expectation: ValueAssertion[StringSourceContents]) -> ValueAssertion[StringSource]:
    return asrt.sub_component(
        'contents',
        properties_access.get_string_source_contents,
        expectation
    )


def pre_post_freeze(before_freeze: ValueAssertion[StringSourceContents],
                    after_freeze: ValueAssertion[StringSourceContents],
                    ) -> ValueAssertion[StringSource]:
    return asrt.and_([
        has_valid_structure_description(),
        asrt.named(
            'pre freeze',
            contents_matches(before_freeze),
        ),
        asrt.named(
            'post freeze',
            asrt.after_manipulation(
                _freeze_string_source,
                contents_matches(after_freeze),
            ),
        ),
    ])


def pre_post_freeze__identical(expectation: ValueAssertion[StringSourceContents],
                               ) -> ValueAssertion[StringSource]:
    return pre_post_freeze(expectation, expectation)


def pre_post_freeze__matches_lines(lines: ValueAssertion[Sequence[str]],
                                   may_depend_on_external_resources: ValueAssertion[bool],
                                   frozen_may_depend_on_external_resources: ValueAssertion[bool],
                                   ) -> ValueAssertion[StringSource]:
    return pre_post_freeze(
        asrt_str_src_contents.matches__lines(lines, may_depend_on_external_resources),
        asrt_str_src_contents.matches__lines(lines, frozen_may_depend_on_external_resources),
    )


def pre_post_freeze__matches_lines__any_frozen_ext_deps(lines: ValueAssertion[Sequence[str]],
                                                        may_depend_on_external_resources: ValueAssertion[bool],
                                                        ) -> ValueAssertion[StringSource]:
    return pre_post_freeze__matches_lines(
        lines,
        may_depend_on_external_resources,
        frozen_may_depend_on_external_resources=asrt.anything_goes(),
    )


def pre_post_freeze__matches_lines__identical(lines: ValueAssertion[Sequence[str]],
                                              may_depend_on_external_resources: ValueAssertion[bool],
                                              ) -> ValueAssertion[StringSource]:
    return pre_post_freeze__identical(
        asrt_str_src_contents.matches__lines(lines, may_depend_on_external_resources)
    )


def pre_post_freeze__matches_str(contents: ValueAssertion[str],
                                 may_depend_on_external_resources: ValueAssertion[bool],
                                 frozen_may_depend_on_external_resources: ValueAssertion[bool],
                                 ) -> ValueAssertion[StringSource]:
    return pre_post_freeze(
        asrt_str_src_contents.matches__str(contents, may_depend_on_external_resources),
        asrt_str_src_contents.matches__str(contents, frozen_may_depend_on_external_resources),
    )


def pre_post_freeze__matches_str__const(contents: str,
                                        may_depend_on_external_resources: bool,
                                        ) -> ValueAssertion[StringSource]:
    return pre_post_freeze__matches_str(
        asrt.equals(contents),
        asrt.equals(may_depend_on_external_resources),
        asrt.equals(may_depend_on_external_resources),
    )


def pre_post_freeze__matches_str__const_2(contents: str,
                                          may_depend_on_external_resources: bool,
                                          frozen_may_depend_on_external_resources: ValueAssertion[bool],
                                          ) -> ValueAssertion[StringSource]:
    return pre_post_freeze__matches_str(
        asrt.equals(contents),
        asrt.equals(may_depend_on_external_resources),
        asrt.is_instance_with(bool, frozen_may_depend_on_external_resources),
    )


def _freeze_string_source(x: StringSource):
    x.freeze()
