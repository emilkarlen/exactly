import unittest

from exactly_lib.instructions.multi_phase_instructions.assign_value_definition import REL_OPTIONS_CONFIGURATION
from exactly_lib.instructions.setup import assign_value_definition as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.util.line_source import Line
from exactly_lib.value_definition.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.value_definition.file_ref_with_val_def import rel_value_definition
from exactly_lib.value_definition.value_structure import ValueDefinition2, ValueContainer, Value, ValueReference2
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.value_definition.test_resources import value_structure_assertions as vs_asrt
from exactly_lib_test.value_definition.test_resources import values2 as v2
from exactly_lib_test.value_definition.test_resources.value_structure_assertions import equals_value_container
from exactly_lib_test.value_definition.test_resources.values2 import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingParseDueToInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestSuccessfulParse))
    ret_val.addTest(unittest.makeSuite(TestAssignmentRelativeSingleValidOption))
    ret_val.addTest(unittest.makeSuite(TestAssignmentRelativeSingleDefaultOption))
    ret_val.addTest(unittest.makeSuite(TestAssignmentRelativeValueDefinition))
    return ret_val


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: ParseSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.Parser(), source, arrangement, expectation)


class TestFailingParseDueToInvalidSyntax(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('', 'Empty source'),
            ('val_name', 'Only VAL-NAME'),
            ('val_name --rel-home x', 'Missing ='),
            ('"val_name" = --rel-act x', 'VAL-NAME must not be quoted'),
            ('name = --rel-act x superfluous-arg', 'Superfluous arguments'),
            ('name SuperfluousName = --rel-act x', 'Superfluous name'),
        ]
        setup = sut.setup('instruction-name')
        for (source_str, case_name) in test_cases:
            source = remaining_source(source_str)
            with self.subTest(msg=case_name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    setup.parse(source)


class TestSuccessfulParse(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        setup = sut.setup('instruction-name')
        source = remaining_source('name = --rel-act component')
        # ACT #
        instruction = setup.parse(source)
        # ASSERT #
        self.assertIsInstance(instruction, SetupPhaseInstruction,
                              'Instruction must be an ' + str(SetupPhaseInstruction))


class TestAssignmentRelativeSingleValidOption(TestCaseBaseForParser):
    def test(self):
        instruction_argument = 'name = --rel-act component'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_value = v2.file_ref_value(file_refs.rel_act('component'))
            expected_value_container = _value_container(expected_file_ref_value)
            self._run(source,
                      Arrangement(),
                      Expectation(
                          value_definition_usages=v2.assert_value_usages_is_singleton_list(
                              vs_asrt.equals_value_definition(
                                  ValueDefinition2('name', expected_value_container))),
                          value_definitions_after_main=assert_symbol_table_is_singleton(
                              'name',
                              equals_value_container(expected_value_container))
                      )
                      )


class TestAssignmentRelativeSingleDefaultOption(TestCaseBaseForParser):
    def test(self):
        instruction_argument = 'name = component'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_value = v2.file_ref_value(
                file_refs.of_rel_option(REL_OPTIONS_CONFIGURATION.default_option,
                                        'component'))
            expected_value_container = _value_container(expected_file_ref_value)
            self._run(source,
                      Arrangement(),
                      Expectation(
                          value_definition_usages=v2.assert_value_usages_is_singleton_list(
                              vs_asrt.equals_value_definition(
                                  ValueDefinition2('name', expected_value_container))),
                          value_definitions_after_main=assert_symbol_table_is_singleton(
                              'name',
                              equals_value_container(expected_value_container)))
                      )


class TestAssignmentRelativeValueDefinition(TestCaseBaseForParser):
    def test(self):
        instruction_argument = 'ASSIGNED_NAME = --rel REFERENCED_VAL_DEF component'
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_value = v2.file_ref_value(
                rel_value_definition(
                    ValueReference2('REFERENCED_VAL_DEF',
                                    FileRefRelativityRestriction(
                                        REL_OPTIONS_CONFIGURATION.accepted_relativity_variants)),
                    'component'))
            expected_value_container = _value_container(expected_file_ref_value)
            self._run(source,
                      Arrangement(),
                      Expectation(
                          value_definition_usages=asrt.matches_sequence([
                              vs_asrt.equals_value_definition(
                                  ValueDefinition2('ASSIGNED_NAME',
                                                   expected_value_container),
                                  ignore_source_line=True)
                          ]),
                          value_definitions_after_main=assert_symbol_table_is_singleton(
                              'ASSIGNED_NAME',
                              equals_value_container(expected_value_container)))
                      )


def _value_container(value: Value) -> ValueContainer:
    return ValueContainer(Line(1, 'source line'), value)
