from typing import Sequence

from exactly_lib.symbol.sdv_structure import SymbolReference
from exactly_lib.type_val_deps.dep_variants.ddv import ddv_validation
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.types.string_matcher import StringMatcherSdv
from exactly_lib.type_val_prims.matcher.string_matcher import StringMatcher
from exactly_lib_test.impls.types.matcher.test_resources import sdv_ddv


def string_matcher_sdv_constant_test_impl(resolved_value: StringMatcher,
                                          references: Sequence[SymbolReference] = (),
                                          validator: DdvValidator = ddv_validation.ConstantDdvValidator(),
                                          ) -> StringMatcherSdv:
    return sdv_ddv.MatcherSdvOfConstantDdvTestImpl(
        sdv_ddv.MatcherDdvOfConstantMatcherTestImpl(
            resolved_value,
            validator,
        ),
        references,
    )
