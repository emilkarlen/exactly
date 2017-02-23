from exactly_lib.instructions.multi_phase_instructions.run import INTERPRET_OPTION
from exactly_lib.section_document.new_parse_source import ParseSource
from exactly_lib_test.test_resources.parse import single_line_source
from exactly_lib_test.test_resources.programs import python_program_execution as py_exe


def source_for_interpreting(relativity_option: str,
                            file_name: str) -> ParseSource:
    file_ref = '%s %s' % (relativity_option, file_name)
    return single_line_source('%s %s %s' % (py_exe.command_line_for_arguments([]),
                                            INTERPRET_OPTION,
                                            file_ref))
