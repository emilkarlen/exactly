from typing import Sequence

from exactly_lib.impls.types.matcher.impls import constant, ddv_components
from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator, ConstantDdvValidator
from exactly_lib.type_val_deps.types.line_matcher import LineMatcherSdv, LineMatcherDdv
from exactly_lib.type_val_prims.matcher.line_matcher import LineMatcherLine
from exactly_lib.type_val_prims.matcher.matcher_base_class import MatcherWTrace
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv


def successful_matcher_with_validation(validator: DdvValidator) -> LineMatcherSdv:
    return sdv_ddv.sdv_from_primitive_value(
        constant.MatcherWithConstantResult(True),
        (),
        validator,
    )


def sdv_from_primitive_value(
        primitive_value: MatcherWTrace[LineMatcherLine] = constant.MatcherWithConstantResult(True),
        references: Sequence[SymbolReference] = (),
        validator: DdvValidator = ConstantDdvValidator.new_success(),
) -> LineMatcherSdv:
    return sdv_ddv.sdv_from_primitive_value(
        primitive_value,
        references,
        validator,
    )


def ddv_of_unconditionally_matching_matcher() -> LineMatcherDdv:
    return ddv_components.MatcherDdvFromConstantPrimitive(
        constant.MatcherWithConstantResult(False)
    )
