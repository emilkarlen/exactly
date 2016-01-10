from shellcheck_lib.document.parser_implementations.instruction_parser_for_single_phase import \
    SingleInstructionParserSource
from shellcheck_lib.instructions.multi_phase_instructions.execute import INTERPRET_OPTION
from shellcheck_lib_test.test_resources import python_program_execution as py_exe
from shellcheck_lib_test.test_resources.parse import single_line_source


def source_for_interpreting(relativity_option: str,
                            file_name: str) -> SingleInstructionParserSource:
    file_ref = '%s %s' % (relativity_option, file_name)
    return single_line_source('%s %s %s' % (py_exe.command_line_for_arguments([]),
                                            INTERPRET_OPTION,
                                            file_ref))
