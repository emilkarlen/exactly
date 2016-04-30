from exactly_lib.help.program_modes.test_case.contents.main.utils import Setup
from exactly_lib.program_info import PROGRAM_NAME
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import document as doc


def intro_intro_documentation(setup: Setup) -> doc.SectionContents:
    format_values = {
        'test_case_file': 'helloworld.case',
        'EXECUTABLE_PROGRAM': PROGRAM_NAME,
        'action_to_check': 'helloworld',
        'phase': setup.phase_names
    }
    paragraphs = normalize_and_parse(TEXT.format_map(format_values))
    return doc.SectionContents(paragraphs, [])


TEXT = """\
A test case is written as a plain text file:


```
[act]

{action_to_check}

[assert]

exitcode 0

stdout <<EOF
Hello, World!
EOF
```


If the file '{test_case_file}' contains this test case,
then {EXECUTABLE_PROGRAM} can execute it:


```
> {EXECUTABLE_PROGRAM} {test_case_file}
PASS
```


"PASS" means that all assertions were satisfied.


It also means that '{action_to_check}'
is an executable program located in the same directory as the test case file.
"""
