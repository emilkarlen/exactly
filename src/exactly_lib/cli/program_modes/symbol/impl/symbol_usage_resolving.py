import itertools

from typing import List, Sequence, Iterator, Dict, Callable, Optional

from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import SYMBOL_INFO, SymbolDefinitionInfo, \
    DefinitionsResolver, ContextAnd, SourceInfo
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolUsage, SymbolReference, SymbolUsageVisitor
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.test_case.phases import setup, before_assert, assert_, cleanup
from exactly_lib.test_case.phases.act import ActPhaseInstruction
from exactly_lib.test_case.test_case_doc import TestCaseOfInstructions, ElementWithSourceLocation


class DefinitionsInfoResolverFromTestCase(DefinitionsResolver):
    def __init__(self,
                 test_case: TestCaseOfInstructions,
                 act_phase: Sequence[SymbolUsage]):
        self.test_case = test_case
        self.act_phase = act_phase

    def definitions(self) -> Iterator[SymbolDefinitionInfo]:
        usages = list(self.symbol_usages())
        references = self.references(usages)

        def mk_definition(definition: ContextAnd[SymbolDefinition]) -> SymbolDefinitionInfo:
            name = definition.value().name

            references_to_symbol = references.get(name, [])

            return SymbolDefinitionInfo(definition.phase(),
                                        definition.value(),
                                        references_to_symbol)

        return map(mk_definition,
                   filter(is_not_none,
                          map(_extract_symbol_definition, usages))
                   )

    def symbol_usages(self) -> Iterator[ContextAnd[SymbolUsage]]:
        return itertools.chain.from_iterable([
            _symbol_usages_from(phase_identifier.SETUP,
                                self.test_case.setup_phase, setup.get_symbol_usages),
            self._act_phase_symbol_usages(),
            _symbol_usages_from(phase_identifier.BEFORE_ASSERT,
                                self.test_case.before_assert_phase,
                                before_assert.get_symbol_usages),
            _symbol_usages_from(phase_identifier.ASSERT,
                                self.test_case.assert_phase, assert_.get_symbol_usages),
            _symbol_usages_from(phase_identifier.CLEANUP,
                                self.test_case.cleanup_phase, cleanup.get_symbol_usages),
        ])

    def _act_phase_symbol_usages(self) -> Iterator[ContextAnd[SymbolUsage]]:
        usages_extractor = _UsagesExtractor()
        source_info = self._act_phase_source_info()

        def mk_act_phase_sym_usage(usage: SymbolUsage) -> ContextAnd[SymbolUsage]:
            return ContextAnd(phase_identifier.ACT,
                              source_info,
                              usage)

        return map(
            mk_act_phase_sym_usage,
            itertools.chain.from_iterable([
                usages_extractor.visit(symbol_usage)
                for symbol_usage in self.act_phase
            ])
        )

    def _act_phase_source_info(self) -> SourceInfo:
        def instruction_source_lines(instruction: ElementWithSourceLocation[ActPhaseInstruction]) -> Sequence[str]:
            return instruction.value.source_code().lines

        source_lines = list(
            itertools.chain.from_iterable(
                map(instruction_source_lines, self.test_case.act_phase)
            )
        )

        if source_lines:
            return SourceInfo.of_lines(source_lines)
        else:
            return SourceInfo.empty()

    @staticmethod
    def references(usages: List[ContextAnd[SymbolUsage]]
                   ) -> Dict[str, List[ContextAnd[SymbolReference]]]:
        context_and_reference_iter = filter(
            is_not_none,
            map(_extract_symbol_reference, usages)
        )
        ret_val = {}
        for context_and_reference in context_and_reference_iter:
            name = context_and_reference.value().name
            refs_for_name = ret_val.setdefault(name, [])
            refs_for_name.append(context_and_reference)

        return ret_val


def _symbol_usages_from(phase: Phase,
                        elements: Sequence[ElementWithSourceLocation[SYMBOL_INFO]],
                        symbol_usages_getter: Callable[[SYMBOL_INFO], Sequence[SymbolUsage]]
                        ) -> Iterator[ContextAnd[SymbolUsage]]:
    usages_extractor = _UsagesExtractor()

    def get_direct_and_indirect_symbol_usages(symbol_info: SYMBOL_INFO) -> Iterator[SymbolUsage]:
        return itertools.chain.from_iterable(
            usages_extractor.visit(symbol_usage)
            for symbol_usage in symbol_usages_getter(symbol_info)
        )

    symbol_usages_sequence_list = [
        [
            ElementWithSourceLocation(
                element.source_location_info,
                symbol_usage
            )
            for symbol_usage in get_direct_and_indirect_symbol_usages(element.value)

        ]
        for element in elements
    ]

    def mk_item(element: ElementWithSourceLocation[SymbolUsage]) -> ContextAnd[SymbolUsage]:
        return ContextAnd(phase,
                          SourceInfo.of_location_info(element.source_location_info),
                          element.value)

    return map(mk_item,
               itertools.chain.from_iterable(symbol_usages_sequence_list)
               )


def _extract_symbol_definition(usage: ContextAnd[SymbolUsage]) -> Optional[ContextAnd[SymbolDefinition]]:
    value = usage.value()
    if isinstance(value, SymbolDefinition):
        return ContextAnd(usage.phase(),
                          usage.source_info(),
                          value)
    else:
        return None


def _extract_symbol_reference(context_and_usage: ContextAnd[SymbolUsage]) -> Optional[ContextAnd[SymbolReference]]:
    usage = context_and_usage.value()
    if isinstance(usage, SymbolReference):
        return ContextAnd(context_and_usage.phase(),
                          context_and_usage.source_info(),
                          usage)
    else:
        return None


def is_not_none(x) -> bool:
    return x is not None


class _UsagesExtractor(SymbolUsageVisitor):
    def _visit_definition(self, definition: SymbolDefinition) -> List[SymbolUsage]:
        return [definition] + list(definition.references)

    def _visit_reference(self, reference: SymbolReference) -> List[SymbolUsage]:
        return [
            reference
        ]
