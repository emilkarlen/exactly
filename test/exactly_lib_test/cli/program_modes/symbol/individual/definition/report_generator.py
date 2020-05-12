import unittest
from typing import Iterator, Sequence, Optional

from exactly_lib.cli.program_modes.symbol.impl.report import ReportBlock
from exactly_lib.cli.program_modes.symbol.impl.reports import individual as sut, symbol_info
from exactly_lib.cli.program_modes.symbol.impl.reports import value_presentation
from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import DefinitionsResolver, SymbolDefinitionInfo
from exactly_lib.section_document.source_location import SourceLocationInfo
from exactly_lib.symbol import restriction
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.sdv_structure import SymbolReference, SymbolDefinition
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phase_identifier import PhaseEnum
from exactly_lib.test_case_utils.matcher.impls.constant import MatcherWithConstantResult
from exactly_lib.test_case_utils.string_transformer.sdvs import StringTransformerSdvConstant
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.symbol_table import empty_symbol_table
from exactly_lib_test.section_document.test_resources import source_location_assertions as asrt_source_loc
from exactly_lib_test.symbol.data.test_resources import path, list_
from exactly_lib_test.symbol.test_resources import line_matcher, string_matcher, file_matcher, \
    string_transformer, program, string
from exactly_lib_test.symbol.test_resources.string_matcher import StringMatcherSymbolContext
from exactly_lib_test.symbol.test_resources.symbols_setup import SymbolValueContext
from exactly_lib_test.test_case_utils.files_matcher.test_resources import symbol_context as files_matcher_sc
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.type_system.logic.test_resources.string_transformers import MyToUppercaseTransformer
from exactly_lib_test.util.simple_textstruct.test_resources import structure_assertions as asrt_text_struct


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestDefinition),
        unittest.makeSuite(TestReferences),
    ])


class TestDefinition(unittest.TestCase):
    def test(self):
        # ARRANGE #

        symbol_name = 'the_symbol_name'

        for value_context in _VALUE_CONTEXTS_OF_EVERY_TYPE:
            with self.subTest(str(value_context.value_type)):
                symbol_definition = _symbol_definition(symbol_name, value_context)
                definitions_resolver = _ConstantDefinitionsResolver([symbol_definition])

                report_generator = sut.IndividualReportGenerator(symbol_name, False, empty_symbol_table())

                # ACT #

                report = report_generator.generate(definitions_resolver)
                blocks = report.blocks()

                # ASSERT #

                self.assertTrue(report.is_success, 'is success')

                expected_blocks = [
                    _matches_definition_short_info_block(symbol_definition),
                    _matches_definition_source_block(symbol_definition),
                    _is_resolved_value_presentation_block(),
                ]

                expected_blocks_assertion = asrt.matches_sequence(expected_blocks)

                expected_blocks_assertion.apply_with_message(self, blocks, 'blocks')

                _rendered_blocks_are_major_blocks(self, blocks)


class TestReferences(unittest.TestCase):
    def test_symbol_without_references(self):
        # ARRANGE #

        symbol_name = 'the_symbol_name'

        symbol_definition = _symbol_definition(symbol_name, string.ARBITRARY_SYMBOL_VALUE_CONTEXT)
        definitions_resolver = _ConstantDefinitionsResolver([symbol_definition])

        report_generator = sut.IndividualReportGenerator(symbol_name, True, empty_symbol_table())

        # ACT #

        report = report_generator.generate(definitions_resolver)
        blocks = report.blocks()

        # ASSERT #

        self.assertTrue(report.is_success, 'is success')

        expected_blocks = asrt.is_empty_sequence

        expected_blocks.apply_with_message(self, blocks, 'blocks')

        _rendered_blocks_are_major_blocks(self, blocks)

    def test_symbol_with_single_reference(self):
        # ARRANGE #

        referenced_symbol = string.arbitrary_symbol_context('referenced_symbol')

        referencing_symbol = StringMatcherSymbolContext.of_sdv(
            'referencing_symbol',
            string_matcher.string_matcher_sdv_constant_test_impl(
                MatcherWithConstantResult(True),
                [SymbolReference(referenced_symbol.name,
                                 restriction.ValueTypeRestriction(ValueType.STRING))]),
        )

        symbol_definitions = [
            _symbol_definition(referencing_symbol.name, referencing_symbol.value),
            _symbol_definition(referenced_symbol.name, referenced_symbol.value,
                               referencing_symbol.value.sdv.references),
        ]

        definitions_resolver = _ConstantDefinitionsResolver(symbol_definitions)

        report_generator = sut.IndividualReportGenerator(referenced_symbol.name, True, empty_symbol_table())

        # ACT #

        report = report_generator.generate(definitions_resolver)
        blocks = report.blocks()

        # ASSERT #

        self.assertTrue(report.is_success, 'is success')

        expected_blocks = asrt.matches_sequence([
            _matches_reference_source_location_block(referenced_symbol.name),
        ])

        expected_blocks.apply_with_message(self, blocks, 'blocks')

        _rendered_blocks_are_major_blocks(self, blocks)


def _rendered_blocks_are_major_blocks(put: unittest.TestCase, blocks: Sequence[ReportBlock]):
    rendered_blocks = [
        block.render()
        for block in blocks
    ]

    IS_SEQUENCE_OF_MAJOR_BLOCKS.apply_with_message(put, rendered_blocks, 'text blocks')


def _arbitrary_string_transformer() -> StringTransformerSdv:
    return StringTransformerSdvConstant(MyToUppercaseTransformer())


class _ConstantDefinitionsResolver(DefinitionsResolver):
    def __init__(self, constant: Sequence[SymbolDefinitionInfo]):
        self._constant = constant

    def definitions(self) -> Iterator[SymbolDefinitionInfo]:
        return self._constant


def _symbol_definition(name: str,
                       value: SymbolValueContext,
                       references: Sequence[SymbolReference] = ()
                       ) -> SymbolDefinitionInfo:
    return SymbolDefinitionInfo(
        phase_identifier.SETUP,
        SymbolDefinition(
            name,
            value.container,
        ),
        [
            symbol_info.ContextAnd(
                phase_identifier.SETUP,
                _SOURCE_INFO_WITH_SOURCE,
                symbol_reference
            )
            for symbol_reference in references
        ],
    )


def _is_resolved_value_presentation_block() -> ValueAssertion[ReportBlock]:
    return asrt.is_instance(value_presentation.ResolvedValuePresentationBlock)


def _matches_reference_source_location_block(expected_name: str) -> ValueAssertion[ReportBlock]:
    return asrt.is_instance_with__many(
        sut.ReferenceSourceLocationBlock,
        [
            asrt.sub_component('name',
                               _get_reference_block_symbol_name,
                               asrt.equals(expected_name))
        ],
    )


def _matches_definition_short_info_block(expected: SymbolDefinitionInfo) -> ValueAssertion[ReportBlock]:
    return asrt.is_instance_with__many(
        sut.DefinitionShortInfoBlock,
        [
            asrt.sub_component('name',
                               _get_short_info_name,
                               asrt.equals(expected.name()))
        ],
    )


def _matches_definition_source_block(expected: SymbolDefinitionInfo) -> ValueAssertion[ReportBlock]:
    return asrt.is_instance_with__many(
        sut.DefinitionSourceBlock,
        [
            asrt.sub_component(
                'phase',
                _get_source_block_phase_enum,
                asrt.equals(expected.phase.the_enum),
            ),
            asrt.sub_component(
                'source_location_info',
                _get_source_block_source_location_info,
                asrt_source_loc.equals_source_location_info(expected.definition.symbol_container.source_location),
            ),
        ],
    )


def _get_short_info_name(block: sut.DefinitionShortInfoBlock) -> str:
    return block.definition.name()


def _get_source_block_source_location_info(block: sut.DefinitionSourceBlock) -> Optional[SourceLocationInfo]:
    return block.source_location


def _get_source_block_phase_enum(block: sut.DefinitionSourceBlock) -> PhaseEnum:
    return block.phase_if_user_defined_symbol.the_enum


def _get_reference_block_symbol_name(block: sut.ReferenceSourceLocationBlock) -> str:
    return block.reference.value().name


IS_SEQUENCE_OF_MAJOR_BLOCKS = asrt.is_sequence_of(asrt_text_struct.matches_major_block())

_SOURCE_INFO_WITH_SOURCE = symbol_info.SourceInfo.of_lines(
    ['the reference source line']
)

_VALUE_CONTEXTS_OF_EVERY_TYPE = [
    string.ARBITRARY_SYMBOL_VALUE_CONTEXT,
    list_.ARBITRARY_SYMBOL_VALUE_CONTEXT,
    path.ARBITRARY_SYMBOL_VALUE_CONTEXT,

    line_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,
    string_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,
    file_matcher.ARBITRARY_SYMBOL_VALUE_CONTEXT,
    files_matcher_sc.ARBITRARY_SYMBOL_VALUE_CONTEXT,

    string_transformer.ARBITRARY_SYMBOL_VALUE_CONTEXT,
    program.ARBITRARY_SYMBOL_VALUE_CONTEXT,
]
