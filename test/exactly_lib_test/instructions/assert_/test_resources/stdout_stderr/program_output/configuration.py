from exactly_lib.instructions.assert_.utils.instruction_parser import AssertPhaseInstructionParser


class ChannelConfiguration:
    def parser(self) -> AssertPhaseInstructionParser:
        raise NotImplementedError('abstract method')

    def py_source_for_print(self, output: str) -> str:
        raise NotImplementedError('abstract method')
