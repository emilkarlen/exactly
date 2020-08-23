from exactly_lib.instructions.assert_ import existence_of_file as sut
from exactly_lib_test.instructions.assert_.test_resources import instruction_check

CHECKER = instruction_check.Checker(sut.Parser())
