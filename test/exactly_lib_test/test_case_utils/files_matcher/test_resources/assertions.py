from exactly_lib.symbol import sdv_structure
from exactly_lib.symbol.logic.files_matcher import FilesMatcherSdv
from exactly_lib.symbol.logic.logic_type_sdv import LogicTypeSdv
from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.type_system.logic.files_matcher import FilesMatcher, FilesMatcherConstructor, FilesMatcherDdv
from exactly_lib.type_system.value_type import ValueType, LogicValueType
from exactly_lib.util import symbol_table
from exactly_lib.util.file_utils import TmpDirFileSpaceThatMustNoBeUsed
from exactly_lib_test.symbol.test_resources.sdv_assertions import is_sdv_of_logic_type
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def matches_files_matcher_sdv(references: ValueAssertion = asrt.is_empty_sequence,
                              symbols: symbol_table.SymbolTable = None,
                              tcds: Tcds = fake_tcds()
                              ) -> ValueAssertion[LogicTypeSdv]:
    symbols = symbol_table.symbol_table_from_none_or_value(symbols)

    def resolve_ddv(sdv: LogicTypeSdv):
        return sdv.resolve(symbols)

    def get_validator(ddv: FilesMatcherDdv):
        return ddv.validator

    def resolve_constructor(ddv: FilesMatcherDdv):
        return ddv.value_of_any_dependency(tcds)

    def resolve_matcher(value: FilesMatcherConstructor):
        return value.construct(TmpDirFileSpaceThatMustNoBeUsed())

    def get_negation(value: FilesMatcher):
        return value.negation

    matcher_assertion = asrt.is_instance_with__many(
        FilesMatcher,
        [
            asrt.sub_component('negation',
                               get_negation,
                               asrt.is_instance(FilesMatcher)),
        ])

    constructor_assertion = asrt.is_instance_with__many(
        FilesMatcherConstructor,
        [
            asrt.sub_component('construct',
                               resolve_matcher,
                               matcher_assertion),
        ])

    ddv_assertion = asrt.is_instance_with__many(
        FilesMatcherDdv,
        [
            asrt.sub_component('validator',
                               get_validator,
                               asrt.is_instance(DdvValidator)
                               ),

            asrt.sub_component('resolve-constructor',
                               resolve_constructor,
                               constructor_assertion),
        ])

    return asrt.is_instance_with(
        FilesMatcherSdv,
        asrt.and_([
            is_sdv_of_logic_type(LogicValueType.FILES_MATCHER,
                                 ValueType.FILES_MATCHER),

            asrt.sub_component('references',
                               sdv_structure.get_references,
                               references),

            asrt.sub_component('resolved value',
                               resolve_ddv,
                               ddv_assertion
                               ),
        ])
    )
