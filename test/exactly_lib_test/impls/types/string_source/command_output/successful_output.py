import unittest

from exactly_lib.util.name_and_value import NameAndValue
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.types.string_source.command_output.test_resources import ModelMaker, \
    SourceConstructorForPySourceProgramViaCmdLine
from exactly_lib_test.test_resources.programs import py_programs
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestSuccessfulScenariosWithProgramFromDifferentChannels(),
    ])


class TestSuccessfulScenariosWithProgramFromDifferentChannels(unittest.TestCase):
    def runTest(self):
        text_printed_by_program = 'the text printed by the program'
        mem_buff_size_cases = [
            NameAndValue(
                'output fits in mem buff',
                len(text_printed_by_program),
            ),
            NameAndValue(
                'output do not fit in mem buff',
                len(text_printed_by_program) - 1,
            ),
        ]
        for proc_output_file in ProcOutputFile:
            python_source = py_programs.single_line_pgm_that_prints_to(proc_output_file,
                                                                       text_printed_by_program)
            for mem_buff_size_case in mem_buff_size_cases:
                frozen_may_depend_on_external_resources = len(text_printed_by_program) > mem_buff_size_case.value
                with self.subTest(output_channel=proc_output_file,
                                  mem_buff_size_case=mem_buff_size_case.name):
                    source_constructors = SourceConstructorForPySourceProgramViaCmdLine(
                        python_source,
                        ModelMaker(
                            ignore_exit_code=False,
                            output_channel_to_capture=proc_output_file,
                            mem_buff_size=mem_buff_size_case.value,
                        )
                    )
                    assertion = multi_obj_assertions.assertion_of_2_seq_w_file_first_and_last(
                        multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.equals(
                            text_printed_by_program,
                            may_depend_on_external_resources=asrt.equals(True),
                            frozen_may_depend_on_external_resources=asrt.equals(
                                frozen_may_depend_on_external_resources),
                        ),
                    )
                    # ACT & ASSERT #
                    assertion.apply_without_message(
                        self,
                        source_constructors.build(),
                    )
