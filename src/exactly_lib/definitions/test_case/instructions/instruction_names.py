from exactly_lib.definitions import conf_params
from exactly_lib.definitions.primitives import program
from exactly_lib.definitions.test_case import file_check_properties

RUN_INSTRUCTION_NAME = program.RUN_PROGRAM_PRIMITIVE

SHELL_INSTRUCTION_NAME = program.SHELL_COMMAND_TOKEN
SYS_CMD_INSTRUCTION_NAME = program.SYSTEM_PROGRAM_TOKEN

SYMBOL_REF_PROGRAM_INSTRUCTION_NAME = program.SYMBOL_PROGRAM_TOKEN

NEW_FILE_INSTRUCTION_NAME = 'file'

NEW_DIR_INSTRUCTION_NAME = 'dir'

ENV_VAR_INSTRUCTION_NAME = 'env'

CHANGE_DIR_INSTRUCTION_NAME = 'cd'

SYMBOL_DEFINITION_INSTRUCTION_NAME = 'def'

EXIT_CODE_INSTRUCTION_NAME = 'exit-code'

CONTENTS_OF_STDOUT_INSTRUCTION_NAME = 'stdout'

CONTENTS_OF_STDIN_INSTRUCTION_NAME = 'stdin'

CONTENTS_OF_EXPLICIT_FILE_INSTRUCTION_NAME = file_check_properties.REGULAR_FILE_CONTENTS

CONTENTS_OF_EXPLICIT_DIR_INSTRUCTION_NAME = file_check_properties.DIR_CONTENTS

TEST_CASE_STATUS_INSTRUCTION_NAME = conf_params.TEST_CASE_STATUS

HDS_CASE_DIRECTORY_INSTRUCTION_NAME = conf_params.HDS_CASE_DIRECTORY

HDS_ACT_DIRECTORY_INSTRUCTION_NAME = conf_params.HDS_ACT_DIRECTORY

ACTOR_INSTRUCTION_NAME = conf_params.ACTOR

TIMEOUT_INSTRUCTION_NAME = conf_params.TIMEOUT
