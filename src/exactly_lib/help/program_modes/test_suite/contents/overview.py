from exactly_lib import program_info
from exactly_lib.help import cross_reference_id as cross_ref
from exactly_lib.help.program_modes.test_suite.contents_structure import TestSuiteHelp
from exactly_lib.help.utils.render import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.test_suite import parser
from exactly_lib.util.textformat.parse import normalize_and_parse
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import lists
from exactly_lib.util.textformat.structure import structures as docs


class OverviewRenderer(SectionContentsRenderer):
    def __init__(self, suite_help: TestSuiteHelp,
                 target_factory: cross_ref.CustomTargetInfoFactory = None):
        self._suite_help = suite_help
        self._format_map = {
            'program_name': program_info.PROGRAM_NAME,
        }
        if target_factory is None:
            target_factory = cross_ref.CustomTargetInfoFactory('')

        self._FILES_AND_EXECUTION_TI = target_factory.sub('Suite files and execution',
                                                          'files-and-execution')

        self._STRUCTURE_TI = target_factory.sub('Suite structure',
                                                'structure')

        self._FILE_SYNTAX_TI = target_factory.sub('Suite file syntax',
                                                  'test-case-files')

    def target_info_hierarchy(self) -> list:
        return [
            _leaf(self._FILES_AND_EXECUTION_TI),
            _leaf(self._STRUCTURE_TI),
            _leaf(self._FILE_SYNTAX_TI),
        ]

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents(
            self._parse(_INTRODUCTION_SUMMARY),
            [
                docs.section(self._FILES_AND_EXECUTION_TI.anchor_text(),
                             self._parse(_FILES_AND_EXECUTION_TEXT)),
                docs.section(self._STRUCTURE_TI.anchor_text(),
                             self._suite_structure()),
                docs.section(self._FILE_SYNTAX_TI.anchor_text(),
                             self._parse(_FILE_SYNTAX)),
            ])

    def _parse(self, s: str) -> list:
        return normalize_and_parse(s.format_map(self._format_map))

    def _suite_structure(self) -> list:
        ret_val = []
        ret_val.extend(self._parse(_STRUCTURE_INTRO))
        ret_val.append(self._suite_structure_sections_list())
        return ret_val

    def _suite_structure_sections_list(self) -> docs.ParagraphItem:
        return docs.simple_list([
            self._item(parser.SECTION_NAME__CASES,
                       _STRUCTURE_CASES_TEXT),
            self._item(parser.SECTION_NAME__SUITS,
                       _STRUCTURE_SUITES_TEXT),
            self._item(parser.SECTION_NAME__CONF,
                       _STRUCTURE_CONFIGURATION_TEXT),
        ],
            lists.ListType.VARIABLE_LIST)

    def _item(self,
              section_name: str,
              section_description: str) -> lists.HeaderContentListItem:
        return lists.HeaderContentListItem(docs.text(section_name),
                                           self._parse(section_description))


_leaf = cross_ref.target_info_leaf

_INTRODUCTION_SUMMARY = """\
TODO suite intro summary."""

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
> {program_name} suite example.suite
...
OK
```


A suite file can have any name - {program_name} does not put any restriction on file names.
"""

_STRUCTURE_INTRO = """\
A suite file is a sequence of "sections". The sections are:
"""

_STRUCTURE_CASES_TEXT = """\
Lists test cases.
"""

_STRUCTURE_SUITES_TEXT = """\
Lists sub suites.
"""

_STRUCTURE_CONFIGURATION_TEXT = """\
Configuration for the execution of every test case listed in the suite file.
"""

_FILE_SYNTAX = """\
"[NAME]" on a single line declares the start of section NAME.


A section may appear any number of times in a suite file.
The contents of all appearances are accumulated.


Empty lines, and lines beginning with "#" are ignored.
"""
