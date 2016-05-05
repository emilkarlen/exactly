import unittest

from exactly_lib.util.cli_syntax.elements import argument as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(ArgumentRecordingArgumentVisitor),
        unittest.makeSuite(ArgumentVisitorTest),
    ])


if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())


class ArgumentRecordingArgumentVisitor(sut.ArgumentVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_constant(self, x: sut.Constant):
        self.visited_classes.append(sut.Constant)
        return x

    def visit_named(self, x: sut.Named):
        self.visited_classes.append(sut.Named)
        return x

    def visit_option(self, x: sut.Option):
        self.visited_classes.append(sut.Option)
        return x


class ArgumentVisitorTest(unittest.TestCase):
    def test_as_is(self):
        self._check(sut.Constant('name'), sut.Constant)

    def test_positional(self):
        self._check(sut.Named('value-element'), sut.Named)

    def test_plain_option(self):
        self._check(sut.Option('n'), sut.Option)

    def test_visit_SHOULD_raise_TypeError_WHEN_argument_is_not_a_sub_class_of_argument(self):
        visitor = ArgumentRecordingArgumentVisitor()
        with self.assertRaises(TypeError):
            visitor.visit('not an argument')

    def _check(self, x: sut.Argument, expected_class):
        # ARRANGE #
        visitor = ArgumentRecordingArgumentVisitor()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertListEqual([expected_class],
                             visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'Visitor should return the return-value of the visited method')
