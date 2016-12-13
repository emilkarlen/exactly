import unittest

from exactly_lib.common.help import see_also as sut
from exactly_lib.help.cross_reference_id import CustomCrossReferenceId
from exactly_lib.util.textformat.structure.core import StringText


class ArgumentRecordingVisitor(sut.SeeAlsoItemVisitor):
    def __init__(self):
        self.visited_classes = []

    def visit_cross_reference_id(self, x: sut.CrossReferenceIdSeeAlsoItem):
        self.visited_classes.append(sut.CrossReferenceIdSeeAlsoItem)
        return x

    def visit_text(self, x: sut.TextSeeAlsoItem):
        self.visited_classes.append(sut.TextSeeAlsoItem)
        return x


class SeeAlsoItemVisitorTest(unittest.TestCase):
    def test_cross_reference_id(self):
        self._check(sut.CrossReferenceIdSeeAlsoItem(CustomCrossReferenceId('target name')),
                    sut.CrossReferenceIdSeeAlsoItem)

    def test_text(self):
        self._check(sut.TextSeeAlsoItem(StringText('text value')),
                    sut.TextSeeAlsoItem)

    def test_visit_SHOULD_raise_TypeError_WHEN_argument_is_not_a_sub_class_of_argument(self):
        visitor = ArgumentRecordingVisitor()
        with self.assertRaises(TypeError):
            visitor.visit('not an argument usage')

    def _check(self, x: sut.SeeAlsoItem, expected_class):
        # ARRANGE #
        visitor = ArgumentRecordingVisitor()
        # ACT #
        returned = visitor.visit(x)
        # ASSERT #
        self.assertListEqual([expected_class],
                             visitor.visited_classes)
        self.assertIs(x,
                      returned,
                      'Visitor should return the return-value of the visited method')
