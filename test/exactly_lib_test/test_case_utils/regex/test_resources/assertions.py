import re
from typing import Pattern, Callable, Sequence

from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.dir_dependent_value import DirDependencies
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.regex.regex_ddv import RegexSdv, RegexDdv
from exactly_lib.util import symbol_table
from exactly_lib_test.test_case_file_structure.test_resources.dir_dep_value_assertions import \
    matches_multi_dir_dependent_value
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.test_resources.pre_or_post_sds_value_validator import \
    PreOrPostSdsValueValidationAssertion
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationAssertions, all_validations_passes
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_regex_sdv(
        primitive_value: Callable[[Tcds], ValueAssertion[Pattern]] = lambda tcds: asrt.anything_goes(),
        references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
        dir_dependencies: DirDependencies = DirDependencies.NONE,
        validation: ValidationAssertions = all_validations_passes(),
        symbols: symbol_table.SymbolTable = None,
        tcds: Tcds = fake_tcds(),
) -> ValueAssertion[RegexSdv]:
    symbols = symbol_table.symbol_table_from_none_or_value(symbols)

    def resolve_value(sdv: RegexSdv):
        return sdv.resolve(symbols)

    def on_resolve_primitive_value(tcds_: Tcds) -> ValueAssertion[Pattern]:
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
                                              PreOrPostSdsValueValidationAssertion(
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
