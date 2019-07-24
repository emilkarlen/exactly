import unittest

from exactly_lib.util import file_printables
from exactly_lib.util.simple_textstruct import structure as sut


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestPreFormattedStringLineObject),
        unittest.makeSuite(TestStringLineObject),
        unittest.makeSuite(TestStringLinesObject),
        unittest.makeSuite(TestFilePrintableLineObject),

        unittest.makeSuite(TestMinorBlock),
        unittest.makeSuite(TestMajorBlock),
        unittest.makeSuite(TestDocument),
    ])


class TestPreFormattedStringLineObject(unittest.TestCase):
    def test_getters(self):
        # ARRANGE #

        string_arg = 's'
        line_ended_arg = False
        line_object = sut.PreFormattedStringLineObject(string_arg, line_ended_arg)

        # ACT && ASSERT #

        self.assertIs(string_arg,
                      line_object.string,
                      'string')

        self.assertIs(line_ended_arg,
                      line_object.string_is_line_ended,
                      'string_is_line_ended')

    def test_accept_visitor(self):
        # ARRANGE #

        line_object = sut.PreFormattedStringLineObject('s', False)
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheEnv()
        env = 'PreFormattedStringLineObject'

        # ACT #

        return_value = line_object.accept(visitor, env)

        # ASSERT #

        self.assertEqual(env, return_value,
                         'return value')
        self.assertEqual([sut.PreFormattedStringLineObject],
                         visitor.visited_classes,
                         'visitor method')


class TestStringLineObject(unittest.TestCase):
    def test_getters(self):
        # ARRANGE #

        string_arg = 's'
        line_ended_arg = False
        line_object = sut.StringLineObject(string_arg, line_ended_arg)

        # ACT && ASSERT #

        self.assertIs(string_arg,
                      line_object.string,
                      'string')

        self.assertIs(line_ended_arg,
                      line_object.string_is_line_ended,
                      'string_is_line_ended')

    def test_accept_visitor(self):
        # ARRANGE #

        line_object = sut.StringLineObject('s', False)
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheEnv()
        env = 'StringLineObject'

        # ACT #

        return_value = line_object.accept(visitor, env)

        # ASSERT #

        self.assertEqual(env, return_value,
                         'return value')
        self.assertEqual([sut.StringLineObject],
                         visitor.visited_classes,
                         'visitor method')


class TestStringLinesObject(unittest.TestCase):
    def test_getters(self):
        # ARRANGE #

        strings_arg = ['s']
        line_object = sut.StringLinesObject(strings_arg)

        # ACT && ASSERT #

        self.assertIs(strings_arg,
                      line_object.strings,
                      'strings')

    def test_accept_visitor(self):
        # ARRANGE #

        line_object = sut.StringLinesObject(['s'])
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheEnv()
        env = 'StringLinesObject'

        # ACT #

        return_value = line_object.accept(visitor, env)

        # ASSERT #

        self.assertEqual(env, return_value,
                         'return value')
        self.assertEqual([sut.StringLinesObject],
                         visitor.visited_classes,
                         'visitor method')


class TestFilePrintableLineObject(unittest.TestCase):
    def test_getters(self):
        # ARRANGE #

        fp_arg = file_printables.of_new_line()
        line_ended_arg = True
        line_object = sut.FilePrintableLineObject(fp_arg, line_ended_arg)

        # ACT && ASSERT #

        self.assertIs(fp_arg,
                      line_object.file_printable,
                      'file_printable')
        self.assertIs(line_ended_arg,
                      line_object.is_line_ended,
                      'is_line_ended')

    def test_accept_visitor(self):
        # ARRANGE #

        line_object = sut.FilePrintableLineObject(file_printables.of_new_line(),
                                                  False)
        visitor = VisitorThatRegistersVisitedClassesAndReturnsTheEnv()
        env = 'FilePrintableLineObject'

        # ACT #

        return_value = line_object.accept(visitor, env)

        # ASSERT #

        self.assertEqual(env, return_value,
                         'return value')
        self.assertEqual([sut.FilePrintableLineObject],
                         visitor.visited_classes,
                         'visitor method')


class TestMinorBlock(unittest.TestCase):
    def test_getters(self):
        # ARRANGE #

        parts_arg = []
        properties_arg = sut.ElementProperties(False, None)
        block = sut.MinorBlock(parts_arg, properties_arg)

        # ACT && ASSERT #

        self.assertIs(parts_arg,
                      block.parts,
                      'parts')
        self.assertIs(properties_arg,
                      block.properties,
                      'properties_arg')


class TestMajorBlock(unittest.TestCase):
    def test_getters(self):
        # ARRANGE #

        parts = []
        properties_arg = sut.ElementProperties(False, None)
        block = sut.MajorBlock(parts, properties_arg)

        # ACT && ASSERT #

        self.assertIs(parts,
                      block.parts,
                      'parts')
        self.assertIs(properties_arg,
                      block.properties,
                      'properties_arg')


class TestDocument(unittest.TestCase):
    def test_getters(self):
        # ARRANGE #

        blocks_arg = []
        document = sut.Document(blocks_arg)

        # ACT && ASSERT #

        self.assertIs(blocks_arg,
                      document.blocks,
                      'blocks')


class VisitorThatRegistersVisitedClassesAndReturnsTheEnv(sut.LineObjectVisitor[str, str]):
    def __init__(self):
        self.visited_classes = []

    def visit_pre_formatted(self, env: str, x: sut.PreFormattedStringLineObject) -> str:
        self.visited_classes.append(sut.PreFormattedStringLineObject)
        return env

    def visit_string(self, env: str, x: sut.StringLineObject) -> str:
        self.visited_classes.append(sut.StringLineObject)
        return env

    def visit_string_lines(self, env: str, x: sut.StringLinesObject) -> str:
        self.visited_classes.append(sut.StringLinesObject)
        return env

    def visit_file_printable(self, env: str, x: sut.FilePrintableLineObject) -> str:
        self.visited_classes.append(sut.FilePrintableLineObject)
        return env
