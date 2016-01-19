from shellcheck_lib.instructions.cleanup import change_dir, env, execute, new_dir, shell
from shellcheck_lib.test_case.instruction_setup import instruction_set_from_name_and_setup_constructor_list

INSTRUCTIONS = instruction_set_from_name_and_setup_constructor_list(
        [
            ('dir', new_dir.setup),
            ('env', env.setup),
            ('execute', execute.setup),
            ('pwd', change_dir.setup),
            ('shell', shell.setup),
        ]
)
