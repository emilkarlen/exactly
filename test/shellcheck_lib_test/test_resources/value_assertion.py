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


class ValueAssertion:
    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        raise NotImplementedError()


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
                 assertion_name: str = 'none of the assertions was satisfied'):
        self.assertions = assertions
        self.assertion_name = assertion_name

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: MessageBuilder = MessageBuilder()):
        for assertion in self.assertions:
            assert isinstance(assertion, ValueAssertion)
            try:
                assertion.apply(put, value, message_builder)
                return
            except put.failureException:
                pass
        put.fail(message_builder.apply('OR: ' + self.assertion_name))


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
        put.assertEquals(self.expected,
                         value,
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


def fail(msg: str) -> ValueAssertion:
    return Constant(False, msg)
