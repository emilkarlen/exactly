import pathlib
import unittest

from exactly_lib.test_case_file_structure.file_ref import FileRef
from exactly_lib.test_case_file_structure.file_ref_relativity import PathRelativityVariants
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_resolving_environment import PathResolvingEnvironmentPreOrPostSds
from exactly_lib.test_case_file_structure.relativity_root import RelOptionType
from exactly_lib.test_case_file_structure.sandbox_directory_structure import SandboxDirectoryStructure
from exactly_lib.util.line_source import Line
from exactly_lib.util.symbol_table import SymbolTable
from exactly_lib.value_definition import value_structure as vs
from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.value_definition.concrete_values import FileRefValue
from exactly_lib.value_definition.value_structure import ValueReference, ValueContainer
from exactly_lib_test.test_case_file_structure.test_resources.simple_file_ref import file_ref_test_impl
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources import value_structure_assertions as vs_tr
from exactly_lib_test.value_definition.test_resources.concrete_restriction_assertion import \
    equals_file_ref_relativity_restriction
from exactly_lib_test.value_definition.test_resources.value_definition_utils import file_ref_value


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
            assert isinstance(ref, vs.ValueReference)
            value_restriction = ref.value_restriction
            assert isinstance(value_restriction, FileRefRelativityRestriction)
            elements[ref.name] = _value_container(file_ref_val_test_impl(value_restriction.accepted))
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
            put.assertIsInstance(actual_ref, ValueReference)
            assert isinstance(actual_ref, ValueReference)
            assert isinstance(expected_ref, ValueReference)
            expected_value_restriction = expected_ref.value_restriction
            assert isinstance(expected_value_restriction, FileRefRelativityRestriction)
            vs_tr.equals_value_reference(expected_ref.name,
                                         equals_file_ref_relativity_restriction(expected_value_restriction)
                                         ).apply(put, actual_ref,
                                                 mb.for_sub_component('[%d]' % idx))


def file_ref_val_test_impl(valid_relativities: PathRelativityVariants) -> FileRefValue:
    relativity = list(valid_relativities.rel_option_types)[0]
    assert isinstance(relativity, RelOptionType)
    return file_ref_value(file_ref_test_impl('file_ref_test_impl', relativity))


def _value_container(value: FileRefValue) -> ValueContainer:
    return ValueContainer(Line(1, 'source line'), value)
