from exactly_lib.cli.program_modes.help.program_modes.test_case.help_request import TestCaseHelpRequest
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt


def matches_test_case_help_request(item: asrt.ValueAssertion = asrt.anything_goes(),
                                   name: asrt.ValueAssertion = asrt.anything_goes(),
                                   data: asrt.ValueAssertion = asrt.anything_goes(),
                                   do_include_name_in_output: asrt.ValueAssertion = asrt.anything_goes(),
                                   ) -> asrt.ValueAssertion:
    return asrt.is_instance_with(TestCaseHelpRequest,
                                 asrt.and_([
                                     asrt.sub_component('item',
                                                        TestCaseHelpRequest.item.fget,
                                                        item),
                                     asrt.sub_component('name',
                                                        TestCaseHelpRequest.name.fget,
                                                        name),
                                     asrt.sub_component('data',
                                                        TestCaseHelpRequest.data.fget,
                                                        data),
                                     asrt.sub_component('do_include_name_in_output',
                                                        TestCaseHelpRequest.do_include_name_in_output.fget,
                                                        do_include_name_in_output),
                                 ]))
