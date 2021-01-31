from exactly_lib.cli.program_modes.help.program_modes.test_case.help_request import TestCaseHelpRequest
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import Assertion


def matches_test_case_help_request(item: Assertion = asrt.anything_goes(),
                                   name: Assertion = asrt.anything_goes(),
                                   data: Assertion = asrt.anything_goes(),
                                   do_include_name_in_output: Assertion = asrt.anything_goes(),
                                   ) -> Assertion:
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
