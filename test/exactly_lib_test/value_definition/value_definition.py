import unittest

from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.file_ref_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.value_definition import value_definition_usage as sut
from exactly_lib.value_definition.file_ref_with_val_def import rel_value_definition
from exactly_lib.value_definition.value_definition_usage import ValueReferenceOfPath
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources import value_definition as tr
from exactly_lib_test.value_definition.test_resources import value_definition as vd_tr
from exactly_lib_test.value_definition.test_resources.value_reference import equals_value_reference


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestValueDefinitionVisitor),
        unittest.makeSuite(TestValueReferenceVisitor),
        unittest.makeSuite(TestValueDefinitionOfPathShouldReportAllReferencedValueDefinitions),

    ])


class TestValueDefinitionOfPathShouldReportAllReferencedValueDefinitions(unittest.TestCase):
    def test_no_references(self):
        # ARRANGE #
        value_definition = sut.ValueDefinitionOfPath('VAL_DEF',
                                                     vd_tr.file_ref_value(file_refs.rel_home('path')))
        # ACT #
        actual = value_definition.referenced_values
        # ASSERT #
        self.assertListEqual([], actual,
                             'A definition that references no value definitions should report an empty list')

    def test_one_reference(self):
        # ARRANGE #
        value_reference = ValueReferenceOfPath('REFERENCED_DEF',
                                               PathRelativityVariants({RelOptionType.REL_CWD},
                                                                      True))
        value_definition = sut.ValueDefinitionOfPath(
            'VAL_DEF',
            vd_tr.file_ref_value(
                rel_value_definition(value_reference, 'file-name')))
        # ACT #
        actual = value_definition.referenced_values
        # ASSERT #
        asrt.matches_sequence([equals_value_reference(value_reference)]).apply_with_message(self, actual,
                                                                                            'referenced_values')


class TestValueReferenceVisitor(unittest.TestCase):
    def test_visit_path(self):
        # ARRANGE #
        visitor = _ValueReferenceVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        visitor.visit(sut.ValueReferenceOfPath('name', sut.PathRelativityVariants(set(), False)))
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.ValueReferenceOfPath],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _ValueReferenceVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit('a string is not a ValueReference')


class _ValueReferenceVisitorTestThatRegistersClassOfVisitedObjects(sut.ValueReferenceVisitor):
    def __init__(self):
        self.visited_classes = []

    def _visit_path(self, path_reference: sut.ValueReferenceOfPath):
        self.visited_classes.append(sut.ValueReferenceOfPath)


class TestValueDefinitionVisitor(unittest.TestCase):
    def test_visit_path(self):
        # ARRANGE #
        visitor = _ValueDefinitionVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        visitor.visit(sut.ValueDefinitionOfPath('name', tr.file_ref_value()))
        # ASSERT #
        self.assertListEqual(visitor.visited_classes,
                             [sut.ValueDefinitionOfPath],
                             'visited classes')

    def test_visit_non_sub_class_should_raise_exception(self):
        # ARRANGE #
        visitor = _ValueDefinitionVisitorTestThatRegistersClassOfVisitedObjects()
        # ACT #
        with self.assertRaises(TypeError):
            visitor.visit('a string is not a ValueReference')


class _ValueDefinitionVisitorTestThatRegistersClassOfVisitedObjects(sut.ValueDefinitionVisitor):
    def __init__(self):
        self.visited_classes = []

    def _visit_path(self, value_definition: sut.ValueDefinitionOfPath):
        self.visited_classes.append(sut.ValueDefinitionOfPath)
