import unittest
from pathlib import Path

from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib_test.impls.types.string_source.command_output.test_resources import ModelMaker, \
    SourceConstructorsBuilderBase
from exactly_lib_test.test_resources.value_assertions.value_assertion import MessageBuilder
from exactly_lib_test.type_val_prims.program.test_resources import commands
from exactly_lib_test.type_val_prims.string_source.test_resources import multi_obj_assertions, \
    contents_assertions as asrt_str_src_contents


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        TestWhenProgramIsUnableToExecuteResultShouldBeHardError()
    ])


class TestWhenProgramIsUnableToExecuteResultShouldBeHardError(unittest.TestCase):
    def runTest(self):
        for proc_output_file in ProcOutputFile:
            for ignore_exit_code in [False, True]:
                with self.subTest(ignore_exit_code=ignore_exit_code,
                                  proc_output_file=proc_output_file):
                    # ACT & ASSERT #
                    source_constructor = _SourceConstructorsForExeFile(
                        Path('/the/path/of/a/non-existing/program'),
                        ModelMaker(
                            ignore_exit_code=ignore_exit_code,
                            output_channel_to_capture=proc_output_file,
                            mem_buff_size=2 ** 10
                        )
                    )
                    assertion = multi_obj_assertions.assertion_of_2_seq_w_file_first_and_last(
                        multi_obj_assertions.ExpectationOnUnFrozenAndFrozen.hard_error(
                            may_depend_on_external_resources=asrt_str_src_contents.external_dependencies__const(True),
                        ),
                    )
                    # ACT & ASSERT #
                    assertion.apply_without_message(
                        self,
                        source_constructor.build(),
                    )


class _SourceConstructorsForExeFile(SourceConstructorsBuilderBase):
    def __init__(self,
                 exe_file: Path,
                 model_maker: ModelMaker,
                 ):
        super().__init__()
        self.exe_file = exe_file
        self.model_maker = model_maker

    def new_with(self,
                 put: unittest.TestCase,
                 message_builder: MessageBuilder,
                 app_env: ApplicationEnvironment) -> StringSource:
        return self.model_maker.model_from(
            app_env,
            commands.command_that_runs_executable_file(self.exe_file),
        )
