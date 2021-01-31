import re
from typing import Pattern, Callable, Sequence

from exactly_lib.impls.types.regex.regex_ddv import RegexSdv, RegexDdv
from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.sdv_structure import SymbolReference, ReferenceRestrictions
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.type_val_deps.dep_variants.ddv.ddv_validation import DdvValidator
from exactly_lib.type_val_deps.dep_variants.ddv.dir_dependent_value import DirDependencies
from exactly_lib.util import symbol_table
from exactly_lib_test.impls.test_resources.validation.ddv_assertions import \
    DdvValidationAssertion
from exactly_lib_test.impls.test_resources.validation.validation import ValidationAssertions
from exactly_lib_test.tcfs.test_resources.fake_ds import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion
from exactly_lib_test.type_val_deps.data.test_resources.concrete_restriction_assertion import \
    is_any_data_type_reference_restrictions
from exactly_lib_test.type_val_deps.data.test_resources.symbol_reference_assertions import \
    is_reference_to_data_type_symbol
from exactly_lib_test.type_val_deps.dep_variants.test_resources.ddv_w_deps_assertions import \
    matches_multi_dir_dependent_value


def matches_regex_sdv(
        primitive_value: Callable[[TestCaseDs], Assertion[Pattern]] = lambda tcds: asrt.anything_goes(),
        references: Assertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
        dir_dependencies: DirDependencies = DirDependencies.NONE,
        validation: ValidationAssertions = ValidationAssertions.all_passes(),
        symbols: symbol_table.SymbolTable = None,
        tcds: TestCaseDs = fake_tcds(),
) -> Assertion[RegexSdv]:
    symbols = symbol_table.symbol_table_from_none_or_value(symbols)

    def resolve_value(sdv: RegexSdv):
        return sdv.resolve(symbols)

    def on_resolve_primitive_value(tcds_: TestCaseDs) -> Assertion[Pattern]:
        return asrt.is_instance_with(RE_PATTERN_TYPE,
                                     primitive_value(tcds_))

    resolved_value_assertion = matches_multi_dir_dependent_value(
        dir_dependencies,
        on_resolve_primitive_value,
        tcds,
    )

    def validation_is_successful(ddv: RegexDdv) -> bool:
        validator = ddv.validator()
        return (validator.validate_pre_sds_if_applicable(tcds.hds) is None and
                validator.validate_post_sds_if_applicable(tcds) is None)

    return asrt.is_instance_with(
        RegexSdv,
        asrt.and_([
            asrt.sub_component(
                'references',
                sdv_structure.get_references,
                references),

            asrt.sub_component(
                'resolved value',
                resolve_value,
                asrt.and_([
                    asrt.sub_component(
                        'validator',
                        lambda value: value.validator(),
                        asrt.is_instance_with(DdvValidator,
                                              DdvValidationAssertion(
                                                  tcds,
                                                  validation))
                    ),
                    asrt.if_(
                        validation_is_successful,
                        resolved_value_assertion
                    ),
                ]),
            )
        ])
    )


RE_PATTERN_TYPE = type(re.compile(''))


def is_reference_to_valid_regex_string_part(symbol_name: str) -> Assertion[SymbolReference]:
    return is_reference_to_data_type_symbol(symbol_name)


def is_regex_reference_restrictions() -> Assertion[ReferenceRestrictions]:
    return is_any_data_type_reference_restrictions()
