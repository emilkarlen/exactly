from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.primitives import string
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help import std_tags
from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.string_matcher.matcher_options import EQUALS_ARGUMENT
from exactly_lib.processing import exit_values
from exactly_lib.program_info import PROGRAM_NAME
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    SectionContentsConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser


class Documentation(SectionContentsConstructor):
    def __init__(self):
        self._tp = TextParser({
            'test_case_file': 'helloworld.case',
            'EXECUTABLE_PROGRAM': PROGRAM_NAME,
            'program_name': formatting.program_name(PROGRAM_NAME),
            'action_to_check': 'helloworld',
            'ATC': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
            'CONTENTS_EQUALS_ARGUMENT': EQUALS_ARGUMENT,
            'INT_EQUALS_OPERATOR': comparators.EQ.name,
            'act': phase_names.ACT,
            'assert': phase_names.ASSERT,
            'PASS': exit_values.EXECUTION__PASS.exit_identifier,
            'FAIL': exit_values.EXECUTION__FAIL.exit_identifier,
            'stdout_instruction': instruction_names.CONTENTS_OF_STDOUT_INSTRUCTION_NAME,
            'exit_code_instruction': instruction_names.EXIT_CODE_INSTRUCTION_NAME,
            'executable_file': formatting.misc_name_with_formatting(misc_texts.EXECUTABLE_FILE),
            'console_style': std_tags.CONSOLE_TEXT,
            'HERE_DOCUMENT_MARKER_PREFIX': string.HERE_DOCUMENT_MARKER_PREFIX,
            'MARKER': 'EOF',
        })

    def apply(self, environment: ConstructionEnvironment) -> doc.SectionContents:
        return doc.SectionContents(self._tp.fnap(_INITIAL_DESCRIPTION),
                                   [
                                       docs.section('File structure',
                                                    self._tp.fnap(_FILE_STRUCTURE))
                                   ])


_INITIAL_DESCRIPTION = """\
A test case is written as a plain text file:


```
{act:syntax}

{action_to_check}

{assert:syntax}

{exit_code_instruction} {INT_EQUALS_OPERATOR} 0

{stdout_instruction} {CONTENTS_EQUALS_ARGUMENT} {HERE_DOCUMENT_MARKER_PREFIX}{MARKER}
Hello, World!
{MARKER}
```


If the file "{test_case_file}" contains this test case,
then {program_name} can execute it:


```:{console_style}
> {EXECUTABLE_PROGRAM} {test_case_file}
{PASS}
```


"{PASS}" means that {program_name} was able to execute the "{action_to_check}" program,
and that all assertions were satisfied.


It also means that the executable "{action_to_check}" file
was found in in the same directory as the test case file.
"""

_FILE_STRUCTURE = """\
{act:syntax} marks the beginning of the {act} phase.


The {act} phase contains the {ATC} - the thing that is tested by the test case.


It must consist of a single command line,
starting with the name of {executable_file:a}
(by default).

The file must be located in the same directory as the test case file (by default).


{assert:syntax} marks the beginning of the {assert} phase.


The {assert} phase contains assertions,
such as "{exit_code_instruction}" and "{stdout_instruction}".


The assertions determines the outcome of the test case.

Each assertion either {PASS} or {FAIL}.
If any assertion {FAIL}, then the outcome of the test case as a whole is {FAIL}.
Otherwise it is {PASS}.
"""
