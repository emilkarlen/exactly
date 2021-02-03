from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.entity import types, concepts
from exactly_lib.util.process_execution import process_output_files
from exactly_lib.util.process_execution.process_output_files import ProcOutputFile
from exactly_lib.util.str_.str_constructor import ToStringObject


def target_name(attribute_name: str, object_name: str) -> str:
    return ' '.join((attribute_name, 'from', object_name))


def proc_output_file_attribute(file: ProcOutputFile) -> str:
    return process_output_files.PROC_OUTPUT_FILE_NAMES[file]


ATTRIBUTE__EXIT_CODE = misc_texts.EXIT_CODE.singular

OBJECT__ATC = 'the {atc:/q}'.format(atc=concepts.ACTION_TO_CHECK_CONCEPT_INFO.name)

OBJECT__PROGRAM = types.PROGRAM_TYPE_INFO.singular_name


def target_name_of_proc_output_file_from_act_phase(file: ProcOutputFile) -> ToStringObject:
    return target_name(proc_output_file_attribute(file), OBJECT__ATC)


def target_name_of_proc_output_file_from_program(file: ProcOutputFile) -> ToStringObject:
    return target_name(proc_output_file_attribute(file), OBJECT__PROGRAM)
