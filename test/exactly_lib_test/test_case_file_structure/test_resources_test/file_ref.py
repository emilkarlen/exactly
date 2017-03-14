import pathlib
import unittest

from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_relativity import RelOptionType, PathRelativityVariants
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreSds, \
    PathResolvingEnvironmentPostSds
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition import symbol_table_contents as sym_tbl
from exactly_lib.value_definition import value_definition_usage as vd
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
            (_FileRefWithValRef(vd.ValueReferenceOfPath('reffed-name',
                                                        PathRelativityVariants({RelOptionType.REL_ACT}, False)),
                                'file-name'),
             'NOT Exists pre SDS'
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
        expected = _FileRefWithValRef(vd.ValueReferenceOfPath('reffed-name',
                                                              PathRelativityVariants({RelOptionType.REL_ACT}, False)),
                                      'file-name')
        actual = _FileRefWithValRef(vd.ValueReferenceOfPath('reffed-name',
                                                            PathRelativityVariants({RelOptionType.REL_HOME}, False)),
                                    'file-name')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__no_value_refs__value_refs(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRef(vd.ValueReferenceOfPath('reffed-name',
                                                              PathRelativityVariants({RelOptionType.REL_HOME}, False)),
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
        actual = _FileRefWithValRef(vd.ValueReferenceOfPath('reffed-name',
                                                            PathRelativityVariants({RelOptionType.REL_HOME}, False)),
                                    'file-name')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__value_refs_rel_option_types(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRef(vd.ValueReferenceOfPath('reffed-name',
                                                              PathRelativityVariants({RelOptionType.REL_CWD}, False)),
                                      'file-name')
        actual = _FileRefWithValRef(vd.ValueReferenceOfPath('reffed-name',
                                                            PathRelativityVariants({RelOptionType.REL_HOME}, False)),
                                    'file-name')
        # ACT & ASSERT #
        with put.assertRaises(TestException):
            sut.file_ref_equals(expected).apply_with_message(put, actual, 'NotEquals')

    def test_differs__value_refs_name(self):
        # ARRANGE #
        put = test_case_with_failure_exception_set_to_test_exception()
        expected = _FileRefWithValRef(vd.ValueReferenceOfPath('reffed-name',
                                                              PathRelativityVariants({RelOptionType.REL_CWD}, False)),
                                      'file-name')
        actual = _FileRefWithValRef(vd.ValueReferenceOfPath('OTHER-reffed-name',
                                                            PathRelativityVariants({RelOptionType.REL_CWD}, False)),
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
        super().__init__(file_name)
        self._relativity = relativity

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        return self._relativity

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        return self.relativity == RelOptionType.REL_HOME

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return pathlib.Path(str(self.relativity)) / self.file_name

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        return pathlib.Path(str(self.relativity)) / self.file_name

    def value_references_of_paths(self) -> list:
        return []


class _FileRefWithValRef(FileRef):
    """
    A dummy FileRef that has a given relativity,
    and is as simple as possible.
    """

    def __init__(self,
                 value_references_of_path: vd.ValueReferenceOfPath,
                 file_name: str):
        super().__init__(file_name)
        self._value_references_of_path = value_references_of_path

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
        assert isinstance(def_in_symbol_table, sym_tbl.FileRefValue)
        return def_in_symbol_table.file_ref


_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_HOME
_NOT_EXISTS_PRE_SDS_RELATIVITY = RelOptionType.REL_ACT
