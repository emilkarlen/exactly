from exactly_lib.instructions.multi_phase import define_symbol as sut
from exactly_lib_test.instructions.multi_phase.test_resources import \
    instruction_embryo_check

INSTRUCTION_CHECKER = instruction_embryo_check.Checker(sut.EmbryoParser())
