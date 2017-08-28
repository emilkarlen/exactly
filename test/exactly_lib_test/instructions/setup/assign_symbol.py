import unittest

import exactly_lib.help_texts.type_system
from exactly_lib.instructions.multi_phase_instructions.assign_symbol import REL_OPTIONS_CONFIGURATION
from exactly_lib.instructions.setup import assign_symbol as sut
from exactly_lib.named_element.named_element_usage import NamedElementDefinition, NamedElementReference
from exactly_lib.named_element.symbol import string_resolver as sr, list_resolver as lr
from exactly_lib.named_element.symbol.restrictions.reference_restrictions import \
    ReferenceRestrictionsOnDirectAndIndirect, \
    no_restrictions
from exactly_lib.named_element.symbol.restrictions.value_restrictions import FileRefRelativityRestriction
from exactly_lib.named_element.symbol.value_resolvers.file_ref_resolvers import FileRefConstant
from exactly_lib.named_element.symbol.value_resolvers.file_ref_with_symbol import rel_symbol
from exactly_lib.named_element.symbol.value_resolvers.path_part_resolvers import PathPartResolverAsFixedPath
from exactly_lib.section_document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionInvalidArgumentException
from exactly_lib.test_case.phases.setup import SetupPhaseInstruction
from exactly_lib.test_case_utils.parse.symbol_syntax import SymbolWithReferenceSyntax, symbol, constant
from exactly_lib.type_system_values import file_refs
from exactly_lib.type_system_values.concrete_path_parts import PathPartAsFixedPath
from exactly_lib_test.instructions.multi_phase_instructions.define_named_elem.test_resources import *
from exactly_lib_test.instructions.setup.test_resources.instruction_check import TestCaseBase, Arrangement, \
    Expectation
from exactly_lib_test.instructions.test_resources.check_description import suite_for_instruction_documentation
from exactly_lib_test.instructions.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check
from exactly_lib_test.named_element.symbol.test_resources import symbol_structure_assertions as vs_asrt
from exactly_lib_test.named_element.symbol.test_resources.symbol_structure_assertions import equals_container
from exactly_lib_test.named_element.symbol.test_resources.symbol_usage_assertions import \
    assert_symbol_usages_is_singleton_list
from exactly_lib_test.named_element.symbol.test_resources.symbol_utils import string_constant_container, \
    container
from exactly_lib_test.section_document.test_resources.parse_source import assert_source
from exactly_lib_test.test_case_utils.parse.parse_string import string_resolver_from_fragments
from exactly_lib_test.test_resources.parse import remaining_source
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.util.test_resources.symbol_table_assertions import assert_symbol_table_is_singleton


def suite() -> unittest.TestSuite:
    ret_val = unittest.TestSuite()
    ret_val.addTest(unittest.makeSuite(TestFailingParseDueToInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestFailingParsePerTypeDueToInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestPathFailingParseDueToInvalidSyntax))
    ret_val.addTest(unittest.makeSuite(TestStringSuccessfulParse))
    ret_val.addTest(unittest.makeSuite(TestListSuccessfulParse))
    ret_val.addTest(unittest.makeSuite(TestPathSuccessfulParse))
    ret_val.addTest(unittest.makeSuite(TestPathAssignmentRelativeSingleValidOption))
    ret_val.addTest(unittest.makeSuite(TestPathAssignmentRelativeSingleDefaultOption))
    ret_val.addTest(unittest.makeSuite(TestPathAssignmentRelativeSymbolDefinition))
    ret_val.addTest(suite_for_instruction_documentation(sut.setup('instruction name').documentation))
    return ret_val


class TestCaseBaseForParser(TestCaseBase):
    def _run(self,
             source: ParseSource,
             arrangement: Arrangement,
             expectation: Expectation):
        self._check(sut.setup('instr-name'), source, arrangement, expectation)


class TestFailingParseDueToInvalidSyntax(unittest.TestCase):
    def runTest(self):
        test_cases = [
            ('', 'Empty source'),
            ('not_a_type val_name = value', 'Invalid type name'),
            ('not_a_type val_name = value', 'Invalid type name'),
            ('"not_a_type val_name = value', 'Invalid quoting at beginning of type name'),
            ('{string_type} val_name = va"lue', 'Invalid quoting in value'),
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
            ('{valid_type} name = {valid_value} superfluous argument', 'Superfluous argument'),
        ]
        type_setups = [
            (exactly_lib.help_texts.type_system.PATH_TYPE, '--rel-act f'),
            (exactly_lib.help_texts.type_system.STRING_TYPE, 'string-value'),
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
            (src('{path_type} name = --invalid-option x'), 'Invalid file ref syntax'),
            (src('{path_type} name = --rel-act x superfluous-arg'), 'Superfluous arguments'),
        ]
        setup = sut.setup('instruction-name')
        for (source_str, case_name) in test_cases:
            source = remaining_source(source_str)
            with self.subTest(msg=case_name):
                with self.assertRaises(SingleInstructionInvalidArgumentException):
                    setup.parse(source)


class TestStringSuccessfulParse(TestCaseBaseForParser):
    def test_assignment_of_single_constant_word(self):
        source = single_line_source('{string_type} name1 = v1')
        expected_definition = NamedElementDefinition('name1', string_constant_container('v1'))
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(expected_definition, ignore_source_line=True)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                'name1',
                equals_container(string_constant_container('v1')),
            )
        )
        self._run(source, Arrangement(), expectation)

    def test_assignment_of_single_symbol_reference(self):
        # ARRANGE #
        referred_symbol = SymbolWithReferenceSyntax('referred_symbol')
        name_of_defined_symbol = 'defined_symbol'
        source = single_line_source('{string_type} {name} = {symbol_reference}',
                                    name=name_of_defined_symbol,
                                    symbol_reference=referred_symbol)
        expected_resolver = string_resolver_from_fragments([symbol(referred_symbol.name)])
        container_of_expected_resolver = container(expected_resolver)
        expected_definition = NamedElementDefinition(name_of_defined_symbol,
                                                     container_of_expected_resolver)
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(expected_definition, ignore_source_line=True),
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                name_of_defined_symbol,
                equals_container(container_of_expected_resolver),
            )
        )
        # ACT & ASSERT #
        self._run(source, Arrangement(), expectation)

    def test_assignment_of_single_symbol_reference_syntax_within_hard_quotes(self):
        # ARRANGE #
        referred_symbol = SymbolWithReferenceSyntax('referred_symbol')
        name_of_defined_symbol = 'defined_symbol'
        source = single_line_source('{string_type} {name} = {hard_quote}{symbol_reference}{hard_quote}',
                                    name=name_of_defined_symbol,
                                    hard_quote=HARD_QUOTE_CHAR,
                                    symbol_reference=referred_symbol)
        expected_resolver = string_resolver_from_fragments([constant(str(referred_symbol))])
        container_of_expected_resolver = container(expected_resolver)
        expected_definition = NamedElementDefinition(name_of_defined_symbol,
                                                     container_of_expected_resolver)
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(expected_definition, ignore_source_line=True),
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                name_of_defined_symbol,
                equals_container(container_of_expected_resolver),
            )
        )
        # ACT & ASSERT #
        self._run(source, Arrangement(), expectation)

    def test_assignment_of_symbols_and_constant_text_within_soft_quotes(self):
        # ARRANGE #
        referred_symbol1 = SymbolWithReferenceSyntax('referred_symbol_1')
        referred_symbol2 = SymbolWithReferenceSyntax('referred_symbol_2')
        name_of_defined_symbol = 'defined_symbol'
        source = single_line_source('{string_type} {name} = {soft_quote}{sym_ref1} between {sym_ref2}{soft_quote}',
                                    soft_quote=SOFT_QUOTE_CHAR,
                                    name=name_of_defined_symbol,
                                    sym_ref1=referred_symbol1,
                                    sym_ref2=referred_symbol2)
        expected_resolver = string_resolver_from_fragments([
            symbol(referred_symbol1.name),
            constant(' between '),
            symbol(referred_symbol2.name),
        ])
        container_of_expected_resolver = container(expected_resolver)
        expected_definition = NamedElementDefinition(name_of_defined_symbol,
                                                     container_of_expected_resolver)
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(expected_definition, ignore_source_line=True),
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                name_of_defined_symbol,
                equals_container(container_of_expected_resolver),
            )
        )
        # ACT & ASSERT #
        self._run(source, Arrangement(), expectation)


class TestListSuccessfulParse(TestCaseBaseForParser):
    def test_assignment_of_empty_list(self):
        symbol_name = 'the_symbol_name'
        source = single_line_source('{list_type} {symbol_name} = ',
                                    symbol_name=symbol_name)
        expected_resolver = lr.ListResolver([])
        expected_resolver_container = container(expected_resolver)
        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(NamedElementDefinition(symbol_name, expected_resolver_container),
                                      ignore_source_line=True)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                symbol_name,
                equals_container(expected_resolver_container),
            )
        )
        self._run(source, Arrangement(), expectation)

    def test_assignment_of_list_with_multiple_constant_elements(self):
        symbol_name = 'the_symbol_name'
        value_without_space = 'value_without_space'
        value_with_space = 'value with space'
        source = remaining_source(src(
            '{list_type} {symbol_name} = {value_without_space} {soft_quote}{value_with_space}{soft_quote} ',
            symbol_name=symbol_name,
            value_without_space=value_without_space,
            value_with_space=value_with_space,
        ),
            ['following line'],
        )
        expected_resolver = lr.ListResolver([lr.StringResolverElement(sr.string_constant(value_without_space)),
                                             lr.StringResolverElement(sr.string_constant(value_with_space))])
        expected_resolver_container = container(expected_resolver)

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(NamedElementDefinition(symbol_name, expected_resolver_container),
                                      ignore_source_line=True)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                symbol_name,
                equals_container(expected_resolver_container),
            ),
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
        )
        self._run(source, Arrangement(), expectation)

    def test_assignment_of_list_with_symbol_references(self):
        symbol_name = 'the_symbol_name'
        referred_symbol = SymbolWithReferenceSyntax('referred_symbol')
        source = remaining_source(src(
            '{list_type} {symbol_name} = {symbol_reference} ',
            symbol_name=symbol_name,
            symbol_reference=referred_symbol,
        ),
            ['following line'],
        )
        expected_symbol_reference = NamedElementReference(referred_symbol.name, no_restrictions())
        expected_resolver = lr.ListResolver([lr.SymbolReferenceElement(expected_symbol_reference)])

        expected_resolver_container = container(expected_resolver)

        expectation = Expectation(
            symbol_usages=asrt.matches_sequence([
                vs_asrt.equals_symbol(NamedElementDefinition(symbol_name, expected_resolver_container),
                                      ignore_source_line=True)
            ]),
            symbols_after_main=assert_symbol_table_is_singleton(
                symbol_name,
                equals_container(expected_resolver_container),
            ),
            source=assert_source(current_line_number=asrt.equals(2),
                                 column_index=asrt.equals(0)),
        )
        self._run(source, Arrangement(), expectation)


class TestPathSuccessfulParse(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        setup = sut.setup('instruction-name')
        source = single_line_source('{path_type} name = --rel-act component')
        # ACT #
        instruction = setup.parse(source)
        # ASSERT #
        self.assertIsInstance(instruction, SetupPhaseInstruction,
                              'Instruction must be an ' + str(SetupPhaseInstruction))


class TestPathAssignmentRelativeSingleValidOption(TestCaseBaseForParser):
    def test(self):
        instruction_argument = src('{path_type} name = --rel-act component')
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_resolver = FileRefConstant(file_refs.rel_act(PathPartAsFixedPath('component')))
            expected_container = resolver_container(expected_file_ref_resolver)
            self._run(source,
                      Arrangement(),
                      Expectation(
                          symbol_usages=assert_symbol_usages_is_singleton_list(
                              vs_asrt.equals_symbol(
                                  NamedElementDefinition('name', expected_container))),
                          symbols_after_main=assert_symbol_table_is_singleton(
                              'name',
                              equals_container(expected_container))
                      )
                      )


class TestPathAssignmentRelativeSingleDefaultOption(TestCaseBaseForParser):
    def test(self):
        instruction_argument = src('{path_type} name = component')
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_resolver = FileRefConstant(
                file_refs.of_rel_option(REL_OPTIONS_CONFIGURATION.default_option,
                                        PathPartAsFixedPath('component')))
            expected_container = resolver_container(expected_file_ref_resolver)
            self._run(source,
                      Arrangement(),
                      Expectation(
                          symbol_usages=assert_symbol_usages_is_singleton_list(
                              vs_asrt.equals_symbol(
                                  NamedElementDefinition('name', expected_container))),
                          symbols_after_main=assert_symbol_table_is_singleton(
                              'name',
                              equals_container(expected_container)))
                      )


class TestPathAssignmentRelativeSymbolDefinition(TestCaseBaseForParser):
    def test(self):
        instruction_argument = src('{path_type} ASSIGNED_NAME = --rel REFERENCED_SYMBOL component')
        for source in equivalent_source_variants__with_source_check(self, instruction_argument):
            expected_file_ref_resolver = rel_symbol(
                NamedElementReference('REFERENCED_SYMBOL',
                                      ReferenceRestrictionsOnDirectAndIndirect(FileRefRelativityRestriction(
                                          REL_OPTIONS_CONFIGURATION.accepted_relativity_variants))),
                PathPartResolverAsFixedPath('component'))
            expected_container = resolver_container(expected_file_ref_resolver)
            self._run(source,
                      Arrangement(),
                      Expectation(
                          symbol_usages=asrt.matches_sequence([
                              vs_asrt.equals_symbol(
                                  NamedElementDefinition('ASSIGNED_NAME',
                                                         expected_container),
                                  ignore_source_line=True)
                          ]),
                          symbols_after_main=assert_symbol_table_is_singleton(
                              'ASSIGNED_NAME',
                              equals_container(expected_container)))
                      )
