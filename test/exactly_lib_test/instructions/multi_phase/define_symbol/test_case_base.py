import unittest

from exactly_lib.instructions.multi_phase import define_symbol
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib_test.instructions.multi_phase.test_resources import \
    instruction_embryo_check as embryo_check
from exactly_lib_test.instructions.multi_phase.test_resources.instruction_embryo_check import Expectation
from exactly_lib_test.instructions.test_resources.arrangements import ArrangementWithSds


class TestCaseBaseForParser(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               arrangement: ArrangementWithSds,
               expectation: Expectation,
               ):
        parser = define_symbol.EmbryoParser()
        embryo_check.check(self, parser, source, arrangement, expectation)
