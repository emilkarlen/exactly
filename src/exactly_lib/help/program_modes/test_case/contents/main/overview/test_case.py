from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity import concepts
from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor, \
    ConstructionEnvironment
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.textformat_parser import TextParser


class Documentation(SectionContentsConstructor):
    def __init__(self, setup: Setup):
        self.setup = setup
        self._tp = TextParser(
            {
                'ATC': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
                'phase': setup.phase_names,
            }
        )

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return doc.SectionContents(self._tp.fnap(DESCRIPTION), [])


DESCRIPTION = """\
A test case file contains a sequence of "phases".


The {phase[act]} phase contains the {ATC} (or, "system under test").


By default, it must consist of a single command line.


All other phases contain "instructions".
E.g., "exit-code" and "stdout" are instructions of the {phase[assert]} phase.


The instructions in the {phase[assert]} phase determines the outcome of the test case.
Each of these instructions is an assertion that either PASS or FAIL.
If any of the instructions FAIL, then the outcome of the test case as a whole is FAIL.
Otherwise it is PASS.
"""
