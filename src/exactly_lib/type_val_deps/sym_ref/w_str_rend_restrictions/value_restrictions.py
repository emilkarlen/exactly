from typing import Optional, Sequence

from exactly_lib.common.err_msg.err_msg_w_fix_tip import ErrorMessageWithFixTip
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.symbol import value_type
from exactly_lib.symbol.err_msg import error_messages as err_msg_for_any_type
from exactly_lib.symbol.sdv_structure import SymbolContainer
from exactly_lib.symbol.value_type import ValueType, WithStrRenderingType
from exactly_lib.tcfs.path_relativity import PathRelativityVariants
from exactly_lib.tcfs.relativity_validation import is_satisfied_by
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions import error_messages
from exactly_lib.type_val_deps.sym_ref.w_str_rend_restrictions.data_value_restriction import ValueRestriction
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.util.symbol_table import SymbolTable


def is_string() -> ValueRestriction:
    return ArbitraryValueWStrRenderingRestriction.of_single(WithStrRenderingType.STRING)


class ArbitraryValueWStrRenderingRestriction(ValueRestriction):
    """A restriction on given set of with-str-rendering types."""

    def __init__(self, accepted: Sequence[WithStrRenderingType]):
        self._accepted__w_str_rendering = accepted
        self._accepted = tuple([
            value_type.W_STR_RENDERING_TYPE_2_VALUE_TYPE[t]
            for t in accepted
        ])

    @staticmethod
    def of_single(accepted: WithStrRenderingType) -> ValueRestriction:
        return ArbitraryValueWStrRenderingRestriction(
            (accepted,)
        )

    @staticmethod
    def of_any() -> ValueRestriction:
        return ArbitraryValueWStrRenderingRestriction(tuple(WithStrRenderingType))

    @property
    def accepted(self) -> Sequence[WithStrRenderingType]:
        # Needed for test (2021-02-23) :(
        return self._accepted__w_str_rendering

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        if container.value_type not in self._accepted:
            return err_msg_for_any_type.invalid_type_msg(
                self._accepted,
                symbol_name,
                container)
        return None


class PathAndRelativityRestriction(ValueRestriction):
    """
    Restricts to `PathDdv` and `PathRelativityVariants`
    """

    def __init__(self, accepted: PathRelativityVariants):
        self._accepted = accepted

    def is_satisfied_by(self,
                        symbol_table: SymbolTable,
                        symbol_name: str,
                        container: SymbolContainer) -> Optional[ErrorMessageWithFixTip]:
        sdv = container.sdv
        if not isinstance(sdv, PathSdv):
            return err_msg_for_any_type.invalid_type_msg([ValueType.PATH], symbol_name, container)
        path = sdv.resolve(symbol_table)
        actual_relativity = path.relativity()
        satisfaction = is_satisfied_by(actual_relativity, self._accepted)
        if satisfaction:
            return None
        else:
            msg = error_messages.unsatisfied_path_relativity(symbol_name, container,
                                                             self._accepted,
                                                             actual_relativity)
            return ErrorMessageWithFixTip(text_docs.single_pre_formatted_line_object(msg))

    @property
    def accepted(self) -> PathRelativityVariants:
        return self._accepted
