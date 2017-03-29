import pathlib
import unittest

from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath, \
    PathPartAsStringSymbolReference
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction, NoRestriction
from exactly_lib.value_definition.concrete_values import FileRefValue
from exactly_lib.value_definition.value_structure import ValueContainer, ValueReference
from exactly_lib_test.test_case_file_structure.test_resources import file_ref as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEquals(),
        unittest.makeSuite(TestNotEquals_PathSuffixAsFixedPath),
        unittest.makeSuite(TestNotEquals_PathSuffixAsSymbolReference),
        unittest.makeSuite(TestNotEquals_DifferentTypeOfPathSuffix),
    ])


class TestEquals(unittest.TestCase):
    def runTest(self):
        test_cases = [
            (_FileRefWithoutValRefInRootPart(_EXISTS_PRE_SDS_RELATIVITY,
                                             PathPartAsFixedPath('file-name')),
             'Exists pre SDS/fixed path suffix'
             ),
            (_FileRefWithoutValRefInRootPart(_NOT_EXISTS_PRE_SDS_RELATIVITY,
                                             PathPartAsFixedPath('a-file-name')),
             'NOT Exists pre SDS/fixed path suffix'
             ),
            (_FileRefWithValRefInRootPart(
                ValueReference('reffed-name',
                               _relativity_restriction({RelOptionType.REL_ACT}, False)),
                PathPartAsFixedPath('file-name')),
             'symbol-ref/NOT Exists pre SDS/fixed path suffix'
            ),
            (_FileRefWithoutValRefInRootPart(_EXISTS_PRE_SDS_RELATIVITY,
                                             PathPartAsStringSymbolReference('symbol-name')),
             'Exists pre SDS/fixed path suffix'
             ),
            (_FileRefWithoutValRefInRootPart(_NOT_EXISTS_PRE_SDS_RELATIVITY,
                                             PathPartAsStringSymbolReference('a-symbol-name')),
             'NOT Exists pre SDS/fixed path suffix'
             ),
            (_FileRefWithValRefInRootPart(
                ValueReference('reffed-name',
                               _relativity_restriction({RelOptionType.REL_ACT}, False)),
                PathPartAsStringSymbolReference('symbol-name')),
             'symbol-ref/NOT Exists pre SDS/fixed path suffix'
            ),
        ]
        for value, msg in test_cases:
            with self.subTest(msg=msg):
                sut.file_ref_equals(value).apply_with_message(self, value, msg)


class TestNotEquals_PathSuffixAsFixedPath(unittest.TestCase):
    def test_differs__file_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT, PathPartAsFixedPath('other-file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        actual = _FileRefWithoutValRefInRootPart(_NOT_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = _FileRefWithoutValRefInRootPart(RelOptionType.REL_HOME, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_value_ref__differs__relativity_variants(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                               _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                                PathPartAsFixedPath('file-name'))
        actual = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                             _relativity_restriction({RelOptionType.REL_HOME}, False)),
                                              PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_value_ref__differs__value_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                               _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                                PathPartAsFixedPath('file-name'))
        actual = _FileRefWithValRefInRootPart(ValueReference('OTHER-reffed-name',
                                                             _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                              PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__no_value_refs__value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                               _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                                PathPartAsFixedPath('file-name'))
        actual = _FileRefWithoutValRefInRootPart(RelOptionType.REL_RESULT,
                                                 PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__value_refs__no_value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(RelOptionType.REL_RESULT,
                                                   PathPartAsFixedPath('file-name'))
        actual = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                             _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                              PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_value_ref__invalid_type_of_value_restriction(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                               _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                                PathPartAsFixedPath('file-name'))
        actual = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                             NoRestriction()),
                                              PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')


class TestNotEquals_PathSuffixAsSymbolReference(unittest.TestCase):
    def test_differs__symbol_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT,
                                                   PathPartAsStringSymbolReference('symbol-name'))
        actual = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT,
                                                 PathPartAsStringSymbolReference('other-symbol-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(_EXISTS_PRE_SDS_RELATIVITY,
                                                   PathPartAsStringSymbolReference('symbol-name'))
        actual = _FileRefWithoutValRefInRootPart(_NOT_EXISTS_PRE_SDS_RELATIVITY,
                                                 PathPartAsStringSymbolReference('symbol-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT,
                                                   PathPartAsStringSymbolReference('symbol-name'))
        actual = _FileRefWithoutValRefInRootPart(RelOptionType.REL_HOME,
                                                 PathPartAsStringSymbolReference('symbol-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_value_ref__differs__relativity_variants(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                               _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                                PathPartAsStringSymbolReference('symbol-name'))
        actual = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                             _relativity_restriction({RelOptionType.REL_HOME}, False)),
                                              PathPartAsStringSymbolReference('symbol-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_value_ref__differs__value_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                               _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                                PathPartAsStringSymbolReference('symbol-name'))
        actual = _FileRefWithValRefInRootPart(ValueReference('OTHER-reffed-name',
                                                             _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                              PathPartAsStringSymbolReference('symbol-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__no_value_refs__value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                               _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                                PathPartAsStringSymbolReference('symbol-name'))
        actual = _FileRefWithoutValRefInRootPart(RelOptionType.REL_RESULT,
                                                 PathPartAsStringSymbolReference('symbol-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__value_refs__no_value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(RelOptionType.REL_RESULT,
                                                   PathPartAsStringSymbolReference('symbol-name'))
        actual = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                             _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                              PathPartAsStringSymbolReference('symbol-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_value_ref__invalid_type_of_value_restriction(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                               _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                                PathPartAsStringSymbolReference('symbol-name'))
        actual = _FileRefWithValRefInRootPart(ValueReference('reffed-name',
                                                             NoRestriction()),
                                              PathPartAsStringSymbolReference('symbol-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')


class TestNotEquals_DifferentTypeOfPathSuffix(unittest.TestCase):
    def test_without_symbol_ref_in_root_part__expected_is_symbol_reference(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT,
                                                   PathPartAsStringSymbolReference('name'))
        actual = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT,
                                                 PathPartAsFixedPath('name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_without_symbol_ref_in_root_part__expected_is_fixed_path(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT,
                                                   PathPartAsFixedPath('name'))
        actual = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT,
                                                 PathPartAsStringSymbolReference('name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_with_symbol_ref_in_root_part(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRefInRootPart(ValueReference('reffed-name', NoRestriction()),
                                                PathPartAsStringSymbolReference('name'))
        actual = _FileRefWithValRefInRootPart(ValueReference('reffed-name', NoRestriction()),
                                              PathPartAsFixedPath('name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')


class _FileRefWithoutValRefInRootPart(FileRef):
    """
    A dummy FileRef that has a given relativity,
    and is as simple as possible.
    """

    def __init__(self,
                 relativity: RelOptionType,
                 path_suffix: PathPart):
        super().__init__(path_suffix)
        self._relativity = relativity
        self.__path_suffix = path_suffix

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        return self._relativity

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        return self.relativity == RelOptionType.REL_HOME

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return pathlib.Path(str(self.relativity)) / self.path_suffix_path(environment.value_definitions)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        return pathlib.Path(str(self.relativity)) / self.path_suffix_path(environment.value_definitions)

    def value_references_of_paths(self) -> list:
        return self.__path_suffix.value_references


class _FileRefWithValRefInRootPart(FileRef):
    """
    A dummy FileRef that has a given relativity,
    and is as simple as possible.
    """

    def __init__(self,
                 value_reference: ValueReference,
                 path_suffix: PathPart):
        super().__init__(path_suffix)
        self._value_references_of_path = value_reference
        self.__path_suffix = path_suffix

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        return self._lookup(value_definitions).relativity(value_definitions)

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        return self._lookup(value_definitions).exists_pre_sds(value_definitions)

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return self._lookup(environment.value_definitions).file_path_pre_sds(environment)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        return self._lookup(environment.value_definitions).file_path_post_sds(environment)

    def value_references_of_paths(self) -> list:
        return [self._value_references_of_path] + self.__path_suffix.value_references

    def _lookup(self, value_definitions: SymbolTable) -> FileRef:
        def_in_symbol_table = value_definitions.lookup(self._value_references_of_path.name)
        assert isinstance(def_in_symbol_table, ValueContainer), 'Symbol Table is assumed to contain ValueContainer:s'
        value = def_in_symbol_table.value
        assert isinstance(value, FileRefValue), 'Referenced ValueContainer must contain a FileRefValue'
        return value.file_ref


_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_HOME
_NOT_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_ACT


def _relativity_restriction(rel_option_types: set, absolute_is_valid: bool):
    return FileRefRelativityRestriction(PathRelativityVariants(rel_option_types, absolute_is_valid))
