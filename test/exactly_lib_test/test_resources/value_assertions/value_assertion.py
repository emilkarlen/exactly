import os
import types
import unittest


class MessageBuilder:
    def __init__(self,
                 head: str = ''):
        self.head = head

    def apply(self, tail: str) -> str:
        msg_head = self.head
        if msg_head:
            if tail:
                return msg_head + ': ' + tail
            else:
                return msg_head
        else:
            return '' if tail is None else tail

    def for_sub_component(self, component_name: str,
                          component_separator: str = '/'):
        return sub_component_builder(component_name,
                                     self,
                                     component_separator)


class ValueAssertion:
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        raise NotImplementedError()

    def apply_with_message(self, put: unittest.TestCase, value, message: str):
        """
        Short cut to 'apply' when using a str message.
        """
        return self.apply(put, value, MessageBuilder(message))

    def apply_without_message(self, put: unittest.TestCase, value):
        """
        Short cut to 'apply' when using no message.
        """
        return self.apply(put, value, MessageBuilder())


class OfCallable(ValueAssertion):
    def __init__(self,
                 f: types.FunctionType):
        self.f = f

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        self.f(put, value, message_builder)


class Constant(ValueAssertion):
    """
    An assertion that passes or fails constantly.
    """

    def __init__(self,
                 result: bool,
                 message: str = ''):
        self.result = result
        self._message = 'Constant ' + str(result) if not message else message

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        if not self.result:
            put.fail(message_builder.apply(self._message))


class Boolean(ValueAssertion):
    """
    Tests a boolean
    """

    def __init__(self,
                 expected: bool,
                 message: str = ''):
        self.expected = expected
        self.message = message

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        msg = message_builder.apply(self.message)
        if self.expected:
            put.assertTrue(value, msg)
        else:
            put.assertFalse(value, msg)


class IsInstance(ValueAssertion):
    """
    Tests a boolean
    """

    def __init__(self,
                 expected: type,
                 message: str = ''):
        self.expected = expected
        self.message = message

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertIsInstance(value,
                             self.expected,
                             message_builder.apply(self.message))


def optional(present_value: ValueAssertion) -> ValueAssertion:
    return Or([ValueIsNone(),
               present_value])


def anything_goes() -> ValueAssertion:
    return Constant(True)


class And(ValueAssertion):
    def __init__(self,
                 assertions: list):
        self.assertions = assertions

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        for assertion in self.assertions:
            assert isinstance(assertion, ValueAssertion)
            assertion.apply(put, value, message_builder)


class Or(ValueAssertion):
    def __init__(self,
                 assertions: list,
                 assertion_name: str = 'none of the assertions were satisfied'):
        self.assertions = assertions
        self.assertion_name = assertion_name

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        failures = []
        for assertion in self.assertions:
            assert isinstance(assertion, ValueAssertion)
            try:
                assertion.apply(put, value, message_builder)
                return
            except put.failureException as ex:
                failures.append('  ' + str(ex))
        put.fail(message_builder.apply('OR: ' + self.assertion_name) + ':' + os.linesep +
                 os.linesep.join(failures))


class Not(ValueAssertion):
    def __init__(self,
                 assertion: ValueAssertion,
                 assertion_name: str = ''):
        self.assertion = assertion
        self.assertion_name = assertion_name

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        try:
            self.assertion.apply(put, value, message_builder)
        except put.failureException:
            pass
        else:
            put.fail(message_builder.apply('NOT ' + self.assertion_name))


class Is(ValueAssertion):
    def __init__(self,
                 expected,
                 message: str = None):
        self.expected = expected
        self.message = message

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertIs(self.expected, value,
                     message_builder.apply(self.message))


class ValueIsNone(ValueAssertion):
    def __init__(self,
                 message: str = None):
        self.message = message

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertIsNone(value,
                         message_builder.apply(self.message))


class ValueIsNotNone(ValueAssertion):
    def __init__(self,
                 message: str = None):
        self.message = message

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertIsNotNone(value,
                            message_builder.apply(self.message))


class Equals(ValueAssertion):
    def __init__(self,
                 expected,
                 message: str = None):
        self.expected = expected
        self.message = message

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertEqual(self.expected,
                        value,
                        message_builder.apply(self.message))


class _LenEquals(ValueAssertion):
    def __init__(self,
                 expected: int,
                 message: str = None):
        self.expected = expected
        self.message = message

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertEqual(self.expected,
                        len(value),
                        message_builder.apply(self.message))


class OnTransformed(ValueAssertion):
    def __init__(self,
                 transformer: types.FunctionType,
                 assertion: ValueAssertion):
        self.transformer = transformer
        self.assertion = assertion

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        self.assertion.apply(put,
                             self.transformer(value),
                             message_builder)


def sub_component(component_name: str,
                  component_getter: types.FunctionType,
                  component_assertion: ValueAssertion,
                  component_separator: str = '/') -> ValueAssertion:
    """
    Short cut for creating a SubComponentValueAssertion
    """
    return SubComponent(SubComponentMessageHeadConstructor(component_name,
                                                           component_separator),
                        component_getter,
                        component_assertion)


def with_transformed_message(message_builder_transformer: types.FunctionType,
                             value_assertion: ValueAssertion) -> ValueAssertion:
    return _WithTransformedMessage(message_builder_transformer, value_assertion)


def append_to_message(s: str) -> types.FunctionType:
    def ret_val(message_builder: MessageBuilder) -> MessageBuilder:
        return message_builder.for_sub_component(s, component_separator='')

    return ret_val


def sub_component_list(list_name: str,
                       list_getter: types.FunctionType,
                       element_assertion: ValueAssertion,
                       component_separator: str = '/') -> ValueAssertion:
    """
    Short cut for creating a SubComponentValueAssertion that checks a list
    """
    return sub_component(list_name,
                         list_getter,
                         every_element('',
                                       element_assertion),
                         component_separator)


def is_list_of(element_assertion: ValueAssertion) -> ValueAssertion:
    return is_instance_with(list,
                            every_element('', element_assertion, component_separator=''))


class _IsInstanceWith(ValueAssertion):
    def __init__(self,
                 expected_type: type,
                 value_assertion: ValueAssertion):
        self.expected_type = expected_type
        self.value_assertion = value_assertion

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertIsInstance(value,
                             self.expected_type,
                             message_builder.apply(''))
        self.value_assertion.apply(put, value, message_builder)


class _IsNotNoneAndInstanceWith(ValueAssertion):
    def __init__(self,
                 expected_type: type,
                 value_assertion: ValueAssertion):
        self.expected_type = expected_type
        self.value_assertion = value_assertion

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        msg = message_builder.apply('')
        put.assertIsNotNone(value, msg)
        put.assertIsInstance(value, self.expected_type, msg)
        self.value_assertion.apply(put, value, message_builder)


def is_instance_with(expected_type: type,
                     value_assertion: ValueAssertion) -> ValueAssertion:
    return _IsInstanceWith(expected_type, value_assertion)


def is_not_none_and_instance_with(expected_type: type,
                                  value_assertion: ValueAssertion) -> ValueAssertion:
    return _IsNotNoneAndInstanceWith(expected_type, value_assertion)


def every_element(iterable_name: str,
                  element_assertion: ValueAssertion,
                  component_separator: str = '/') -> ValueAssertion:
    """
    Short cut for creating a IterableElementsValueAssertion
    """
    return EveryElement(SubComponentMessageHeadConstructor(iterable_name,
                                                           component_separator),
                        element_assertion)


class SubComponentMessageHeadConstructor:
    def __init__(self,
                 component_name: str,
                 component_separator: str = '/'):
        self.component_name = component_name
        self.component_separator = component_separator

    def apply(self, super_message_builder: MessageBuilder) -> str:
        head = self.component_name
        if super_message_builder.head:
            head = super_message_builder.head + self.component_separator + self.component_name
        return head


def sub_component_header(component_name: str,
                         super_message_builder: MessageBuilder,
                         component_separator: str = '/') -> str:
    con = SubComponentMessageHeadConstructor(component_name, component_separator=component_separator)
    return con.apply(super_message_builder)


def sub_component_builder(component_name: str,
                          super_message_builder: MessageBuilder,
                          component_separator: str = '/') -> MessageBuilder:
    return MessageBuilder(sub_component_header(component_name, super_message_builder, component_separator))


class SubComponent(ValueAssertion):
    def __init__(self,
                 message_head_constructor: SubComponentMessageHeadConstructor,
                 component_getter: types.FunctionType,
                 component_assertion: ValueAssertion):
        self.component_getter = component_getter
        self.component_assertion = component_assertion
        self.message_head_constructor = message_head_constructor

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        sub_component_value = self.component_getter(value)
        component_message_builder = MessageBuilder(self.message_head_constructor.apply(message_builder))
        self.component_assertion.apply(put,
                                       sub_component_value,
                                       component_message_builder)


class EveryElement(ValueAssertion):
    def __init__(self,
                 message_head_constructor: SubComponentMessageHeadConstructor,
                 element_assertion: ValueAssertion):
        self.element_assertion = element_assertion
        self.message_head_constructor = message_head_constructor

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        head = self.message_head_constructor.apply(message_builder)
        element_index = 0
        for element in value:
            element_message_builder = MessageBuilder(head + '[' + str(element_index) + ']')
            self.element_assertion.apply(put,
                                         element,
                                         element_message_builder)
            element_index += 1


class _MatchesSequence(ValueAssertion):
    def __init__(self,
                 element_assertions: list):
        self.element_assertions = element_assertions

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        put.assertEqual(len(value),
                        len(self.element_assertions),
                        message_builder.apply('Number of elements'))
        for idx, element in enumerate(value):
            element_message_builder = sub_component_builder('[' + str(idx) + ']',
                                                            message_builder,
                                                            component_separator='')
            self.element_assertions[idx].apply(put, element,
                                               element_message_builder)


def fail(msg: str) -> ValueAssertion:
    return Constant(False, msg)


class _WithTransformedMessage(ValueAssertion):
    def __init__(self,
                 message_builder_transformer: types.FunctionType,
                 value_assertion: ValueAssertion):
        self.value_assertion = value_assertion
        self.message_builder_transformer = message_builder_transformer

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        self.value_assertion.apply(put,
                                   value,
                                   self.message_builder_transformer(message_builder))


is_instance = IsInstance
is_none = ValueIsNone()
is_not_none = ValueIsNotNone()
equals = Equals
len_equals = _LenEquals
on_transformed = OnTransformed

is_false = Equals(False)
is_true = Equals(True)


def is_boolean(expected: bool) -> ValueAssertion:
    return Boolean(expected)


is_empty = len_equals(0)
is_empty_list = is_instance_with(list, is_empty)

ignore = Constant(True)


def matches_sequence(element_assertions: list) -> ValueAssertion:
    """
    :param element_assertions: The element at index i is an assertion on element at index i
        in the list of acutal values.
    :type element_assertions: [`ValueAssertion`]
    """
    return _MatchesSequence(element_assertions)


def and_(assertions: list) -> ValueAssertion:
    if not assertions:
        return Constant(True)
    if len(assertions) == 1:
        return assertions[0]
    return And(assertions)


def or_(assertions: list) -> ValueAssertion:
    if not assertions:
        return Constant(False)
    if len(assertions) == 1:
        return assertions[0]
    return Or(assertions)
