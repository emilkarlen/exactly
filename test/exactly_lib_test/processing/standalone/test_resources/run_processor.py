import io

from exactly_lib.common.process_result_reporter import Environment
from exactly_lib.processing.standalone import processor as standalone_processor
from exactly_lib.processing.standalone.settings import TestCaseExecutionSettings
from exactly_lib.util.std import StdOutputFiles
from exactly_lib_test.test_resources.process import SubProcessResult


def capture_output_from_processor(processor: standalone_processor.Processor,
                                  settings: TestCaseExecutionSettings,
                                  ) -> SubProcessResult:
    stdout_file = io.StringIO()
    stderr_file = io.StringIO()
    std_output_files = StdOutputFiles(stdout_file=stdout_file,
                                      stderr_file=stderr_file)

    # ACT #
    actual_exit_code = processor.process(Environment.new_plain(std_output_files), settings)

    ret_val = SubProcessResult(actual_exit_code,
                               stdout=stdout_file.getvalue(),
                               stderr=stderr_file.getvalue())
    stdout_file.close()
    stderr_file.close()
    return ret_val
