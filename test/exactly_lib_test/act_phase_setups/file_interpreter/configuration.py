from exactly_lib.act_phase_setups import file_interpreter as sut
from exactly_lib_test.act_phase_setups.test_resources.act_source_and_executor import Configuration


class TheConfiguration(Configuration):
    def __init__(self):
        super().__init__(sut.Constructor())
