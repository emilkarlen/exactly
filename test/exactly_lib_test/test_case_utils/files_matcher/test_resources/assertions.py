from exactly_lib.symbol import resolver_structure
from exactly_lib.symbol.logic.files_matcher import FilesMatcherValue, FilesMatcherResolver
from exactly_lib.symbol.logic.logic_value_resolver import LogicValueResolver
from exactly_lib.test_case.validation.pre_or_post_validation import PreOrPostSdsValidator
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib_test.symbol.test_resources.resolver_assertions import is_resolver_of_logic_type
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_files_matcher_resolver(references: ValueAssertion = asrt.is_empty_sequence,
                                   symbols: symbol_table.SymbolTable = None,
                                   ) -> ValueAssertion[LogicValueResolver]:
    symbols = symbol_table.symbol_table_from_none_or_value(symbols)

    def resolve_value(resolver: LogicValueResolver):
        return resolver.resolve(symbols)

    def get_negation(value: FilesMatcherValue):
        return value.negation

    resolved_value_assertion = asrt.is_instance_with__many(
        FilesMatcherValue,
        [
            asrt.sub_component('negation',
                               get_negation,
                               asrt.is_instance(FilesMatcherValue)),
        ])

    return asrt.is_instance_with(
        FilesMatcherResolver,
        asrt.and_([
            is_resolver_of_logic_type(LogicValueType.FILES_MATCHER,
                                      ValueType.FILES_MATCHER),

            asrt.sub_component('references',
                               resolver_structure.get_references,
                               references),

            asrt.sub_component('validator',
                               lambda resolver: resolver.validator(),
                               asrt.is_instance(PreOrPostSdsValidator)
                               ),

            asrt.sub_component('resolved value',
                               resolve_value,
                               resolved_value_assertion
                               ),
        ])
    )
