from exactly_lib.symbol import resolver_structure
from exactly_lib.symbol.logic.logic_value_resolver import LogicValueResolver
from exactly_lib.symbol.logic.string_matcher import StringMatcherResolver
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.test_case_file_structure.home_and_sds import HomeAndSds
from exactly_lib.test_case_file_structure.path_relativity import DirectoryStructurePartition
from exactly_lib.type_system.logic.string_matcher import StringMatcher, StringMatcherValue
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.symbol.test_resources.resolver_assertions import is_resolver_of_logic_type
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_home_and_sds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_string_matcher_resolver(primitive_value: ValueAssertion[StringMatcher] = asrt.anything_goes(),
                                    references: ValueAssertion = asrt.is_empty_sequence,
                                    symbols: symbol_table.SymbolTable = None,
                                    tcds: HomeAndSds = fake_home_and_sds(),
                                    ) -> ValueAssertion[LogicValueResolver]:
    symbols = symbol_table.symbol_table_from_none_or_value(symbols)

    def resolve_value(resolver: LogicValueResolver):
        return resolver.resolve(symbols)

    def resolve_primitive_value(value: StringMatcherValue):
        return value.value_of_any_dependency(tcds)

    resolved_value_assertion = asrt.is_instance_with__many(
        StringMatcherValue,
        [
            asrt.sub_component('resolving dependencies',
                               lambda sm_value: sm_value.resolving_dependencies(),
                               asrt.is_set_of(asrt.is_instance(DirectoryStructurePartition))),

            asrt.sub_component('primitive value',
                               resolve_primitive_value,
                               asrt.is_instance_with(StringMatcher,
                                                     primitive_value))
        ])

    return asrt.is_instance_with(
        StringMatcherResolver,
        asrt.and_([
            is_resolver_of_logic_type(LogicValueType.STRING_MATCHER,
                                      ValueType.STRING_MATCHER),

            asrt.sub_component('references',
                               resolver_structure.get_references,
                               references),

            asrt.sub_component('validator',
                               lambda resolver: resolver.validator,
                               asrt.is_instance(PreOrPostSdsValidator)
                               ),

            asrt.sub_component('resolved value',
                               resolve_value,
                               resolved_value_assertion
                               ),
        ])
    )


def matches_string_matcher_attributes(references: ValueAssertion = asrt.is_empty_sequence,
                                      ) -> ValueAssertion[LogicValueResolver]:
    return asrt.is_instance_with(
        StringMatcherResolver,
        asrt.and_([
            is_resolver_of_logic_type(LogicValueType.STRING_MATCHER,
                                      ValueType.STRING_MATCHER),

            asrt.sub_component('references',
                               resolver_structure.get_references,
                               references),

            asrt.sub_component('validator',
                               lambda resolver: resolver.validator,
                               asrt.is_instance(PreOrPostSdsValidator)
                               ),
        ])
    )
