import sys

from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.instructions.configuration.utils import actor_utils

SET_ACTOR_TO__FILE_INTERPRETER__WITH_PYTHON_INTERPRETER = (
    '{actor_instruction} {option_for_file_interpreter} {abs_path_to_python_executable}'.format(
        actor_instruction=instruction_names.ACTOR_INSTRUCTION_NAME,
        option_for_file_interpreter=actor_utils.FILE_INTERPRETER_OPTION,
        abs_path_to_python_executable=sys.executable))
