import pathlib
import unittest

from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_relativity import RelOptionType, PathRelativityVariants
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
        unittest.makeSuite(TestNotEquals),
    ])


class TestEquals(unittest.TestCase):
    def runTest(self):
        test_cases = [
            (_FileRefWithoutValRef(_EXISTS_PRE_SDS_RELATIVITY, 'file-name'),
             'Exists pre SDS'
             ),
            (_FileRefWithoutValRef(_NOT_EXISTS_PRE_SDS_RELATIVITY, 'a-file-name'),
             'NOT Exists pre SDS'
             ),
            (_FileRefWithValRef(
                ValueReference('reffed-name',
                               _relativity_restriction({RelOptionType.REL_ACT}, False)),
                'file-name'),
             'symbol-ref/NOT Exists pre SDS'
            ),
        ]
        for value, msg in test_cases:
            with self.subTest(msg=msg):
                sut.file_ref_equals(value).apply_with_message(self, value, msg)


class TestNotEquals(unittest.TestCase):
    def test_differs__file_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRef(RelOptionType.REL_ACT, 'file-name')
        actual = _FileRefWithoutValRef(RelOptionType.REL_ACT, 'other-file-name')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRef(_EXISTS_PRE_SDS_RELATIVITY, 'file-name')
        actual = _FileRefWithoutValRef(_NOT_EXISTS_PRE_SDS_RELATIVITY, 'file-name')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRef(RelOptionType.REL_ACT, 'file-name')
        actual = _FileRefWithoutValRef(RelOptionType.REL_HOME, 'file-name')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_value_ref__differs__relativity_variants(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRef(ValueReference('reffed-name',
                                                     _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                      'file-name')
        actual = _FileRefWithValRef(ValueReference('reffed-name',
                                                   _relativity_restriction({RelOptionType.REL_HOME}, False)),
                                    'file-name')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_value_ref__differs__value_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRef(ValueReference('reffed-name',
                                                     _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                      'file-name')
        actual = _FileRefWithValRef(ValueReference('OTHER-reffed-name',
                                                   _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                    'file-name')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__no_value_refs__value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRef(ValueReference('reffed-name',
                                                     _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                      'file-name')
        actual = _FileRefWithoutValRef(RelOptionType.REL_RESULT,
                                       'file-name')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__value_refs__no_value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRef(RelOptionType.REL_RESULT,
                                         'file-name')
        actual = _FileRefWithValRef(ValueReference('reffed-name',
                                                   _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                    'file-name')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_value_ref__invalid_type_of_value_restriction(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRef(ValueReference('reffed-name',
                                                     _relativity_restriction({RelOptionType.REL_ACT}, False)),
                                      'file-name')
        actual = _FileRefWithValRef(ValueReference('reffed-name',
                                                   NoRestriction()),
                                    'file-name')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')


class _FileRefWithoutValRef(FileRef):
    """
    A dummy FileRef that has a given relativity,
    and is as simple as possible.
    """

    def __init__(self,
                 relativity: RelOptionType,
                 file_name: str):
        super().__init__(PathPartAsFixedPath(file_name))
        self._relativity = relativity

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        return self._relativity

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        return self.relativity == RelOptionType.REL_HOME

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return pathlib.Path(str(self.relativity)) / self.path_suffix_path(environment.value_definitions)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        return pathlib.Path(str(self.relativity)) / self.path_suffix_path(environment.value_definitions)

    def value_references_of_paths(self) -> list:
        return []


class _FileRefWithValRef(FileRef):
    """
    A dummy FileRef that has a given relativity,
    and is as simple as possible.
    """

    def __init__(self,
                 value_reference: ValueReference,
                 file_name: str):
        super().__init__(PathPartAsFixedPath(file_name))
        self._value_references_of_path = value_reference

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        return self._lookup(value_definitions).relativity(value_definitions)

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        return self._lookup(value_definitions).exists_pre_sds(value_definitions)

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return self._lookup(environment.value_definitions).file_path_pre_sds(environment)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        return self._lookup(environment.value_definitions).file_path_post_sds(environment)

    def value_references_of_paths(self) -> list:
        return [self._value_references_of_path]

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
