import itertools

from typing import List, Sequence, Iterator, Dict, Callable, Optional

from exactly_lib.cli.program_modes.symbol.impl.reports.symbol_info import SYMBOL_INFO, SymUsageInPhase, \
    SymbolDefinitionInfo, DefinitionsResolver
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolUsage, SymbolReference, SymbolUsageVisitor
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.test_case.phases import setup, before_assert, assert_, cleanup
from exactly_lib.test_case.test_case_doc import TestCaseOfInstructions


class DefinitionsInfoResolverFromTestCase(DefinitionsResolver):
    def __init__(self,
                 test_case: TestCaseOfInstructions,
                 act_phase: Sequence[SymbolUsage]):
        self.test_case = test_case
        self.act_phase = act_phase

    def definitions(self) -> Iterator[SymbolDefinitionInfo]:
        usages = list(self.symbol_usages())
        references = self.references(usages)

        def mk_definition(definition: SymUsageInPhase[SymbolDefinition]) -> SymbolDefinitionInfo:
            name = definition.value().name

            references_to_symbol = []
            if name in references:
                references_to_symbol = references[name]

            return SymbolDefinitionInfo(definition.value(),
                                        references_to_symbol)

        return map(mk_definition,
                   filter(is_not_none,
                          map(_extract_symbol_definition, usages))
                   )

    def symbol_usages(self) -> Iterator[SymUsageInPhase[SymbolUsage]]:
        def mk_act_phase_sym_usage(usage: SymbolUsage) -> SymUsageInPhase[SymbolUsage]:
            return SymUsageInPhase(phase_identifier.ACT,
                                   usage)

        return itertools.chain.from_iterable([
            _symbol_usages_from(phase_identifier.SETUP,
                                self.test_case.setup_phase, setup.get_symbol_usages),
            map(mk_act_phase_sym_usage, self.act_phase),
            _symbol_usages_from(phase_identifier.BEFORE_ASSERT,
                                self.test_case.before_assert_phase,
                                before_assert.get_symbol_usages),
            _symbol_usages_from(phase_identifier.ASSERT,
                                self.test_case.assert_phase, assert_.get_symbol_usages),
            _symbol_usages_from(phase_identifier.CLEANUP,
                                self.test_case.cleanup_phase, cleanup.get_symbol_usages),
        ])

    def references(self, usages: List[SymUsageInPhase[SymbolUsage]]
                   ) -> Dict[str, List[SymUsageInPhase[SymbolReference]]]:
        references = itertools.chain.from_iterable(
            map(_extract_symbol_references, usages)
        )
        ret_val = {}
        for reference in references:
            name = reference.value().name
            if name in ret_val:
                ret_val[name].append(reference)
            else:
                ret_val[name] = [reference]

        return ret_val


def _symbol_usages_from(phase: Phase,
                        elements: Sequence[SYMBOL_INFO],
                        symbol_usages_getter: Callable[[SYMBOL_INFO], Sequence[SymbolUsage]]
                        ) -> Iterator[SymUsageInPhase[SymbolUsage]]:
    symbol_usages_sequence_list = [
        symbol_usages_getter(element)
        for element in elements
    ]

    def mk_item(usage: SymbolUsage) -> SymUsageInPhase[SymbolUsage]:
        return SymUsageInPhase(phase, usage)

    return map(mk_item,
               itertools.chain.from_iterable(symbol_usages_sequence_list)
               )


def _extract_symbol_definition(usage: SymUsageInPhase[SymbolUsage]) -> Optional[SymUsageInPhase[SymbolDefinition]]:
    value = usage.value()
    if isinstance(value, SymbolDefinition):
        return SymUsageInPhase(usage.phase(),
                               value)
    else:
        return None


def _extract_symbol_references(usage: SymUsageInPhase[SymbolUsage]) -> List[SymUsageInPhase[SymbolReference]]:
    return _ReferencesExtractor(usage.phase()).visit(usage.value())


def is_not_none(x) -> bool:
    return x is not None


class _ReferencesExtractor(SymbolUsageVisitor):
    def __init__(self, phase: Phase):
        self._phase = phase

    def _visit_definition(self, definition: SymbolDefinition):
        return [
            self._of(reference)
            for reference in definition.references
        ]

    def _visit_reference(self, reference: SymbolReference) -> List[SymUsageInPhase[SymbolReference]]:
        return [
            self._of(reference)
        ]

    def _of(self, reference: SymbolReference) -> SymUsageInPhase[SymbolReference]:
        return SymUsageInPhase(self._phase,
                               reference)
