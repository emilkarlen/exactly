import itertools
from typing import List, Sequence

from exactly_lib.common.err_msg.definitions import Blocks, single_str_block
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.symbol.data.restrictions.reference_restrictions import FailureOfDirectReference, \
    FailureOfIndirectReference
from exactly_lib.symbol.data.value_restriction import ValueRestrictionFailure
from exactly_lib.symbol.err_msg import error_messages
from exactly_lib.symbol.lookups import lookup_container
from exactly_lib.symbol.resolver_structure import SymbolContainer
from exactly_lib.symbol.restriction import Failure, InvalidTypeCategoryFailure, InvalidValueTypeFailure
from exactly_lib.type_system.value_type import TYPE_CATEGORY_2_VALUE_TYPE_SEQUENCE
from exactly_lib.util.simple_textstruct.rendering import renderer_combinators, blocks, line_objects
from exactly_lib.util.simple_textstruct.rendering.renderer import Renderer
from exactly_lib.util.simple_textstruct.structure import MajorBlock
from exactly_lib.util.symbol_table import SymbolTable


class ErrorMessage(Renderer[Sequence[MajorBlock]]):
    def __init__(self,
                 failing_symbol: str,
                 symbols: SymbolTable,
                 failure: Failure):
        self._failing_symbol = failing_symbol
        self._symbols = symbols
        self._failure = failure

    def render(self) -> Sequence[MajorBlock]:
        failure = self._failure
        if isinstance(failure, FailureOfDirectReference):
            return ErrorMessageForDirectReference(failure.error).render()
        elif isinstance(failure, FailureOfIndirectReference):
            return self._of_indirect(failure)
        elif isinstance(failure, InvalidTypeCategoryFailure):
            return self._of_invalid_type_category(failure)
        elif isinstance(failure, InvalidValueTypeFailure):
            return self._of_invalid_value_type(failure)
        else:
            raise TypeError('Unknown type of {}: {}'.format(str(Failure),
                                                            str(failure)))

    def _of_indirect(self, failure: FailureOfIndirectReference) -> Sequence[MajorBlock]:
        return _of_indirect(self._failing_symbol,
                            self._symbols,
                            failure).render()

    def _of_invalid_type_category(self, failure: InvalidTypeCategoryFailure) -> Sequence[MajorBlock]:
        value_restriction_failure = error_messages.invalid_type_msg(
            TYPE_CATEGORY_2_VALUE_TYPE_SEQUENCE[failure.expected],
            self._failing_symbol,
            lookup_container(self._symbols,
                             self._failing_symbol))

        return _render_vrf(value_restriction_failure)

    def _of_invalid_value_type(self, failure: InvalidValueTypeFailure) -> Sequence[MajorBlock]:
        value_restriction_failure = error_messages.invalid_type_msg(
            [failure.expected],
            self._failing_symbol,
            lookup_container(self._symbols,
                             self._failing_symbol)
        )

        return _render_vrf(value_restriction_failure)


class ErrorMessageForDirectReference(Renderer[Sequence[MajorBlock]]):
    def __init__(self, error: ValueRestrictionFailure):
        self._error = error

    def render(self) -> Sequence[MajorBlock]:
        return _render_vrf(self._error)


def _of_indirect(failing_symbol: str,
                 symbols: SymbolTable,
                 failure: FailureOfIndirectReference) -> TextRenderer:
    major_blocks_sequence = []

    if failure.meaning_of_failure:
        major_blocks_sequence.append(
            blocks.MajorBlocksOfSingleLineObject(
                line_objects.StringLineObject(failure.meaning_of_failure)
            )
        )

    error = failure.error

    major_blocks_sequence.append(error.message)

    major_blocks_sequence.append(
        _path_to_failing_symbol__tr(failing_symbol,
                                    failure.path_to_failing_symbol,
                                    symbols)
    )

    if error.how_to_fix is not None:
        major_blocks_sequence.append(error.how_to_fix)

    return renderer_combinators.ConcatenationR(major_blocks_sequence)


def _path_to_failing_symbol(failing_symbol: str,
                            path_to_failing_symbol: List[str],
                            symbols: SymbolTable) -> Blocks:
    def line_ref_of_symbol(symbol_name: str) -> Blocks:
        container = symbols.lookup(symbol_name)
        assert isinstance(container, SymbolContainer), 'Only known type of SymbolTableValue'
        return error_messages._builtin_or_user_defined_source_blocks(container.source_location)

    path_to_failing_symbol = [failing_symbol] + path_to_failing_symbol

    ret_val = [
        single_str_block('Referenced via')
    ]

    ret_val += itertools.chain.from_iterable(map(line_ref_of_symbol, path_to_failing_symbol))

    return ret_val


def _path_to_failing_symbol__tr(failing_symbol: str,
                                path_to_failing_symbol: List[str],
                                symbols: SymbolTable) -> TextRenderer:
    return text_docs.major_blocks_of_string_blocks(
        _path_to_failing_symbol(failing_symbol,
                                path_to_failing_symbol,
                                symbols))


def _render_vrf(vrf: ValueRestrictionFailure) -> Sequence[MajorBlock]:
    ret_val = list(vrf.message.render())
    if vrf.how_to_fix is not None:
        ret_val += vrf.how_to_fix.render()

    return ret_val
