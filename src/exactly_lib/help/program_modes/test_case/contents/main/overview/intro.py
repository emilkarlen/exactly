from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.help_texts import formatting
from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import EQUALS_ARGUMENT
from exactly_lib.program_info import PROGRAM_NAME
from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor, \
    ConstructionEnvironment
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import document as doc


class Documentation(SectionContentsConstructor):
    def __init__(self, setup: Setup):
        self.setup = setup

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return intro_intro_documentation(self.setup)


def intro_intro_documentation(setup: Setup) -> doc.SectionContents:
    format_values = {
        'test_case_file': 'helloworld.case',
        'EXECUTABLE_PROGRAM': PROGRAM_NAME,
        'program_name': formatting.program_name(PROGRAM_NAME),
        'action_to_check': 'helloworld',
        'phase': setup.phase_names,
        'CONTENTS_EQUALS_ARGUMENT': EQUALS_ARGUMENT,
    }
    paragraphs = normalize_and_parse(TEXT.format_map(format_values))
    return doc.SectionContents(paragraphs, [])


TEXT = """\
A test case is written as a plain text file:


```
[act]

{action_to_check}

[assert]

exitcode == 0

stdout {CONTENTS_EQUALS_ARGUMENT} <<EOF
Hello, World!
EOF
```


If the file '{test_case_file}' contains this test case,
then {program_name} can execute it:


```
> {EXECUTABLE_PROGRAM} {test_case_file}
PASS
```


"PASS" means that all assertions are satisfied.


It also means that '{action_to_check}'
is an executable program located in the same directory as the test case file.
"""
