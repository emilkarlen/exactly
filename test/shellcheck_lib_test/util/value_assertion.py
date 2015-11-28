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


class ValueIsNone(ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value):
        put.assertIsNone(value)


class ValueIsNotNone(ValueAssertion):
    def apply(self,
              put: unittest.TestCase,
              value):
        put.assertIsNotNone(value)
