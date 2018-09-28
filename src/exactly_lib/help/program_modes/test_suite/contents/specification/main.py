from exactly_lib import program_info
from exactly_lib.cli.definitions.common_cli_options import SUITE_COMMAND
from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.formatting import SectionName
from exactly_lib.definitions.test_suite import section_names
from exactly_lib.help.program_modes.test_suite.contents.specification import outcome
from exactly_lib.help.program_modes.test_suite.contents_structure.test_suite_help import TestSuiteHelp
from exactly_lib.test_suite import exit_values
from exactly_lib.util.textformat.constructor import sections
from exactly_lib.util.textformat.constructor.sections import \
    SectionContentsConstructor
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h
from exactly_lib.util.textformat.section_target_hierarchy.as_section_contents import \
    SectionContentsConstructorFromHierarchyGenerator
from exactly_lib.util.textformat.section_target_hierarchy.generator import SectionHierarchyGenerator
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.textformat_parser import TextParser
from . import structure


def specification_constructor(suite_help: TestSuiteHelp) -> SectionContentsConstructor:
    return SectionContentsConstructorFromHierarchyGenerator(
        hierarchy('unused section header', suite_help)
    )


def hierarchy(header: str,
              suite_help: TestSuiteHelp) -> SectionHierarchyGenerator:
    tp = TextParser({
        'program_name': formatting.program_name(program_info.PROGRAM_NAME),
        'executable_name': program_info.PROGRAM_NAME,
        'suite_program_mode': SUITE_COMMAND,
        'reporter_concept': formatting.concept_(concepts.SUITE_REPORTER_CONCEPT_INFO),
        'cases': section_names.CASES,
        'suites': section_names.SUITES,
        'ALL_PASS': exit_values.ALL_PASS.exit_identifier,
        'generic_section': SectionName('NAME'),
    })

    def section_of_parsed(contents: str) -> SectionContentsConstructor:
        return sections.constant_contents(
            docs.section_contents(tp.fnap(contents))
        )

    return h.hierarchy(
        header,
        children=[
            h.child('introduction',
                    h.leaf('Introduction',
                           section_of_parsed(_INTRODUCTION))
                    ),
            h.child('structure',
                    structure.root('Structure', suite_help)
                    ),
            h.child('file-syntax',
                    h.leaf('File syntax',
                           section_of_parsed(_FILE_SYNTAX))
                    ),
            h.child('outcome',
                    outcome.root('Outcome')),
        ])


_INTRODUCTION_SUMMARY = """\
{program_name} has functionality for organizing test cases in test suites.
A test suite can contain test cases as well as sub suites.


The result of executing a test suite is reported by a {reporter_concept}.
"""

_INTRODUCTION = """\
A test suite is written as a plain text file:


```
{cases:syntax}

a.case
group-dir/*.case

{suites:syntax}

sub-suite.suite
sub-dir/*.suite
```


If the file 'example.suite' contains this text, then {program_name} can execute it:


```
> {executable_name} {suite_program_mode} example.suite
...
{ALL_PASS}
```


A suite file can have any name - {program_name} does not put any restriction on file names.
"""

_STRUCTURE_INTRO = """\
A suite is made up of "sections". The sections are:
"""

_FILE_SYNTAX = """\
Syntax is line oriented.


"{generic_section:syntax}" on a single line declares the start of section "{generic_section:plain}".


The order of sections is irrelevant.


A section may appear any number of times.
The contents of all appearances are accumulated.


Empty lines, and lines beginning with "#" are ignored,
unless part of an instruction.
"""
