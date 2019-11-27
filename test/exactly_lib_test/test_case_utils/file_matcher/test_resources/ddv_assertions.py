from exactly_lib.test_case.validation.ddv_validation import DdvValidator
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.file_matcher.impl import name_glob_pattern, file_type, name_regex
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.type_system.logic.file_matcher import FileMatcher, FileMatcherDdv
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion


def is_type_matcher(expected: FileType) -> ValueAssertion[FileMatcher]:
    return asrt.is_instance_with(file_type.FileMatcherType,
                                 asrt.sub_component('file_type',
                                                    file_type.FileMatcherType.file_type.fget,
                                                    asrt.is_(expected)))


def is_name_glob_pattern(name_pattern: ValueAssertion[str] = asrt.anything_goes()) -> ValueAssertion[FileMatcher]:
    return asrt.is_instance_with(name_glob_pattern.FileMatcherNameGlobPattern,
                                 asrt.sub_component('glob_pattern',
                                                    name_glob_pattern.FileMatcherNameGlobPattern.glob_pattern.fget,
                                                    asrt.is_instance_with(str, name_pattern))
                                 )


def is_name_regex(name_pattern: ValueAssertion[str] = asrt.anything_goes()) -> ValueAssertion[FileMatcher]:
    return asrt.is_instance_with(name_regex.FileMatcherBaseNameRegExPattern,
                                 asrt.sub_component('reg_ex_pattern',
                                                    name_regex.FileMatcherBaseNameRegExPattern.reg_ex_pattern.fget,
                                                    asrt.is_instance_with(str, name_pattern))
                                 )


def matches_file_matcher_ddv__deep(
        primitive_value: ValueAssertion[FileMatcher] = asrt.anything_goes(),
        validator: ValueAssertion[DdvValidator] = asrt.anything_goes(),
        tcds: Tcds = fake_tcds(),
) -> ValueAssertion[FileMatcherDdv]:
    def resolve_primitive_value(value: FileMatcherDdv):
        return value.value_of_any_dependency(tcds)

    def get_validator(value: FileMatcherDdv):
        return value.validator()

    return asrt.is_instance_with__many(
        FileMatcherDdv,
        [
            asrt.sub_component(
                'primitive value',
                resolve_primitive_value,
                asrt.is_instance_with(FileMatcher,
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


def matches_file_matcher_ddv(
        validator: ValueAssertion[DdvValidator] = asrt.anything_goes(),
) -> ValueAssertion[FileMatcherDdv]:
    def get_validator(value: FileMatcherDdv):
        return value.validator()

    return asrt.is_instance_with(
        FileMatcherDdv,
        asrt.sub_component(
            'validator',
            get_validator,
            asrt.is_instance_with(DdvValidator,
                                  validator)
        ))
