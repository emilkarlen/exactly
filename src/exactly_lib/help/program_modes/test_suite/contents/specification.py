from typing import List

from exactly_lib import program_info
from exactly_lib.cli.cli_environment.common_cli_options import SUITE_COMMAND
from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity import concepts
from exactly_lib.definitions.test_suite.section_names import DEFAULT_SECTION_NAME
from exactly_lib.help.program_modes.common.renderers import sections_short_list
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.util.textformat.construction.section_contents_constructor import SectionContentsConstructor, \
    SectionContentsConstructorForConstantContents
from exactly_lib.util.textformat.construction.section_hierarchy.as_section_contents import \
    SectionContentsConstructorFromHierarchyGenerator
from exactly_lib.util.textformat.construction.section_hierarchy.hierarchy import leaf, parent, Node
from exactly_lib.util.textformat.construction.section_hierarchy.structures import \
    SectionItemGeneratorNode, \
    SectionHierarchyGenerator
from exactly_lib.util.textformat.construction.section_hierarchy.targets import CustomTargetInfoFactory
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


def specification_constructor(suite_help: TestSuiteHelp) -> SectionContentsConstructor:
    return SectionContentsConstructorFromHierarchyGenerator(
        SpecificationHierarchyGenerator('unused section header', suite_help)
    )


class SpecificationHierarchyGenerator(SectionHierarchyGenerator):
    def __init__(self,
                 header: str,
                 suite_help: TestSuiteHelp):
        self.header = header
        self._suite_help = suite_help
        self._tp = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'executable_name': program_info.PROGRAM_NAME,
            'suite_program_mode': SUITE_COMMAND,
            'reporter_concept': formatting.concept_(concepts.SUITE_REPORTER_CONCEPT_INFO),
        })

    def generator_node(self, target_factory: CustomTargetInfoFactory) -> SectionItemGeneratorNode:
        generator = parent(self.header,
                           [],
                           [
                               Node('files-and-execution',
                                    leaf('Suite files and execution',
                                         self._section_of_parsed(_FILES_AND_EXECUTION_TEXT))
                                    ),
                               Node('sections-overview',
                                    leaf('Sections overview',
                                         self._suite_structure_contents())
                                    ),
                               Node('file-syntax',
                                    leaf('Suite file syntax',
                                         self._section_of_parsed(_FILE_SYNTAX))
                                    ),
                           ])
        return generator.generator_node(target_factory)

    def _section_of_parsed(self, contents: str) -> SectionContentsConstructor:
        return SectionContentsConstructorForConstantContents(
            docs.section_contents(self._tp.fnap(contents)))

    def _suite_structure_paragraphs(self) -> List[ParagraphItem]:
        ret_val = []
        ret_val.extend(self._tp.fnap(_STRUCTURE_INTRO))
        ret_val.append(sections_short_list(self._suite_help.section_helps,
                                           default_section_name=DEFAULT_SECTION_NAME,
                                           section_concept_name='section'))
        return ret_val

    def _suite_structure_contents(self) -> SectionContentsConstructor:
        return SectionContentsConstructorForConstantContents(
            docs.section_contents(self._suite_structure_paragraphs()))


_INTRODUCTION_SUMMARY = """\
{program_name} has functionality for organizing test cases in test suites.
A test suite can contain test cases as well as sub suites.


The result of executing a test suite is reported by a {reporter_concept}.
"""

_FILES_AND_EXECUTION_TEXT = """\
A test suite is written as a plain text file:


```
[cases]

a.case
group-dir/*.case

[suites]

sub-suite.suite
sub-dir/*.suite
```


If the file 'example.suite' contains this text, then {program_name} can execute it:


```
> {executable_name} {suite_program_mode} example.suite
...
OK
```


A suite file can have any name - {program_name} does not put any restriction on file names.
"""

_STRUCTURE_INTRO = """\
A suite is made up of "sections". The sections are:
"""

_FILE_SYNTAX = """\
"[NAME]" on a single line declares the start of section NAME.


The order of sections is irrelevant.


A section may appear any number of times.
The contents of all appearances are accumulated.


Empty lines, and lines beginning with "#" are ignored.
"""
