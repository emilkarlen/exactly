import pathlib
import unittest

from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath, \
    PathPartAsNothing
from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_base import FileRefWithPathSuffixBase, \
    FileRefWithPathSuffixAndIsNotAbsoluteBase
from exactly_lib.test_case_file_structure.path_part import PathPart
from exactly_lib.test_case_file_structure.path_relativity import RelOptionType, PathRelativityVariants, \
    SpecificPathRelativity
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.util.symbol_table import SymbolTable, empty_symbol_table
from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction, \
    EitherStringOrFileRefRelativityRestriction, StringRestriction
from exactly_lib.value_definition.concrete_values import FileRefResolver
from exactly_lib.value_definition.value_structure import ValueContainer, ValueReference
from exactly_lib_test.test_case_file_structure.test_resources import file_ref as sut
from exactly_lib_test.test_resources.test_of_test_resources_util import \
    test_case_with_failure_exception_set_to_test_exception, TestException
from exactly_lib_test.value_definition.test_resources.value_definition_utils import \
    symbol_table_from_value_definitions, string_value_definition, \
    file_ref_value_definition, symbol_table_with_single_file_ref_value


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestEqualsCommonToBothAssertionMethods(),
        TestEqualsSpecificForAssertionMethod2WithIgnoredValueReferences(),
        unittest.makeSuite(TestNotEquals_PathSuffixAsFixedPath),
        unittest.makeSuite(TestNotEquals_DifferentTypeOfPathSuffix),
        unittest.makeSuite(Test2NotEquals),
    ])


class TestEqualsCommonToBothAssertionMethods(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('Exists pre SDS/fixed path suffix',
             _FileRefWithoutValRefInRootPart(_EXISTS_PRE_SDS_RELATIVITY,
                                             PathPartAsFixedPath('file-name')),
             empty_symbol_table(),
             ),
            ('NOT Exists pre SDS/fixed path suffix',
             _FileRefWithoutValRefInRootPart(_NOT_EXISTS_PRE_SDS_RELATIVITY,
                                             PathPartAsFixedPath('a-file-name')),
             empty_symbol_table(),
             ),
            ('symbol-ref/NOT Exists pre SDS/fixed path suffix',
             _FileRefWithValRefInRootPart(
                 ValueReference('reffed-name',
                                _relativity_restriction({RelOptionType.REL_ACT}, False)),
                 PathPartAsFixedPath('file-name')),
             symbol_table_with_single_file_ref_value('reffed-name'),
             ),
            ('symbol-ref(either-string-or-file-ref actual is file-ref)/NOT Exists pre SDS/fixed path suffix',
             _FileRefWithValRefInRootPart(
                 ValueReference('reffed-name',
                                EitherStringOrFileRefRelativityRestriction(
                                    StringRestriction(),
                                    _relativity_restriction({RelOptionType.REL_ACT}, False))
                                ),
                 PathPartAsFixedPath('file-name')),
             symbol_table_with_single_file_ref_value('reffed-name'),
             ),
            ('symbol-ref(either-string-or-file-ref actual is string)/NOT Exists pre SDS/fixed path suffix',
             _FileRefWithValRefInRootPart(
                 ValueReference('reffed-name',
                                EitherStringOrFileRefRelativityRestriction(
                                    StringRestriction(),
                                    _relativity_restriction({RelOptionType.REL_ACT}, False))
                                ),
                 PathPartAsFixedPath('file-name')),
             symbol_table_with_single_file_ref_value('reffed-name'),
             ),
        ]
        for test_case_name, value, symbol_table_for_method2 in test_cases:
            assert isinstance(value, FileRef), 'Type info for IDE'
            with self.subTest(msg='file_ref_equals::' + test_case_name):
                assertion = sut.file_ref_equals(value)
                assertion.apply_with_message(self, value, test_case_name)
            with self.subTest(msg='equals_file_ref2::' + test_case_name):
                assertion = sut.equals_file_ref2(value,
                                                 symbol_table_for_method2)
                assertion.apply_with_message(self, value, test_case_name)


class TestEqualsSpecificForAssertionMethod2WithIgnoredValueReferences(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('Nothing path suffixes',
             _FileRefWithoutValRefInRootPart(_EXISTS_PRE_SDS_RELATIVITY,
                                             PathPartAsNothing()),
             _FileRefWithoutValRefInRootPart(_EXISTS_PRE_SDS_RELATIVITY,
                                             PathPartAsNothing()),
             symbol_table_from_value_definitions([
                 string_value_definition('path_suffix_symbol_1', 'suffix-file-name'),
                 string_value_definition('path_suffix_symbol_2', 'suffix-file-name'),
             ])
             ),
            ('Different symbol references in root',
             _FileRefWithValRefInRootPart(
                 ValueReference('path_root_symbol_1',
                                _relativity_restriction({RelOptionType.REL_ACT}, False)),
                 PathPartAsFixedPath('file-name')),
             _FileRefWithValRefInRootPart(
                 ValueReference('path_root_symbol_2',
                                _relativity_restriction({RelOptionType.REL_ACT}, False)),
                 PathPartAsFixedPath('file-name')),
             symbol_table_from_value_definitions([
                 file_ref_value_definition('path_root_symbol_1',
                                           _FileRefWithoutValRefInRootPart(RelOptionType.REL_TMP,
                                                                           PathPartAsFixedPath('suffix-of-root'))),
                 file_ref_value_definition('path_root_symbol_2',
                                           _FileRefWithoutValRefInRootPart(RelOptionType.REL_TMP,
                                                                           PathPartAsFixedPath('suffix-of-root'))
                                           ),
             ])
             ),
            ('Different kind of root resolving',
             _FileRefWithValRefInRootPart(
                 ValueReference('reffed_file_ref_name',
                                _relativity_restriction({RelOptionType.REL_ACT}, False)),
                 PathPartAsFixedPath('2')),
             _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT,
                                             PathPartAsFixedPath('1/2')),
             symbol_table_with_single_file_ref_value('reffed_file_ref_name',
                                                     _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT,
                                                                                     PathPartAsFixedPath('1'))),
             ),
        ]
        for test_case_name, first, second, symbol_table_for_method2 in test_cases:
            assert isinstance(first, FileRef), 'Type info for IDE (first)'
            assert isinstance(second, FileRef), 'Type info for IDE (second)'
            with self.subTest(msg='1::' + test_case_name):
                assertion = sut.equals_file_ref2(first,
                                                 symbol_table_for_method2)
                assertion.apply_with_message(self, second, test_case_name)
            with self.subTest(msg='2::' + test_case_name):
                assertion = sut.equals_file_ref2(second,
                                                 symbol_table_for_method2)
                assertion.apply_with_message(self, first, test_case_name)


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


class TestNotEquals_DifferentTypeOfPathSuffix(unittest.TestCase):
    def runTest(self):
        pass
        # def test_without_symbol_ref_in_root_part__expected_is_fixed_path(self):
        #     # ARRANGE #
        #     put = test_case_with_failure_exception_set_to_test_exception()
        #     expected = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT,
        #                                                PathPartAsFixedPath('name'))
        #     actual = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT,
        #                                              PathPartAsStringSymbolReference('name'))
        #     # ACT & ASSERT #
        #     with put.assertRaises(TestException):
        #         sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')


class Test2NotEquals(unittest.TestCase):
    def test_differs__file_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT, PathPartAsFixedPath('other-file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref2(expected, empty_symbol_table())
            assertion.apply_with_message(put, actual, 'NotEquals')

    def test_differs__exists_pre_sds(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        actual = _FileRefWithoutValRefInRootPart(_NOT_EXISTS_PRE_SDS_RELATIVITY, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref2(expected, empty_symbol_table())
            assertion.apply_with_message(put, actual, 'NotEquals')

    def test_differs__relativity(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithoutValRefInRootPart(RelOptionType.REL_ACT, PathPartAsFixedPath('file-name'))
        actual = _FileRefWithoutValRefInRootPart(RelOptionType.REL_HOME, PathPartAsFixedPath('file-name'))
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            assertion = sut.equals_file_ref2(expected, empty_symbol_table())
            assertion.apply_with_message(put, actual, 'NotEquals')


class _FileRefWithoutValRefInRootPart(FileRefWithPathSuffixAndIsNotAbsoluteBase):
    """
    A dummy FileRef that has a given relativity,
    and is as simple as possible.
    """

    def __init__(self,
                 relativity: RelOptionType,
                 path_suffix: PathPart):
        super().__init__(path_suffix)
        self.__relativity = relativity
        self.__path_suffix = path_suffix

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        return self.__relativity == RelOptionType.REL_HOME

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return pathlib.Path(str(self.__relativity)) / self.path_suffix_path(environment.value_definitions)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        return pathlib.Path(str(self.__relativity)) / self.path_suffix_path(environment.value_definitions)

    def value_references(self) -> list:
        return self.__path_suffix.value_references

    def _relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        return self.__relativity


class _FileRefWithValRefInRootPart(FileRefWithPathSuffixBase):
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

    def relativity(self, value_definitions: SymbolTable) -> SpecificPathRelativity:
        return self._lookup(value_definitions).relativity(value_definitions)

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        return self._lookup(value_definitions).exists_pre_sds(value_definitions)

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        prefix = self._lookup(environment.value_definitions).file_path_pre_sds(environment)
        return prefix / self.path_suffix_path(environment.value_definitions)

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        prefix = self._lookup(environment.value_definitions).file_path_post_sds(environment)
        return prefix / self.path_suffix_path(environment.value_definitions)

    def value_references(self) -> list:
        return [self._value_references_of_path] + self.__path_suffix.value_references

    def _lookup(self, symbols: SymbolTable) -> FileRef:
        def_in_symbol_table = symbols.lookup(self._value_references_of_path.name)
        assert isinstance(def_in_symbol_table, ValueContainer), 'Symbol Table is assumed to contain ValueContainer:s'
        value = def_in_symbol_table.value
        if not isinstance(value, FileRefResolver):
            assert isinstance(value, FileRefResolver), 'Referenced ValueContainer must contain a FileRefValue: ' + str(
                value)
        return value.resolve(symbols)


_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_HOME
_NOT_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_ACT


def _relativity_restriction(rel_option_types: set, absolute_is_valid: bool) -> FileRefRelativityRestriction:
    return FileRefRelativityRestriction(PathRelativityVariants(rel_option_types, absolute_is_valid))
