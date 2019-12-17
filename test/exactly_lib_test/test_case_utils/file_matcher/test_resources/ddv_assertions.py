from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherDdv
from exactly_lib.type_system.logic.matcher_base_class import MatcherWTraceAndNegation, MatcherDdv
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_file_matcher_ddv__deep(
        primitive_value: ValueAssertion[FileMatcher] = asrt.anything_goes(),
        validator: ValueAssertion[DdvValidator] = asrt.anything_goes(),
        tcds: Tcds = fake_tcds(),
) -> ValueAssertion[FileMatcherDdv]:
    def resolve_primitive_value(value: FileMatcherDdv):
        return value.value_of_any_dependency(tcds)

    def get_validator(value: FileMatcherDdv):
        return value.validator

    return asrt.is_instance_with__many(
        MatcherDdv,
        [
            asrt.sub_component(
                'primitive value',
                resolve_primitive_value,
                asrt.is_instance_with(MatcherWTraceAndNegation,
                                      primitive_value)
            ),
            asrt.sub_component(
                'validator',
                get_validator,
                asrt.is_instance_with(DdvValidator,
                                      validator)
            ),
        ]
    )
