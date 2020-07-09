from exactly_lib.definitions.entity import types
from exactly_lib.definitions.test_case import file_check_properties, phase_names
from exactly_lib.test_case_utils import file_properties
from exactly_lib.test_case_utils.err_msg import header_rendering
from exactly_lib.test_case_utils.file_properties import FileType
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.str_.str_constructor import ToStringObject


def unexpected_of_file_type(file_type: FileType) -> ToStringObject:
    return unexpected(file_properties.TYPE_INFO[file_type].description)


def unexpected_of_std_file(file: ProcOutputFile) -> ToStringObject:
    return unexpected(process_output_files.PROC_OUTPUT_FILE_NAMES[file])


def target_name_of_proc_output_file_from_act_phase(file: ProcOutputFile) -> ToStringObject:
    return str_constructor.FormatPositional(
        '{} from {}',
        process_output_files.PROC_OUTPUT_FILE_NAMES[file],
        phase_names.ACT.syntax,
    )


def target_name_of_proc_output_file_from_program(file: ProcOutputFile) -> ToStringObject:
    return str_constructor.FormatPositional(
        '{} from {}',
        process_output_files.PROC_OUTPUT_FILE_NAMES[file],
        types.PROGRAM_TYPE_INFO.singular_name,
    )


def unexpected(target: ToStringObject) -> ToStringObject:
    return header_rendering.unexpected_attr_of_obj(file_check_properties.CONTENTS,
                                                   target)
