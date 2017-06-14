import unittest

from exactly_lib.help_texts.test_case.instructions.assign_symbol import PATH_TYPE, STRING_TYPE
from exactly_lib.instructions.multi_phase_instructions.assign_symbol import REL_OPTIONS_CONFIGURATION
from exactly_lib.instructions.setup import assign_symbol as sut
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.symbol.concrete_restrictions import FileRefRelativityRestriction
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolReference
from exactly_lib.symbol.value_resolvers.file_ref_with_symbol import rel_symbol
from exactly_lib.symbol.value_resolvers.path_part_resolvers import PathPartResolverAsFixedPath
from exactly_lib.symbol.value_restriction import ReferenceRestrictions
from exactly_lib.symbol.value_structure import ValueContainer, Value
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.test_case_file_structure import file_refs
from exactly_lib.test_case_file_structure.concrete_path_parts import PathPartAsFixedPath
from exactly_lib.util.line_source import Line
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.symbol.test_resources import value_structure_assertions as vs_asrt
from exactly_lib_test.symbol.test_resources.symbol_utils import assert_symbol_table_is_singleton, \
    string_value_container, file_ref_value, assert_symbol_usages_is_singleton_list
from exactly_lib_test.symbol.test_resources.value_structure_assertions import equals_value_container
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingParseDueToInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFailingParsePerTypeDueToInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestPathFailingParseDueToInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestStringSuccessfulParse))
    ret_val.addTest(unittest.makeSuite(TestPathSuccessfulParse))
    ret_val.addTest(unittest.makeSuite(TestPathAssignmentRelativeSingleValidOption))
    ret_val.addTest(unittest.makeSuite(TestPathAssignmentRelativeSingleDefaultOption))
    ret_val.addTest(unittest.makeSuite(TestPathAssignmentRelativeValueDefinition))
    ret_val.addTest(suite_for_instruction_documentation(sut.setup('instruction name').documentation))
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
            ('not_a_type val_name = value', 'Invalid type name'),
        ]
        setup = sut.setup('instruction-name')
        for (source_str, case_name) in test_cases:
            source = remaining_source(source_str)
            with self.subTest(msg=case_name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    setup.parse(source)


class TestFailingParsePerTypeDueToInvalidSyntax(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('{valid_type} name {valid_value}', 'Missing ='),
            ('{valid_type} "val_name" = {valid_value}', 'VAL-NAME must not be quoted'),
            ('{valid_type} val-name = {valid_value}', 'VAL-NAME must only contain alphanum and _'),
            ('{valid_type} name SuperfluousName = {valid_value}', 'Superfluous name'),
        ]
        type_setups = [
            (PATH_TYPE, '--rel-act f'),
            (STRING_TYPE, 'string-value'),
        ]
        setup = sut.setup('instruction-name')
        for type_name, valid_type_value in type_setups:
            for source_template, test_case_name in test_cases:
                source_str = source_template.format(valid_type=type_name,
                                                    valid_value=valid_type_value)
                source = remaining_source(source_str)
                with self.subTest(msg=test_case_name):
                    with self.assertRaises(SingleInstructionInvalidArgumentException):
                        setup.parse(source)


class TestPathFailingParseDueToInvalidSyntax(unittest.TestCase):
    def runTest(self):
        test_cases = [
            (_src('{path_type} name = --invalid-option x'), 'Invalid file ref syntax'),
            (_src('{path_type} name = --rel-act x superfluous-arg'), 'Superfluous arguments'),
        ]
        setup = sut.setup('instruction-name')
        for (source_str, case_name) in test_cases:
            source = remaining_source(source_str)
            with self.subTest(msg=case_name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    setup.parse(source)


class TestStringSuccessfulParse(TestCaseBaseForParser):
    def runTest(self):
        # ARRANGE #
        test_cases = [
            ('Valid assignment of single word',
             '{string_type} name1 = v1',
             Expectation(
                 symbol_usages=asrt.matches_sequence([
                     vs_asrt.equals_symbol(SymbolDefinition('name1', string_value_container('v1')),
                                           ignore_source_line=True)
                 ]),
                 symbols_after_main=assert_symbol_table_is_singleton(
                     'name1',
                     equals_value_container(string_value_container('v1')),
                 )
             )),
        ]
        for test_case_name, source_template, expectation in test_cases:
            with self.subTest(msg=test_case_name):
                source = _remaining_source(source_template)
                # ACT & ASSERT#
                self._run(source,
                          Arrangement(),
                          expectation)


class TestPathSuccessfulParse(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        setup = sut.setup('instruction-name')
        source = _remaining_source('{path_type} name = --rel-act component')
        # ACT #
        instruction = setup.parse(source)
        # ASSERT #
        self.assertIsInstance(instruction, SetupPhaseInstruction,
                              'Instruction must be an ' + str(SetupPhaseInstruction))


class TestPathAssignmentRelativeSingleValidOption(TestCaseBaseForParser):
    def test(self):
        instruction_argument = _src('{path_type} name = --rel-act component')
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_value = file_ref_value(file_refs.rel_act(PathPartAsFixedPath('component')))
            expected_value_container = _value_container(expected_file_ref_value)
            self._run(source,
                      Arrangement(),
                      Expectation(
                          symbol_usages=assert_symbol_usages_is_singleton_list(
                              vs_asrt.equals_symbol(
                                  SymbolDefinition('name', expected_value_container))),
                          symbols_after_main=assert_symbol_table_is_singleton(
                              'name',
                              equals_value_container(expected_value_container))
                      )
                      )


class TestPathAssignmentRelativeSingleDefaultOption(TestCaseBaseForParser):
    def test(self):
        instruction_argument = _src('{path_type} name = component')
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_value = file_ref_value(
                file_refs.of_rel_option(REL_OPTIONS_CONFIGURATION.default_option,
                                        PathPartAsFixedPath('component')))
            expected_value_container = _value_container(expected_file_ref_value)
            self._run(source,
                      Arrangement(),
                      Expectation(
                          symbol_usages=assert_symbol_usages_is_singleton_list(
                              vs_asrt.equals_symbol(
                                  SymbolDefinition('name', expected_value_container))),
                          symbols_after_main=assert_symbol_table_is_singleton(
                              'name',
                              equals_value_container(expected_value_container)))
                      )


class TestPathAssignmentRelativeValueDefinition(TestCaseBaseForParser):
    def test(self):
        instruction_argument = _src('{path_type} ASSIGNED_NAME = --rel REFERENCED_SYMBOL component')
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_resolver = rel_symbol(
                SymbolReference('REFERENCED_SYMBOL',
                                ReferenceRestrictions(FileRefRelativityRestriction(
                                    REL_OPTIONS_CONFIGURATION.accepted_relativity_variants))),
                PathPartResolverAsFixedPath('component'))
            expected_value_container = _value_container(expected_file_ref_resolver)
            self._run(source,
                      Arrangement(),
                      Expectation(
                          symbol_usages=asrt.matches_sequence([
                              vs_asrt.equals_symbol(
                                  SymbolDefinition('ASSIGNED_NAME',
                                                   expected_value_container),
                                  ignore_source_line=True)
                          ]),
                          symbols_after_main=assert_symbol_table_is_singleton(
                              'ASSIGNED_NAME',
                              equals_value_container(expected_value_container)))
                      )


def _src(s: str) -> str:
    return s.format(
        path_type=PATH_TYPE,
        string_type=STRING_TYPE,
    )


def _remaining_source(s: str) -> ParseSource:
    return remaining_source(_src(s))


def _value_container(value: Value) -> ValueContainer:
    return ValueContainer(Line(1, 'source line'), value)
