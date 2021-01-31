from exactly_lib.help.program_modes.common.contents_structure import SectionDocumentation
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches_section_documentation(name: Assertion = asrt.anything_goes()) -> Assertion:
    return asrt.is_instance_with(SectionDocumentation,
                                 asrt.and_([
                                     asrt.sub_component('name',
                                                        lambda sec_doc: sec_doc.name.plain,
                                                        name),
                                 ]))
