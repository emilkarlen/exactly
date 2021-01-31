import unittest
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import List, ContextManager, Sequence

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.type_val_prims.string_source.contents import StringSourceContents
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.common.test_resources import text_doc_assertions as asrt_text_doc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion, MessageBuilder
from exactly_lib_test.type_val_prims.string_source.test_resources import assertions as asrt_string_source
from exactly_lib_test.type_val_prims.string_source.test_resources import contents_assertions as asrt_str_src_contents
from exactly_lib_test.type_val_prims.string_source.test_resources import properties_access
from exactly_lib_test.type_val_prims.string_source.test_resources.contents_assertions import Expectation
from exactly_lib_test.type_val_prims.string_source.test_resources.properties_access import ContentsAsStrGetter
from exactly_lib_test.util.description_tree.test_resources import rendering_assertions as asrt_trace_rendering


class SourceConstructor(ABC):
    @abstractmethod
    def new(self, put: unittest.TestCase, message_builder: MessageBuilder) -> ContextManager[StringSource]:
        pass


class SourceConstructors:
    """One SourceConstructor used for checking without freeze,
    and one after freezing.

    The two constructors should construct identical objects,
    except for possibly their "environment".
    This difference in "environment" can be used to test
    properties that are unique for each case.
    E.g. for executing programs - the model for freeze case
    can use a :class:`CommandExecutor` that must be used at most 1 time.
    """

    def __init__(self,
                 for_check_without_freeze: SourceConstructor,
                 for_check_after_freeze: SourceConstructor,
                 ):
        self.for_check_without_freeze = for_check_without_freeze
        self.for_check_after_freeze = for_check_after_freeze

    @staticmethod
    def of_common(source_constructor: SourceConstructor) -> 'SourceConstructors':
        return SourceConstructors(source_constructor, source_constructor)


class ExpectationOnUnFrozenAndFrozen:
    def __init__(self,
                 un_frozen: Expectation,
                 frozen_may_depend_on_external_resources: Assertion[StringSourceContents]
                 = asrt_str_src_contents.external_dependencies(asrt.is_instance(bool)),
                 structure: Assertion[NodeRenderer]
                 = asrt_trace_rendering.matches_node_renderer(),
                 ):
        self.structure = structure
        self.un_frozen = un_frozen
        self.frozen_may_depend_on_external_resources = frozen_may_depend_on_external_resources

    @staticmethod
    def equals(contents: str,
               may_depend_on_external_resources: Assertion[bool],
               frozen_may_depend_on_external_resources: Assertion[bool],
               structure: Assertion[NodeRenderer]
               = asrt_trace_rendering.matches_node_renderer(),
               ) -> 'ExpectationOnUnFrozenAndFrozen':
        return ExpectationOnUnFrozenAndFrozen(
            Expectation.equals(contents, may_depend_on_external_resources),
            asrt_str_src_contents.external_dependencies(frozen_may_depend_on_external_resources),
            structure,
        )

    @staticmethod
    def hard_error(expected: Assertion[TextRenderer] = asrt_text_doc.is_any_text(),
                   may_depend_on_external_resources: Assertion[StringSourceContents]
                   = asrt_str_src_contents.external_dependencies(asrt.is_instance(bool)),
                   structure: Assertion[NodeRenderer]
                   = asrt_trace_rendering.matches_node_renderer(),
                   ) -> 'ExpectationOnUnFrozenAndFrozen':
        return ExpectationOnUnFrozenAndFrozen(
            Expectation.hard_error(expected, may_depend_on_external_resources),
            asrt.anything_goes(),
            structure,
        )

    @property
    def frozen(self) -> Expectation:
        return Expectation(self.un_frozen.contents,
                           self.frozen_may_depend_on_external_resources,
                           self.un_frozen.hard_error)


def assertion_of_sequence_permutations(expectation: ExpectationOnUnFrozenAndFrozen,
                                       ) -> Assertion[SourceConstructors]:
    return _SourceAssertionOnUnFrozenAndFrozen(
        expectation,
        properties_access.contents_cases__all_permutations(),
    )


def assertion_of_first_access_is_not_write_to(expectation: ExpectationOnUnFrozenAndFrozen,
                                              ) -> Assertion[SourceConstructors]:
    return _SourceAssertionOnUnFrozenAndFrozen(
        expectation,
        properties_access.contents_cases__first_access_is_not_write_to(),
    )


def assertion_of_2_seq_w_file_first_and_last(expectation: ExpectationOnUnFrozenAndFrozen,
                                             ) -> Assertion[SourceConstructors]:
    return _SourceAssertionOnUnFrozenAndFrozen(
        expectation,
        properties_access.contents_cases__2_seq_w_file_first_and_last(),
    )


class _SourceWithContentsVariantsAssertion(asrt.AssertionBase[SourceConstructor], ABC):
    def __init__(self,
                 expectation: Expectation,
                 contents_access_sequence_cases: Sequence[NameAndValue[List[NameAndValue[ContentsAsStrGetter]]]],
                 structure: Assertion[NodeRenderer]
                 = asrt_trace_rendering.matches_node_renderer(),
                 ):
        self.structure = structure
        self._expectation = expectation
        self._contents_access_sequence_cases = contents_access_sequence_cases

    def _apply(self,
               put: unittest.TestCase,
               value: SourceConstructor,
               message_builder: MessageBuilder,
               ):
        self._non_contents_related(put, value, message_builder.for_sub_component('non-contents-related'))
        self._contents_related(put, value, message_builder.for_sub_component('contents-related'))

    def _non_contents_related(self,
                              put: unittest.TestCase,
                              constructor: SourceConstructor,
                              message_builder: MessageBuilder,
                              ):
        with constructor.new(put, message_builder) as string_source:
            asrt_string_source.has_structure_description(self.structure).apply(put, string_source, message_builder)

    def _contents_related(self,
                          put: unittest.TestCase,
                          constructor: SourceConstructor,
                          message_builder: MessageBuilder,
                          ):
        for contents_access_sequence_case in self._contents_access_sequence_cases:
            case_message_builder = message_builder.for_sub_component(contents_access_sequence_case.name)
            ext_dep_case_message_builder = case_message_builder.for_sub_component('may-dep-on-ext-rsrc-first')
            with constructor.new(put, ext_dep_case_message_builder) as string_source:
                self._contents_related__ext_deps_first(
                    put,
                    contents_access_sequence_case.value,
                    string_source.contents(),
                    ext_dep_case_message_builder,
                )
            ext_dep_case_message_builder = case_message_builder.for_sub_component('may-dep-on-ext-rsrc-last')
            with constructor.new(put, ext_dep_case_message_builder) as string_source:
                self._contents_related__ext_deps_last(
                    put,
                    contents_access_sequence_case.value,
                    string_source.contents(),
                    ext_dep_case_message_builder,
                )

    def _contents_related__ext_deps_first(self,
                                          put: unittest.TestCase,
                                          contents_assertions: List[NameAndValue[ContentsAsStrGetter]],
                                          contents: StringSourceContents,
                                          message_builder: MessageBuilder,
                                          ):
        try:
            self._expectation.may_depend_on_external_resources.apply(
                put,
                contents,
                message_builder,
            )
            asrt_str_src_contents.ActualContentsVariantsSequenceAssertion(
                self._expectation,
                contents_assertions,
            ).apply(
                put,
                contents,
                message_builder,
            )
        except asrt.StopAssertion:
            pass

    def _contents_related__ext_deps_last(self,
                                         put: unittest.TestCase,
                                         contents_assertions: List[NameAndValue[ContentsAsStrGetter]],
                                         contents: StringSourceContents,
                                         message_builder: MessageBuilder,
                                         ):
        try:
            asrt_str_src_contents.ActualContentsVariantsSequenceAssertion(
                self._expectation,
                contents_assertions,
            ).apply(
                put,
                contents,
                message_builder,
            )
            self._expectation.may_depend_on_external_resources.apply(
                put,
                contents,
                message_builder,
            )
        except asrt.StopAssertion:
            pass


class _SourceAssertionOnUnFrozenAndFrozen(asrt.AssertionBase[SourceConstructors]):
    def __init__(self,
                 expectation: ExpectationOnUnFrozenAndFrozen,
                 contents_cases_: Sequence[NameAndValue[List[NameAndValue[ContentsAsStrGetter]]]],
                 ):
        self._expectation = expectation
        self._contents_cases = contents_cases_

    def _apply(self,
               put: unittest.TestCase,
               value: SourceConstructors,
               message_builder: MessageBuilder,
               ):
        self._un_frozen(put, value.for_check_without_freeze, message_builder)
        self._frozen(put, value.for_check_after_freeze, message_builder)

    def _un_frozen(self,
                   put: unittest.TestCase,
                   source_constructor: SourceConstructor,
                   message_builder: MessageBuilder,
                   ):
        assertion = _SourceWithContentsVariantsAssertion(self._expectation.un_frozen,
                                                         self._contents_cases,
                                                         self._expectation.structure)
        assertion.apply(put, source_constructor, message_builder.for_sub_component('un-frozen'))

    def _frozen(self,
                put: unittest.TestCase,
                source_constructor: SourceConstructor,
                message_builder: MessageBuilder,
                ):
        assertion = _SourceWithContentsVariantsAssertion(self._expectation.frozen,
                                                         self._contents_cases,
                                                         self._expectation.structure)
        for num_freeze in range(1, 3):
            constructor_that_freezes = _SourceConstructorThatFreezes(message_builder, num_freeze,
                                                                     source_constructor)
            assertion.apply(put,
                            constructor_that_freezes,
                            message_builder.for_sub_component('frozen ({} times)'.format(num_freeze)))


class _SourceConstructorThatFreezes(SourceConstructor):
    def __init__(self,
                 message_builder: MessageBuilder,
                 num_times_to_freeze: int,
                 unfrozen: SourceConstructor,
                 ):
        self._message_builder = message_builder
        self._num_times_to_freeze = num_times_to_freeze
        self._unfrozen = unfrozen

    @contextmanager
    def new(self, put: unittest.TestCase, message_builder: MessageBuilder) -> ContextManager[StringSource]:
        with self._unfrozen.new(put, message_builder) as to_freeze:
            for _ in range(self._num_times_to_freeze):
                self._do_freeze(put, to_freeze)
            yield to_freeze

    def _do_freeze(self, put: unittest.TestCase, source: StringSource):
        try:
            source.freeze()
        except HardErrorException as ex:
            put.fail(
                self._message_builder.for_sub_component('freeze').apply('freeze raised HardErrorException: ' + str(ex))
            )
