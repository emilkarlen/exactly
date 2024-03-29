import os
import unittest
from typing import TypeVar, Sequence, Callable, Any, Generic, Type, Sized, List, Set, Optional, Mapping

from exactly_lib.util.name_and_value import NameAndValue

COMPONENT_SEPARATOR = '/'

T = TypeVar('T')
U = TypeVar('U')

TYPE_WITH_EQUALS = TypeVar('TYPE_WITH_EQUALS')


class MessageBuilder:
    def __init__(self,
                 head: str = ''):
        self.head = head

    @staticmethod
    def new_empty() -> 'MessageBuilder':
        return MessageBuilder('')

    @staticmethod
    def new(message_header_or_none: str = None) -> 'MessageBuilder':
        return MessageBuilder('' if message_header_or_none is None else message_header_or_none)

    def apply(self, tail: str) -> str:
        msg_head = self.head
        if msg_head:
            if tail:
                return msg_head + ': ' + tail
            else:
                return msg_head
        else:
            return '' if tail is None else tail

    def msg_for_sub_component(self, component_name: str) -> str:
        return self.apply(COMPONENT_SEPARATOR + component_name)

    def for_sub_component(self, component_name: str,
                          component_separator: str = COMPONENT_SEPARATOR) -> 'MessageBuilder':
        return sub_component_builder(component_name,
                                     self,
                                     component_separator)

    def with_description(self, description: str) -> 'MessageBuilder':
        """
        Adds a description
        :param description: If empty on None, no description is added
        """
        if description:
            return sub_component_builder(' (' + description + ') ',
                                         self,
                                         '')
        else:
            return self


def new_message_builder(message_header_or_none: str = None) -> MessageBuilder:
    return MessageBuilder('' if message_header_or_none is None else message_header_or_none)


class StopAssertion(Exception):
    """Raised by assertions to signal that no more assertions should be applied."""
    pass


class Assertion(Generic[T]):
    def apply(self,
              put: unittest.TestCase,
              value: T,
              message_builder: MessageBuilder = MessageBuilder()):
        raise NotImplementedError('abstract method')

    def apply_with_message(self, put: unittest.TestCase, value: T, message: str):
        """
        Short cut to 'apply' when using a str message.
        """
        return self.apply(put, value, MessageBuilder(message))

    def apply_without_message(self, put: unittest.TestCase, value: T):
        """
        Short cut to 'apply' when using no message.
        """
        return self.apply(put, value, MessageBuilder())


class AssertionBase(Assertion[T]):
    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        raise NotImplementedError('abstract method')

    def apply(self,
              put: unittest.TestCase,
              value: T,
              message_builder: MessageBuilder = MessageBuilder()):
        self._apply(put, value, message_builder)


class OfCallable(AssertionBase[T]):
    def __init__(self, f: Callable[[unittest.TestCase, T, MessageBuilder], None]):
        self.f = f

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        self.f(put, value, message_builder)


class Constant(AssertionBase[Any]):
    """
    An assertion that passes or fails constantly.
    """

    def __init__(self,
                 result: bool,
                 message: str = ''):
        self.result = result
        self._message = 'Constant ' + str(result) if not message else message

    def _apply(self,
               put: unittest.TestCase,
               value: Any,
               message_builder: MessageBuilder):
        if not self.result:
            put.fail(message_builder.apply(self._message))


class Boolean(AssertionBase[T]):
    """
    Tests an expression casted to a boolean
    """

    def __init__(self,
                 expected: bool,
                 message: str = ''):
        self.expected = expected
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder = MessageBuilder()):
        msg = message_builder.apply(self.message)
        if self.expected:
            put.assertTrue(value, msg)
        else:
            put.assertFalse(value, msg)


class IsInstance(AssertionBase[Any]):
    """
    Tests a boolean
    """

    def __init__(self,
                 expected: Type,
                 message: str = ''):
        self.expected = expected
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: Any,
               message_builder: MessageBuilder):
        put.assertIsInstance(value,
                             self.expected,
                             message_builder.apply(self.message))


def optional(present_value: Assertion[T]) -> Assertion[T]:
    return Or([ValueIsNone(),
               present_value])


def anything_goes() -> Assertion[Any]:
    return _CONST_TRUE


_CONST_TRUE = Constant(True)


class And(AssertionBase[T]):
    def __init__(self,
                 assertions: Sequence[Assertion[T]]):
        self.assertions = assertions

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        for assertion in self.assertions:
            assert isinstance(assertion, Assertion)
            try:
                assertion.apply(put, value, message_builder)
            except StopAssertion:
                return


class Or(AssertionBase[T]):
    def __init__(self,
                 assertions: Sequence[Assertion[T]],
                 assertion_name: str = 'none of the assertions were satisfied'):
        self.assertions = assertions
        self.assertion_name = assertion_name

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        failures = []
        for assertion in self.assertions:
            assert isinstance(assertion, Assertion)
            try:
                try:
                    assertion.apply(put, value, message_builder)
                    return
                except StopAssertion:
                    return
            except put.failureException as ex:
                failures.append('  ' + str(ex))
        put.fail(message_builder.apply('OR: ' + self.assertion_name) + ':' + os.linesep +
                 os.linesep.join(failures))


class Not(AssertionBase[T]):
    def __init__(self,
                 assertion: Assertion[T],
                 assertion_name: str = ''):
        self.assertion = assertion
        self.assertion_name = assertion_name

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        try:
            self.assertion.apply(put, value, message_builder)
        except put.failureException:
            pass
        else:
            put.fail(message_builder.apply('NOT ' + self.assertion_name))


class Is(AssertionBase[T]):
    def __init__(self,
                 expected: T,
                 message: str = None):
        self.expected = expected
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        put.assertIs(self.expected, value,
                     message_builder.apply(self.message))


class IsAny(AssertionBase[Any]):
    def __init__(self,
                 expected: T,
                 message: str = None):
        self.expected = expected
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        put.assertIs(self.expected, value,
                     message_builder.apply(self.message))


class IsNot(AssertionBase[T]):
    def __init__(self,
                 expected: T,
                 message: str = None):
        self.expected = expected
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        put.assertIsNot(self.expected, value,
                        message_builder.apply(self.message))


class ValueIsNone(AssertionBase[T]):
    def __init__(self,
                 message: str = None):
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        put.assertIsNone(value,
                         message_builder.apply(self.message))


class ValueIsNotNone(AssertionBase[T]):
    def __init__(self,
                 message: str = None):
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        put.assertIsNotNone(value,
                            message_builder.apply(self.message))


class ValueIsNotNoneAnd(Generic[T], AssertionBase[Optional[T]]):
    def __init__(self,
                 present_value: Assertion[T]
                 ):
        self.present_value = present_value

    def _apply(self,
               put: unittest.TestCase,
               value: Optional[T],
               message_builder: MessageBuilder):
        put.assertIsNotNone(value,
                            message_builder.apply(''))
        assert value is not None
        self.present_value.apply(put, value, message_builder)


class Equals(AssertionBase[T]):
    def __init__(self,
                 expected: Any,
                 message: str = None):
        self.expected = expected
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        put.assertEqual(self.expected,
                        value,
                        message_builder.apply(self.message))


class GreaterThan(AssertionBase[T]):
    def __init__(self,
                 limit: T,
                 message: str = None,
                 ):
        self.limit = limit
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        put.assertGreater(value, self.limit,
                          message_builder.apply(self.message))


class Length(AssertionBase[Sized]):
    def __init__(self, expected: Assertion[int]):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value: Sized,
               message_builder: MessageBuilder):
        self.expected.apply(put, len(value),
                            message_builder.for_sub_component('length'))


class _LenEquals(AssertionBase[Sized]):
    def __init__(self,
                 expected: int,
                 message: str = None):
        self.expected = expected
        self.message = message

    def _apply(self,
               put: unittest.TestCase,
               value: Sized,
               message_builder: MessageBuilder):
        put.assertEqual(self.expected,
                        len(value),
                        message_builder.for_sub_component('length').apply(self.message))


class OnTransformed(AssertionBase[T]):
    def __init__(self,
                 transformer: Callable[[T], U],
                 assertion: Assertion[U],
                 transformer_name: Optional[str] = None,
                 ):
        self.transformer = transformer
        self.assertion = assertion
        self.transformer_name = transformer_name

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        if self.transformer_name is not None:
            message_builder = message_builder.for_sub_component(self.transformer_name)

        self.assertion.apply(put,
                             self.transformer(value),
                             message_builder)


class AfterManipulation(AssertionBase[T]):
    def __init__(self,
                 manipulator: Callable[[T], Any],
                 assertion: Assertion[U],
                 ):
        self.manipulator = manipulator
        self.assertion = assertion

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        self.manipulator(value)
        self.assertion.apply(put,
                             value,
                             message_builder)


def if_(condition: Callable[[T], bool],
        assertion: Assertion[T]) -> Assertion[T]:
    return _IfAssertion(condition, assertion)


def sub_component(component_name: str,
                  component_getter: Callable[[T], U],
                  component_assertion: Assertion[U],
                  component_separator: str = COMPONENT_SEPARATOR) -> Assertion[T]:
    """
    Short cut for creating a SubComponentValueAssertion
    """
    return SubComponent(SubComponentMessageHeadConstructor(component_name,
                                                           component_separator),
                        component_getter,
                        component_assertion)


def elem_at_index(element_name: str,
                  element_index: int,
                  element_assertion: Assertion[U],
                  element_separator: str = COMPONENT_SEPARATOR) -> Assertion[T]:
    """
    Short cut for creating a SubComponentValueAssertion
    """
    return sub_component(
        element_name,
        lambda x: x[element_index],
        element_assertion,
        element_separator,
    )


def sequence_elem_at_index(element_index: int,
                           element_assertion: Assertion[U]) -> Assertion[T]:
    """
    Short cut for creating a SubComponentValueAssertion
    """
    return sub_component(
        _element_at_index(element_index),
        lambda x: x[element_index],
        element_assertion,
        '',
    )


def named(name: str,
          assertion: Assertion[T]) -> Assertion[T]:
    return sub_component(name,
                         lambda x: x,
                         assertion)


def after_manipulation(manipulator: Callable[[T], Any],
                       assertion: Assertion[T],
                       name: str = '',
                       ) -> Assertion[T]:
    after_manipulation = AfterManipulation(manipulator, assertion)
    return (
        named(name, after_manipulation)
        if name
        else
        after_manipulation
    )


def sub_component_many(component_name: str,
                       component_getter: Callable[[T], U],
                       component_assertions: List[Assertion[U]],
                       component_separator: str = COMPONENT_SEPARATOR) -> Assertion[T]:
    return sub_component(component_name,
                         component_getter,
                         and_(component_assertions),
                         component_separator)


def with_transformed_message(message_builder_transformer: Callable[[MessageBuilder], MessageBuilder],
                             value_assertion: Assertion[T]) -> Assertion[T]:
    return _WithTransformedMessage(message_builder_transformer, value_assertion)


def with_sub_component_message(component_name: str,
                               value_assertion: Assertion[T]) -> Assertion[T]:
    return _WithTransformedMessage(lambda mb: mb.for_sub_component(component_name),
                                   value_assertion)


def append_to_message(s: str) -> Callable[[MessageBuilder], MessageBuilder]:
    def ret_val(message_builder: MessageBuilder) -> MessageBuilder:
        return message_builder.for_sub_component(s, component_separator='')

    return ret_val


def sub_component_sequence(sequence_name: str,
                           sequence_getter: Callable[[T], Sequence[U]],
                           element_assertion: Assertion[U],
                           component_separator: str = COMPONENT_SEPARATOR) -> Assertion[T]:
    """
    Short cut for creating a SubComponentValueAssertion that checks a list
    """
    return sub_component(sequence_name,
                         sequence_getter,
                         every_element('',
                                       element_assertion),
                         component_separator)


def is_list_of(element_assertion: Assertion[T]) -> Assertion[List[T]]:
    return is_instance_with(list,
                            every_element('', element_assertion, component_separator=''))


def is_sequence_of(element_assertion: Assertion[T]) -> Assertion[Sequence[T]]:
    return is_instance_with(Sequence,
                            every_element('', element_assertion, component_separator=''))


def is_set_of(element_assertion: Assertion[T]) -> Assertion[Set[T]]:
    return is_instance_with(Set,
                            every_element('', element_assertion, component_separator=''))


class _IsInstanceWith(Generic[T], AssertionBase[Any]):
    def __init__(self,
                 expected_type: Type[T],
                 value_assertion: Assertion[T],
                 description: str):
        self.expected_type = expected_type
        self.value_assertion = value_assertion
        self.description = description

    def _apply(self,
               put: unittest.TestCase,
               value: Any,
               message_builder: MessageBuilder):
        if self.description:
            message_builder = message_builder.with_description(self.description)
        put.assertIsInstance(value,
                             self.expected_type,
                             message_builder.msg_for_sub_component('type'))
        self.value_assertion.apply(put, value, message_builder)


class _IsOptionalInstanceWith(Generic[T], AssertionBase[Any]):
    def __init__(self,
                 expected_type: Type[T],
                 value_assertion: Assertion[Optional[T]],
                 description: str):
        self.expected_type = expected_type
        self.value_assertion = value_assertion
        self.description = description

    def _apply(self,
               put: unittest.TestCase,
               value: Any,
               message_builder: MessageBuilder):
        if self.description:
            message_builder = message_builder.with_description(self.description)
        if value is not None:
            put.assertIsInstance(value,
                                 self.expected_type,
                                 message_builder.msg_for_sub_component('type'))
        self.value_assertion.apply(put, value, message_builder)


class _IsNotNoneAndInstanceWith(Generic[T], AssertionBase[Any]):
    def __init__(self,
                 expected_type: Type[T],
                 value_assertion: Assertion[T]):
        self.expected_type = expected_type
        self.value_assertion = value_assertion

    def _apply(self,
               put: unittest.TestCase,
               value: Any,
               message_builder: MessageBuilder):
        msg = message_builder.apply('')
        put.assertIsNotNone(value, msg)
        put.assertIsInstance(value, self.expected_type, msg)
        self.value_assertion.apply(put, value, message_builder)


class _IsNoneOrInstanceWith(Generic[T], AssertionBase[Any]):
    def __init__(self,
                 expected_type: Type[T],
                 value_assertion: Assertion[T]):
        self.expected_type = expected_type
        self.value_assertion = value_assertion

    def _apply(self,
               put: unittest.TestCase,
               value: Any,
               message_builder: MessageBuilder):
        msg = message_builder.apply('')
        if value is None:
            return
        put.assertIsInstance(value, self.expected_type, msg)
        self.value_assertion.apply(put, value, message_builder)


def is_instance_with(expected_type: Type[T],
                     value_assertion: Assertion[T],
                     description: str = '') -> Assertion[Any]:
    return _IsInstanceWith(expected_type, value_assertion, description)


def is_optional_instance_with(expected_type: Type[T],
                              value_assertion: Assertion[Optional[T]],
                              description: str = '') -> Assertion[Optional[Any]]:
    return _IsOptionalInstanceWith(expected_type, value_assertion, description)


def is_instance_with__many(expected_type: Type[T],
                           value_assertions: List[Assertion[T]],
                           description: str = '') -> Assertion[Any]:
    return _IsInstanceWith(expected_type,
                           and_(value_assertions),
                           description)


def is_not_none_and_instance_with(expected_type: Type[T],
                                  value_assertion: Assertion[T]) -> Assertion[Any]:
    return _IsNotNoneAndInstanceWith(expected_type, value_assertion)


def is_none_or_instance_with(expected_type: Type[T],
                             value_assertion: Assertion[T]) -> Assertion[Any]:
    return _IsNoneOrInstanceWith(expected_type, value_assertion)


def is_none_or_instance(expected_type: Type[T]) -> Assertion[Any]:
    return _IsNoneOrInstanceWith(expected_type, anything_goes())


def is_none_or_instance_with__many(expected_type: Type[T],
                                   assertions: Sequence[Assertion[T]]) -> Assertion[Any]:
    return _IsNoneOrInstanceWith(expected_type, and_(assertions))


def every_element(iterable_name: str,
                  element_assertion: Assertion[T],
                  component_separator: str = COMPONENT_SEPARATOR) -> Assertion[Sequence[T]]:
    """
    Short cut for creating a IterableElementsValueAssertion
    """
    return EveryElement(SubComponentMessageHeadConstructor(iterable_name,
                                                           component_separator),
                        element_assertion)


class SubComponentMessageHeadConstructor:
    def __init__(self,
                 component_name: str,
                 component_separator: str = COMPONENT_SEPARATOR):
        self.component_name = component_name
        self.component_separator = component_separator

    def apply(self, super_message_builder: MessageBuilder) -> str:
        head = self.component_name
        if super_message_builder.head:
            head = super_message_builder.head + self.component_separator + self.component_name
        return head


def sub_component_header(component_name: str,
                         super_message_builder: MessageBuilder,
                         component_separator: str = COMPONENT_SEPARATOR) -> str:
    con = SubComponentMessageHeadConstructor(component_name, component_separator=component_separator)
    return con.apply(super_message_builder)


def sub_component_builder(component_name: str,
                          super_message_builder: MessageBuilder,
                          component_separator: str = COMPONENT_SEPARATOR) -> MessageBuilder:
    return MessageBuilder(sub_component_header(component_name, super_message_builder, component_separator))


def _element_at_index(i: int) -> str:
    return ''.join(('[', str(i), ']'))


class SubComponent(AssertionBase[T]):
    def __init__(self,
                 message_head_constructor: SubComponentMessageHeadConstructor,
                 component_getter: Callable[[T], U],
                 component_assertion: Assertion[U]):
        self.component_getter = component_getter
        self.component_assertion = component_assertion
        self.message_head_constructor = message_head_constructor

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        sub_component_value = self.component_getter(value)
        component_message_builder = MessageBuilder(self.message_head_constructor.apply(message_builder))
        self.component_assertion.apply(put,
                                       sub_component_value,
                                       component_message_builder)


class EveryElement(AssertionBase[Sequence[T]]):
    def __init__(self,
                 message_head_constructor: SubComponentMessageHeadConstructor,
                 element_assertion: Assertion[T]):
        self.element_assertion = element_assertion
        self.message_head_constructor = message_head_constructor

    def _apply(self,
               put: unittest.TestCase,
               value: Sequence[T],
               message_builder: MessageBuilder):
        head = self.message_head_constructor.apply(message_builder)
        element_index = 0
        for element in value:
            element_message_builder = MessageBuilder(head + _element_at_index(element_index))
            self.element_assertion.apply(put,
                                         element,
                                         element_message_builder)
            element_index += 1


class _MatchesSequence(AssertionBase[Sequence[T]]):
    def __init__(self,
                 element_assertions: Sequence[Assertion[T]],
                 get_name: Callable[[int], str] = _element_at_index,
                 ):
        self.element_assertions = element_assertions
        self._get_name = get_name

    def _apply(self,
               put: unittest.TestCase,
               value: Sequence[T],
               message_builder: MessageBuilder):
        put.assertEqual(len(value),
                        len(self.element_assertions),
                        message_builder.apply('Number of elements'))
        for idx, element in enumerate(value):
            element_message_builder = sub_component_builder(self._get_name(idx),
                                                            message_builder,
                                                            component_separator='')
            self.element_assertions[idx].apply(put, element,
                                               element_message_builder)


class _MatchesList(AssertionBase[List[T]]):
    def __init__(self, elements: Sequence[Assertion[T]]):
        self.elements = _MatchesSequence(elements)

    def _apply(self,
               put: unittest.TestCase,
               value: List[T],
               message_builder: MessageBuilder):
        put.assertIsInstance(value, list,
                             message_builder.apply('type'))
        self.elements.apply(put, value, message_builder)


class _IsSequenceWithElementAtPos(AssertionBase[Sequence[T]]):
    def __init__(self,
                 index: int,
                 element_assertion: Assertion[T]):
        self.index = index
        self.element_assertion = element_assertion

    def _apply(self,
               put: unittest.TestCase,
               value: Sequence[T],
               message_builder: MessageBuilder):
        put.assertGreater(len(value),
                          self.index,
                          message_builder.apply('number of elements'))
        idx = self.index
        element_message_builder = sub_component_builder(_element_at_index(idx),
                                                        message_builder,
                                                        component_separator='')
        self.element_assertion.apply(put,
                                     value[idx],
                                     element_message_builder)


class _EqualsSequence(AssertionBase[Sequence[T]]):
    def __init__(self,
                 expected: Sequence[T],
                 new_value_assertion_for_expected: Callable[[T], Assertion[T]]):
        self.expected = expected
        self.new_value_assertion_for_expected = new_value_assertion_for_expected

    def _apply(self,
               put: unittest.TestCase,
               value: Sequence[T],
               message_builder: MessageBuilder):
        put.assertEqual(len(value),
                        len(self.expected),
                        message_builder.apply('Number of elements'))
        for idx, element in enumerate(value):
            element_message_builder = sub_component_builder(_element_at_index(idx),
                                                            message_builder,
                                                            component_separator='')
            element_assertion = self.new_value_assertion_for_expected(self.expected[idx])
            assert isinstance(element_assertion, Assertion)
            element_assertion.apply(put, element,
                                    element_message_builder)


def fail(msg: str) -> Assertion[T]:
    return Constant(False, msg)


class _WithTransformedMessage(AssertionBase[T]):
    def __init__(self,
                 message_builder_transformer: Callable[[MessageBuilder], MessageBuilder],
                 value_assertion: Assertion[T]):
        self.value_assertion = value_assertion
        self.message_builder_transformer = message_builder_transformer

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        self.value_assertion.apply(put,
                                   value,
                                   self.message_builder_transformer(message_builder))


def equals_sequence(expected: Sequence[T],
                    new_value_assertion_for_expected: Callable[[T], Assertion[T]]) -> Assertion[Sequence[T]]:
    return _EqualsSequence(expected, new_value_assertion_for_expected)


is_instance = IsInstance
is_ = Is
is__any = IsAny
not_ = Not

is_none = ValueIsNone()
is_not_none = ValueIsNotNone()
equals = Equals
gt = GreaterThan
len_equals = _LenEquals
length = Length
on_transformed = OnTransformed


def on_transformed2(transformer: Callable[[T], U],
                    assertion: Assertion[U],
                    transformer_name: str) -> Assertion[T]:
    return OnTransformed(transformer,
                         assertion,
                         transformer_name)


is_false = Equals(False)
is_true = Equals(True)


def not__(assertion: Assertion[T]) -> Assertion[T]:
    return Not(assertion)


def casted_to_boolean_is(expected: bool) -> Assertion[T]:
    return Boolean(expected)


is_empty = len_equals(0)
is_empty_list = is_instance_with(list, is_empty)

is_empty_sequence = is_instance_with(Sequence, is_empty)

ignore = Constant(True)


def matches_sequence(element_assertions: Sequence[Assertion[T]]) -> Assertion[Sequence[T]]:
    """
    :param element_assertions: The element at index i is an assertion on element at index i
    in the list of actual values.
    """
    return _MatchesSequence(element_assertions)


def matches_sequence__named(element_assertions: Sequence[NameAndValue[Assertion[T]]],
                            ) -> Assertion[Sequence[T]]:
    """
    :param element_assertions: The element at index i is an assertion on element at index i
    in the list of actual values.
    """

    def get_name(idx: int) -> str:
        return ''.join(('[', str(idx), ':', element_assertions[idx].name, ']'))

    return _MatchesSequence([
        e.value
        for e in element_assertions
    ],
        get_name
    )


def matches_list(elements: Sequence[Assertion[T]]) -> Assertion[List[T]]:
    return _MatchesList(elements)


def matches_singleton_sequence(element: Assertion[T]) -> Assertion[Sequence[T]]:
    return matches_sequence([element])


def is_sequence_with_element_at_pos(index: int, element: Assertion[T]) -> Assertion[Sequence[T]]:
    return _IsSequenceWithElementAtPos(index, element)


def is_sub_class_with(expected_class: Type[T],
                      on_sub_class=Assertion[U]) -> Assertion[T]:
    return is_instance_with(expected_class, on_sub_class)


class _MatchesMapping(AssertionBase[Mapping[TYPE_WITH_EQUALS, T]]):
    def __init__(self, expected: Mapping[TYPE_WITH_EQUALS, Assertion[T]]):
        self.expected = expected

    def _apply(self,
               put: unittest.TestCase,
               value: Mapping[TYPE_WITH_EQUALS, T],
               message_builder: MessageBuilder):
        put.assertEqual(self.expected.keys(),
                        value.keys(),
                        'key set')
        for k in self.expected.keys():
            assertion = self.expected[k]
            actual = value[k]
            element_message_builder = sub_component_builder('[' + repr(k) + ']',
                                                            message_builder,
                                                            component_separator='')
            assertion.apply(put, actual, element_message_builder)


def matches_mapping(expected: Mapping[TYPE_WITH_EQUALS, Assertion[T]]
                    ) -> Assertion[Mapping[TYPE_WITH_EQUALS, T]]:
    """Assertion on a Mapping, with keys that can be compared using std Python equality"""
    return _MatchesMapping(expected)


def is_not(value) -> Assertion[T]:
    return IsNot(value)


def is_not_none_and(also: Assertion[T]) -> Assertion[Optional[T]]:
    return ValueIsNotNoneAnd(also)


def and_(assertions: Sequence[Assertion[T]]) -> Assertion[T]:
    if not assertions:
        return Constant(True)
    if len(assertions) == 1:
        return assertions[0]
    return And(assertions)


def or_(assertions: Sequence[Assertion[T]]) -> Assertion[T]:
    if not assertions:
        return Constant(False)
    if len(assertions) == 1:
        return assertions[0]
    return Or(assertions)


def all_named(assertions: Sequence[NameAndValue[Assertion[T]]]) -> Assertion[T]:
    return And([
        named(assertion.name,
              assertion.value)
        for assertion in assertions
    ])


class _IfAssertion(AssertionBase[T]):
    def __init__(self,
                 condition: Callable[[T], bool],
                 assertion: Assertion[T]
                 ):
        self.condition = condition
        self.assertion = assertion

    def _apply(self,
               put: unittest.TestCase,
               value: T,
               message_builder: MessageBuilder):
        if self.condition(value):
            self.assertion.apply(put, value, message_builder)
