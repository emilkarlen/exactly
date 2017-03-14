import pathlib
import unittest

from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_relativity import PathRelativityVariants
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds, \
    PathResolvingEnvironmentPreSds, PathResolvingEnvironmentPostSds
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition import symbol_table_contents as sym_tbl
from exactly_lib.value_definition import value_definition_usage as vd
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources import value_definition as vd_tr
from exactly_lib_test.value_definition.test_resources import value_reference as vr_tr


def file_ref_equals(expected: FileRef) -> asrt.ValueAssertion:
    return _FileRefAssertion(expected)


class _FileRefAssertion(asrt.ValueAssertion):
    def __init__(self,
                 expected: FileRef):
        self._expected = expected

    def apply(self,
              put: unittest.TestCase,
              value,
              message_builder: asrt.MessageBuilder = asrt.MessageBuilder()):
        put.assertIsInstance(value, FileRef,
                             'Actual value is expected to be a ' + str(FileRef))
        assert isinstance(value, FileRef)
        put.assertEqual(self._expected.file_name, value.file_name,
                        message_builder.apply('file_name'))
        self._equals_value_references_of_paths(put, message_builder, value)
        environment = self._fake_environment()
        put.assertEqual(self._expected.relativity(environment.value_definitions),
                        value.relativity(environment.value_definitions),
                        message_builder.apply('relativity'))

        expected_exists_pre_sds = self._expected.exists_pre_sds(environment.value_definitions)
        put.assertEqual(expected_exists_pre_sds,
                        value.exists_pre_sds(environment.value_definitions),
                        message_builder.apply('exists_pre_sds'))
        if expected_exists_pre_sds:
            put.assertEqual(self._expected.file_path_pre_sds(environment),
                            value.file_path_pre_sds(environment),
                            message_builder.apply('file_path_pre_sds'))
        else:
            put.assertEqual(self._expected.file_path_post_sds(environment),
                            value.file_path_post_sds(environment),
                            message_builder.apply('file_path_post_sds'))

    def _fake_environment(self) -> PathResolvingEnvironmentPreOrPostSds:
        home_dir_path = pathlib.Path('home')
        sds = SandboxDirectoryStructure('sds')
        return PathResolvingEnvironmentPreOrPostSds(HomeAndSds(home_dir_path, sds),
                                                    self._fake_value_definitions_according_to_expected())

    def _fake_value_definitions_according_to_expected(self) -> SymbolTable:
        elements = {}
        for ref in self._expected.value_references_of_paths():
            assert isinstance(ref, vd.ValueReferenceOfPath)
            elements[ref.name] = file_ref_val_test_impl(ref.valid_relativities)
        return SymbolTable(elements)

    def _equals_value_references_of_paths(self,
                                          put: unittest.TestCase,
                                          message_builder: asrt.MessageBuilder,
                                          actual: FileRef):
        mb = message_builder.for_sub_component('value_references_of_paths')
        put.assertEqual(len(self._expected.value_references_of_paths()),
                        len(actual.value_references_of_paths()),
                        mb.apply('Number of value_references_of_paths'))
        for idx, expected_ref in enumerate(self._expected.value_references_of_paths()):
            actual_ref = actual.value_references_of_paths()[idx]
            put.assertIsInstance(actual_ref, vd.ValueReferenceOfPath)
            vr_tr.equals_value_reference(expected_ref).apply(put, actual_ref,
                                                             mb.for_sub_component('[%d]' % idx))


def file_ref_val_test_impl(valid_relativities: PathRelativityVariants) -> sym_tbl.FileRefValue:
    relativity = list(valid_relativities.rel_option_types)[0]
    assert isinstance(relativity, RelOptionType)
    return vd_tr.file_ref_value(_FileRefTestImpl('file_ref_test_impl', relativity))


def file_ref_test_impl(file_name: str = 'file_ref_test_impl',
                       relativity: RelOptionType = RelOptionType.REL_RESULT) -> FileRef:
    return _FileRefTestImpl(file_name, relativity)


class _FileRefTestImpl(FileRef):
    """
    A dummy FileRef that has a given relativity,
    and is as simple as possible.
    """

    def __init__(self, file_name: str, relativity: RelOptionType):
        super().__init__(file_name)
        self._relativity = relativity

    def relativity(self, value_definitions: SymbolTable) -> RelOptionType:
        return self._relativity

    def value_references_of_paths(self) -> list:
        return []

    def exists_pre_sds(self, value_definitions: SymbolTable) -> bool:
        return self._relativity == RelOptionType.REL_HOME

    def file_path_pre_sds(self, environment: PathResolvingEnvironmentPreSds) -> pathlib.Path:
        return pathlib.Path('_FileRefWithoutValRef-path') / self.file_name

    def file_path_post_sds(self, environment: PathResolvingEnvironmentPostSds) -> pathlib.Path:
        return pathlib.Path('_FileRefWithoutValRef-path') / self.file_name
