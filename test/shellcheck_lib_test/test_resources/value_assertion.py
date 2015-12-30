import unittest


class ValueAssertion:
    def apply(self,
              put: unittest.TestCase,
              value):
        raise NotImplementedError()


class AnythingGoes(ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value):
        pass


class And(ValueAssertion):
    def __init__(self,
                 assertions: list):
        self.assertions = assertions

    def apply(self,
              put: unittest.TestCase,
              value):
        for assertion in self.assertions:
            assert isinstance(assertion, ValueAssertion)
            assertion.apply(put, value)


class ValueIsNone(ValueAssertion):
    def __init__(self,
                 message: str = None):
        self.message = message

    def apply(self,
              put: unittest.TestCase,
              value):
        put.assertIsNone(value,
                         self.message)


class ValueIsNotNone(ValueAssertion):
    def __init__(self,
                 message: str = None):
        self.message = message

    def apply(self,
              put: unittest.TestCase,
              value):
        put.assertIsNotNone(value,
                            self.message)
