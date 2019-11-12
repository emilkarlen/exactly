import unittest

from exactly_lib.type_system.data import concrete_path_parts as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPathPartAsFixedPath),
        unittest.makeSuite(TestPathPartAsNothing),
        unittest.makeSuite(TestPathPartVisitor),
    ])


class TestPathPartAsFixedPath(unittest.TestCase):
    def test_value(self):
        # ARRANGE #
        path_part = sut.PathPartDdvAsFixedPath('the file name')
        # ACT #
        actual = path_part.value()
        # ASSERT #
        self.assertEqual('the file name',
                         actual,
                         'resolved file name')


class TestPathPartAsNothing(unittest.TestCase):
    def test_resolve(self):
        # ARRANGE #
        path_part = sut.PathPartDdvAsNothing()
        # ACT #
        actual = path_part.value()
        # ASSERT #
        self.assertEqual('',
                         actual,
                         'resolved file name')


class TestPathPartVisitor(unittest.TestCase):
    def test_visit_fixed_path(self):
        # ARRANGE #
        recording_visitor = _VisitorThatRegisterClassOfVisitMethod()
        path_suffix = sut.PathPartDdvAsFixedPath('file name')
        # ACT #
        ret_val = recording_visitor.visit(path_suffix)
        # ASSERT #
        self.assertEqual([sut.PathPartDdvAsFixedPath],
                         recording_visitor.visited_classes,
                         'The method for visiting a %s should have been invoked'
                         % str(sut.PathPartDdvAsFixedPath))
        self.assertIs(path_suffix,
                      ret_val,
                      'Returns value from visitor')

    def test_visit_nothing(self):
        # ARRANGE #
        recording_visitor = _VisitorThatRegisterClassOfVisitMethod()
        path_suffix = sut.PathPartDdvAsNothing()
        # ACT #
        ret_val = recording_visitor.visit(path_suffix)
        # ASSERT #
        self.assertEqual([sut.PathPartDdvAsNothing],
                         recording_visitor.visited_classes,
                         'The method for visiting a %s should have been invoked'
                         % str(sut.PathPartDdvAsNothing))
        self.assertIs(path_suffix,
                      ret_val,
                      'Returns value from visitor')

    def test_visit_invalid_object_should_raise_exception(self):
        # ARRANGE #
        recording_visitor = _VisitorThatRegisterClassOfVisitMethod()
        not_a_path_suffix = 'a string is not a sub class of ' + str(sut.PathPartDdv)
        # ACT & ASSERT #
        with self.assertRaises(TypeError):
            recording_visitor.visit(not_a_path_suffix)


class _VisitorThatRegisterClassOfVisitMethod(sut.PathPartDdvVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_fixed_path(self, path_suffix: sut.PathPartDdvAsFixedPath):
        self.visited_classes.append(sut.PathPartDdvAsFixedPath)
        return path_suffix

    def visit_nothing(self, path_suffix: sut.PathPartDdvAsNothing):
        self.visited_classes.append(sut.PathPartDdvAsNothing)
        return path_suffix
