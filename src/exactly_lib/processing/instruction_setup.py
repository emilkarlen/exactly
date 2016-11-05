class InstructionsSetup(tuple):
    def __new__(cls,
                config_instruction_set: dict,
                setup_instruction_set: dict,
                assert_instruction_set: dict,
                before_assert_instruction_set: dict,
                cleanup_instruction_set: dict):
        """
        Each dictionary is a mapping: instruction-name -> `SingleInstructionSetup`.

        Each SingleInstructionSetup should parse and construct an instruction for
         the correct phase (of course). I.e., sub classes of Instruction.
        """
        return tuple.__new__(cls, (config_instruction_set,
                                   setup_instruction_set,
                                   assert_instruction_set,
                                   before_assert_instruction_set,
                                   cleanup_instruction_set))

    @property
    def config_instruction_set(self) -> dict:
        return self[0]

    @property
    def setup_instruction_set(self) -> dict:
        return self[1]

    @property
    def before_assert_instruction_set(self) -> dict:
        return self[2]

    @property
    def assert_instruction_set(self) -> dict:
        return self[3]

    @property
    def cleanup_instruction_set(self) -> dict:
        return self[4]
