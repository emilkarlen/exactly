from typing import Sequence

from exactly_lib.impls.types.string_source import sdvs
from exactly_lib.tcfs.path_relativity import RelOptionType
from exactly_lib.type_val_deps.types.path import path_ddvs
from exactly_lib.type_val_deps.types.path.path_sdv_impls import constant
from exactly_lib.type_val_deps.types.string_source.sdv import StringSourceSdv
from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib_test.impls.types.string_source.test_resources import abstract_syntaxes
from exactly_lib_test.impls.types.test_resources import validation
from exactly_lib_test.impls.types.test_resources.validation import ValidationAssertions
from exactly_lib_test.type_val_deps.types.path.test_resources import abstract_syntaxes as path_abs_stx
from exactly_lib_test.type_val_deps.types.string_source.test_resources.abstract_syntax import StringSourceAbsStx


class ValidationCase:
    def __init__(self,
                 syntax: StringSourceAbsStx,
                 sdv: StringSourceSdv,
                 expectation: ValidationAssertions,
                 ):
        self.syntax = syntax
        self.sdv = sdv
        self._expectation = expectation

    @property
    def expectation(self) -> ValidationAssertions:
        return self._expectation


def failing_validation_cases() -> Sequence[NameAndValue[ValidationCase]]:
    name_of_non_existing_file = 'non-existing-string-source-file'

    def validation_case(relativity: RelOptionType,
                        expectation: validation.Expectation) -> ValidationCase:
        return ValidationCase(
            abstract_syntaxes.StringSourceOfFileAbsStx(
                path_abs_stx.RelOptPathAbsStx(relativity,
                                              name_of_non_existing_file)
            ),
            sdvs.PathStringSourceSdv(
                constant.PathConstantSdv(
                    path_ddvs.of_rel_option(
                        relativity,
                        path_ddvs.constant_path_part(name_of_non_existing_file),
                    ),
                )
            ),
            validation.ValidationAssertions.of_expectation(expectation),
        )

    return [
        NameAndValue(
            'failure pre sds',
            validation_case(RelOptionType.REL_HDS_CASE,
                            validation.PRE_SDS_FAILURE_EXPECTATION,
                            )
        ),
        NameAndValue(
            'failure post sds',
            validation_case(RelOptionType.REL_ACT,
                            validation.POST_SDS_FAILURE_EXPECTATION,
                            )
        ),
    ]
