import unittest

from exactly_lib_test.test_resources.value_assertions import value_assertion as sut


class TestException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class TestIsNone(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_none(self):
        sut.ValueIsNone().apply(self.put, None)
        sut.ValueIsNone().apply(self.put, None,
                                sut.MessageBuilder('head'))

    def test_not_none(self):
        with self.assertRaises(TestException):
            sut.ValueIsNone().apply(self.put, 'not none')
            sut.ValueIsNone().apply(self.put, 'not none',
                                    sut.MessageBuilder('head'))


class TestIsNotNone(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_none__sans_message_builder(self):
        with self.assertRaises(TestException):
            sut.ValueIsNotNone().apply(self.put, None)

    def test_none__with_message_builder(self):
        with self.assertRaises(TestException):
            sut.ValueIsNotNone().apply(self.put, None,
                                       sut.MessageBuilder('message head'))

    def test_not_none(self):
        sut.ValueIsNotNone().apply(self.put, 'not none')
        sut.ValueIsNotNone().apply(self.put, 'not none',
                                   sut.MessageBuilder('head'))


class TestEquals(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_false__sans_message_builder(self):
        with self.assertRaises(TestException):
            sut.Equals('expected').apply(self.put, 'not equal to expected')

    def test_false__with_message_builder(self):
        with self.assertRaises(TestException):
            sut.Equals('expected').apply(self.put, 'not equal to expected',
                                         sut.MessageBuilder('message head'))

    def test_true(self):
        sut.Equals('expected').apply(self.put, 'expected')
        sut.Equals('expected').apply(self.put, 'expected',
                                     sut.MessageBuilder('head'))


class TestConstant(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_false__sans_message_builder(self):
        with self.assertRaises(TestException):
            sut.Constant(False).apply(self.put, 'value')

    def test_false__with_message_builder(self):
        with self.assertRaises(TestException):
            sut.Constant(False).apply(self.put, 'value',
                                      sut.MessageBuilder('head'))

    def test_true(self):
        sut.Constant(True).apply(self.put, 'value')
        sut.Constant(True).apply(self.put, 'value',
                                 sut.MessageBuilder('head'))


class TestIsInstance(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_false__sans_message_builder(self):
        with self.assertRaises(TestException):
            sut.IsInstance(int).apply(self.put, 'not an int')

    def test_false__with_message_builder(self):
        with self.assertRaises(TestException):
            sut.IsInstance(int).apply(self.put, 'not an int',
                                      sut.MessageBuilder('head'))

    def test_true(self):
        sut.IsInstance(int).apply(self.put, 1)
        sut.IsInstance(int).apply(self.put, 1,
                                  sut.MessageBuilder('head'))


class TestBoolean(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_false_true__sans_message_builder(self):
        with self.assertRaises(TestException):
            sut.Boolean(False).apply(self.put, True)

    def test_false_false__with_message_builder(self):
        sut.Boolean(False).apply(self.put, False,
                                 sut.MessageBuilder('message header'))

    def test_true_false__with_message_builder(self):
        with self.assertRaises(TestException):
            sut.Boolean(True).apply(self.put, False)

    def test_true_true__with_message_builder(self):
        sut.Boolean(True).apply(self.put, True)


class TestNot(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_true__sans_message_builder(self):
        with self.assertRaises(TestException):
            sut.Not(sut.Constant(True)).apply(self.put, 'value')

    def test_true__with_message_builder(self):
        with self.assertRaises(TestException):
            sut.Not(sut.Constant(True)).apply(self.put, 'value',
                                              sut.MessageBuilder('head'))

    def test_false(self):
        sut.Not(sut.Constant(False)).apply(self.put, 'value')
        sut.Not(sut.Constant(False)).apply(self.put, 'value',
                                           sut.MessageBuilder('head'))


class TestAnd(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_empty_list(self):
        sut.And([]).apply(self.put, 'value')
        sut.And([]).apply(self.put, 'value',
                          sut.MessageBuilder('head'))

    def test_singleton_list__true(self):
        assertions = [sut.Constant(True)]
        sut.And(assertions).apply(self.put, 'value')

    def test_singleton_list__false(self):
        assertions = [sut.Constant(False)]
        with self.assertRaises(TestException):
            sut.And(assertions).apply(self.put, 'value')

    def test_two_element_list__false_false(self):
        assertions = [sut.Constant(False),
                      sut.Constant(False)]
        with self.assertRaises(TestException):
            sut.And(assertions).apply(self.put, 'value')

    def test_two_element_list__false_true(self):
        assertions = [sut.Constant(False),
                      sut.Constant(True)]
        with self.assertRaises(TestException):
            sut.And(assertions).apply(self.put, 'value')

    def test_two_element_list__true_false(self):
        assertions = [sut.Constant(True),
                      sut.Constant(False)]
        with self.assertRaises(TestException):
            sut.And(assertions).apply(self.put, 'value')

    def test_two_element_list__true_true(self):
        assertions = [sut.Constant(True),
                      sut.Constant(True)]
        sut.And(assertions).apply(self.put, 'value')


class TestOr(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_empty_list__sans_message_builder(self):
        with self.assertRaises(TestException):
            sut.Or([]).apply(self.put, 'value')

    def test_empty_list__with_message_builder(self):
        with self.assertRaises(TestException):
            sut.Or([]).apply(self.put, 'value',
                             sut.MessageBuilder('head'))

    def test_singleton_list__true(self):
        assertions = [sut.Constant(True)]
        sut.Or(assertions).apply(self.put, 'value')

    def test_singleton_list__false(self):
        assertions = [sut.Constant(False)]
        with self.assertRaises(TestException):
            sut.Or(assertions).apply(self.put, 'value')

    def test_two_element_list__false_false(self):
        assertions = [sut.Constant(False),
                      sut.Constant(False)]
        with self.assertRaises(TestException):
            sut.Or(assertions).apply(self.put, 'value')

    def test_two_element_list__false_true(self):
        assertions = [sut.Constant(False),
                      sut.Constant(True)]
        sut.Or(assertions).apply(self.put, 'value')

    def test_two_element_list__true_false(self):
        assertions = [sut.Constant(True),
                      sut.Constant(False)]
        sut.Or(assertions).apply(self.put, 'value')

    def test_two_element_list__true_true(self):
        assertions = [sut.Constant(True),
                      sut.Constant(True)]
        sut.Or(assertions).apply(self.put, 'value')


class TestOnTransformed(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_false__sans_message_builder(self):
        with self.assertRaises(TestException):
            value = ['not none']
            sut.OnTransformed(lambda x: x[0],
                              sut.ValueIsNone()).apply(self.put, value)

    def test_false__with_message_builder(self):
        with self.assertRaises(TestException):
            value = ['not none']
            sut.OnTransformed(lambda x: x[0],
                              sut.ValueIsNone()).apply(self.put,
                                                       value,
                                                       sut.MessageBuilder('message head'))

    def test_true(self):
        value = [None]
        sut.OnTransformed(lambda x: x[0],
                          sut.ValueIsNone()).apply(self.put, value)
        sut.OnTransformed(lambda x: x[0],
                          sut.ValueIsNone()).apply(self.put,
                                                   value,
                                                   sut.MessageBuilder('message head'))


class TestSubComponent(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()

    def test_false__sans_message_builder(self):
        with self.assertRaises(TestException):
            value = ['not none']
            sut.sub_component('component name',
                              lambda x: x[0],
                              sut.ValueIsNone()).apply(self.put, value)

    def test_false__with_message_builder(self):
        with self.assertRaises(TestException):
            value = ['not none']
            sut.sub_component('component name',
                              lambda x: x[0],
                              sut.ValueIsNone()).apply(self.put,
                                                       value,
                                                       sut.MessageBuilder('message head'))

    def test_true(self):
        value = [None]
        sut.sub_component('component name',
                          lambda x: x[0],
                          sut.ValueIsNone()).apply(self.put, value)
        sut.sub_component('component name',
                          lambda x: x[0],
                          sut.ValueIsNone()).apply(self.put,
                                                   value,
                                                   sut.MessageBuilder('message head'))


class TestEveryElement(unittest.TestCase):
    def setUp(self):
        self.put = test_case_with_failure_exception_set_to_test_exception()
        self.every_element_is_none = sut.every_element('iterable name',
                                                       sut.ValueIsNone())

    def test_empty_list(self):
        self.every_element_is_none.apply(self.put, [])
        self.every_element_is_none.apply(self.put, [],
                                         sut.MessageBuilder('message head'))

    def test_singleton_list__true(self):
        self.every_element_is_none.apply(self.put, [None])

    def test_singleton_list__false(self):
        with self.assertRaises(TestException):
            self.every_element_is_none.apply(self.put, ['not none'])

    def test_two_element_list__false_false(self):
        with self.assertRaises(TestException):
            self.every_element_is_none.apply(self.put, ['not none 1', 'not none 2'])

    def test_two_element_list__false_true(self):
        with self.assertRaises(TestException):
            self.every_element_is_none.apply(self.put, ['not none 1', None])

    def test_two_element_list__true_false(self):
        with self.assertRaises(TestException):
            self.every_element_is_none.apply(self.put, [None, 'not none 2'])

    def test_two_element_list__true_true(self):
        self.every_element_is_none.apply(self.put, [None, None])


def test_case_with_failure_exception_set_to_test_exception() -> unittest.TestCase:
    put = unittest.TestCase()
    put.failureException = TestException
    return put


def suite():
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestIsNone))
    ret_val.addTest(unittest.makeSuite(TestIsNotNone))
    ret_val.addTest(unittest.makeSuite(TestBoolean))
    ret_val.addTest(unittest.makeSuite(TestEquals))
    ret_val.addTest(unittest.makeSuite(TestConstant))
    ret_val.addTest(unittest.makeSuite(TestIsInstance))
    ret_val.addTest(unittest.makeSuite(TestNot))
    ret_val.addTest(unittest.makeSuite(TestAnd))
    ret_val.addTest(unittest.makeSuite(TestOr))
    ret_val.addTest(unittest.makeSuite(TestOnTransformed))
    ret_val.addTest(unittest.makeSuite(TestSubComponent))
    ret_val.addTest(unittest.makeSuite(TestEveryElement))
    return ret_val


def run_suite():
    runner = unittest.TextTestRunner()
    runner.run(suite())


if __name__ == '__main__':
    run_suite()
