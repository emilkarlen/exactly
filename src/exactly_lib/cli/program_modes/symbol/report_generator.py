import itertools

import functools
from typing import TypeVar, Sequence, Callable, List, Iterator, Generic, Optional, Dict

from exactly_lib.cli.program_modes.symbol.completion_reporter import CompletionReporter
from exactly_lib.definitions.test_case.instructions.define_symbol import ANY_TYPE_INFO_DICT
from exactly_lib.symbol.symbol_usage import SymbolDefinition, SymbolUsage, SymbolReference, SymbolUsageVisitor
from exactly_lib.test_case import phase_identifier
from exactly_lib.test_case import test_case_doc
from exactly_lib.test_case.phase_identifier import Phase
from exactly_lib.test_case.phases import assert_, before_assert, cleanup, setup
from exactly_lib.test_case.test_case_doc import TestCaseOfInstructions
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.std import StdOutputFiles
from exactly_lib.util.string import lines_content

_A = TypeVar('_A')


class SymUsageInPhase(Generic[_A]):
    def __init__(self, phase: Phase, value: _A):
        self._phase = phase
        self._value = value

    def value(self) -> _A:
        return self._value

    def phase(self) -> Phase:
        return self._phase


class _SymbolDefinitionInfo:
    def __init__(self,
                 definition: SymbolDefinition,
                 references: List[SymUsageInPhase[SymbolDefinition]]):
        self.definition = definition
        self.references = references
        self._num_refs_str = format_num_refs_info(self)

    def name(self) -> str:
        return self.definition.name

    def name_length(self) -> int:
        return len(self.definition.name)

    def value_type(self) -> ValueType:
        return self.definition.resolver_container.resolver.value_type

    def type_identifier(self) -> str:
        return ANY_TYPE_INFO_DICT[self.value_type()].identifier

    def num_refs_str(self) -> str:
        return self._num_refs_str

    def num_refs_str_length(self) -> int:
        return len(self._num_refs_str)


def format_num_refs_info(symbol: _SymbolDefinitionInfo) -> str:
    return '(' + str(len(symbol.references)) + ')'


class _TypeReportingInfo:
    def __init__(self, value_type: ValueType):
        self.type_info = ANY_TYPE_INFO_DICT[value_type]
        self.identifier_length = len(self.type_info.identifier)
        self.identifier = self.type_info.identifier


class ReportGenerator:
    def __init__(self,
                 output: StdOutputFiles,
                 completion_reporter: CompletionReporter,
                 test_case: test_case_doc.TestCaseOfInstructions,
                 act_phase: Sequence[SymbolUsage]):
        self._output = output
        self._completion_reporter = completion_reporter
        self._act_phase = act_phase
        self._test_case_instructions = test_case
        self._type_info_dict = {
            value_type: _TypeReportingInfo(value_type)
            for value_type in ValueType
        }

    def list(self) -> int:
        definitions_resolver = DefinitionsInfoResolver(self._test_case_instructions,
                                                       self._act_phase)
        output_lines = self._get_list_lines(definitions_resolver.definitions())
        self._output.out.write(lines_content(output_lines))
        return self._completion_reporter.report_success()

    def _get_list_lines(self, symbols: Iterator[_SymbolDefinitionInfo]) -> List[str]:
        symbol_list = list(symbols)
        symbol_line_formatter = self._symbol_line_formatter(symbol_list)
        return [
            symbol_line_formatter(symbol)
            for symbol in symbol_list
        ]

    def _symbol_line_formatter(self, symbols: List[_SymbolDefinitionInfo]) -> Callable[[_SymbolDefinitionInfo], str]:
        def get_identifier_length(symbol: _SymbolDefinitionInfo) -> int:
            return self._type_info_dict[symbol.value_type()].identifier_length

        max_type_identifier_len = functools.reduce(_max_int,
                                                   map(get_identifier_length, symbols),
                                                   0)
        max_num_refs_len = functools.reduce(_max_int,
                                            map(_SymbolDefinitionInfo.num_refs_str_length, symbols),
                                            0)

        type_formatting_string = '%-{}s %-{}s'.format(max_type_identifier_len,
                                                      max_num_refs_len)

        def ret_val(symbol: _SymbolDefinitionInfo) -> str:
            return (type_formatting_string % (symbol.type_identifier(),
                                              symbol.num_refs_str()) +
                    ' ' +
                    symbol.name()
                    )

        return ret_val


class DefinitionsInfoResolver:
    def __init__(self,
                 test_case: TestCaseOfInstructions,
                 act_phase: Sequence[SymbolUsage]):
        self.test_case = test_case
        self.act_phase = act_phase

    def definitions(self) -> Iterator[_SymbolDefinitionInfo]:
        usages = list(self.symbol_usages())
        references = self.references(usages)

        def mk_definition(definition: SymUsageInPhase[SymbolDefinition]) -> _SymbolDefinitionInfo:
            name = definition.value().name

            references_to_symbol = []
            if name in references:
                references_to_symbol = references[name]

            return _SymbolDefinitionInfo(definition.value(),
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
                        elements: Sequence[_A],
                        symbol_usages_getter: Callable[[_A], Sequence[SymbolUsage]]
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


def _max_int(x: int, y: int) -> int:
    return max(x, y)


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
