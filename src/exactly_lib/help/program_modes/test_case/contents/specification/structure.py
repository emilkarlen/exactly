from typing import List

from exactly_lib.actors.common import SHELL_COMMAND_MARKER
from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.entity import concepts, actors
from exactly_lib.definitions.test_case import phase_names_plain, phase_infos
from exactly_lib.definitions.test_suite import file_names
from exactly_lib.help.program_modes.common.renderers import sections_short_list
from exactly_lib.help.program_modes.test_case.contents.specification.utils import Setup
from exactly_lib.help.render import see_also
from exactly_lib.test_case import phase_identifier
from exactly_lib.util.textformat.constructor import sections, paragraphs
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h, generator
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.structures import StrOrStringText
from exactly_lib.util.textformat.textformat_parser import TextParser


def root(header: str, setup: Setup) -> generator.SectionHierarchyGenerator:
    tp = TextParser({
        'default_suite_file_name': file_names.DEFAULT_SUITE_FILE,
        'act': phase_infos.ACT.name,
        'assert': phase_infos.ASSERT.name,
        'action_to_check': concepts.ACTION_TO_CHECK_CONCEPT_INFO.name,
        'ATC': concepts.ACTION_TO_CHECK_CONCEPT_INFO.acronym,
        'actor': concepts.ACTOR_CONCEPT_INFO.name,
        'os_process': misc_texts.OS_PROCESS_NAME,
        'null_actor': actors.NULL_ACTOR.singular_name,
        'shell_command_marker': SHELL_COMMAND_MARKER,
        'shell_command': formatting.misc_name_with_formatting(misc_texts.SHELL_COMMAND),
        'shell_command_line': formatting.misc_name_with_formatting(misc_texts.SHELL_COMMAND_LINE),
    })

    def const_paragraphs(header_: StrOrStringText,
                         initial_paragraphs: List[docs.ParagraphItem]) -> generator.SectionHierarchyGenerator:
        return h.leaf(header_,
                      sections.constant_contents(docs.section_contents(initial_paragraphs)))

    def phases_documentation() -> List[ParagraphItem]:
        return (tp.fnap(_PHASES_INTRO) +
                [sections_short_list(setup.test_case_help.phase_helps_in_order_of_execution,
                                     phase_identifier.DEFAULT_PHASE.section_name,
                                     phase_names_plain.SECTION_CONCEPT_NAME)])

    act_contents = sections.contents(
        paragraphs.constant(tp.fnap(_ACT)),
        [
            _act_examples(tp),
            see_also.SeeAlsoSectionConstructor(
                see_also.items_of_targets(_act_see_also_targets())
            )
        ]
    )

    instructions_contents = sections.contents(
        paragraphs.constant(tp.fnap(_INSTRUCTIONS)),
        [
            see_also.SeeAlsoSectionConstructor(
                see_also.items_of_targets(_instructions_see_also_targets())
            )
        ]
    )

    return h.hierarchy(
        header,
        children=[
            h.child('phases',
                    const_paragraphs('Phases',
                                     phases_documentation())
                    ),
            h.child('act',
                    h.leaf(
                        tp.text('The {act} phase, {action_to_check:/q} and {actor:s/q}'),
                        act_contents
                    )
                    ),
            h.child('instructions',
                    h.leaf('Instructions',
                           instructions_contents)
                    ),
            h.child('suites',
                    h.hierarchy(
                        'Relation to test suites',
                        children=[
                            h.child('suite-contents',
                                    const_paragraphs('Inclusion of phase contents from suites',
                                                     tp.fnap(_SUITE_CONTENTS_INCLUSION))
                                    ),
                            h.child('part-of-suite',
                                    const_paragraphs('Part of suite',
                                                     tp.fnap(_PART_OF_SUITE))
                                    ),
                            h.with_not_in_toc(
                                h.leaf(
                                    see_also.SEE_ALSO_TITLE,
                                    see_also.SeeAlsoSectionContentsConstructor(
                                        see_also.items_of_targets(_suite_see_also_targets())
                                    )))
                            ,
                        ]),
                    ),
        ]
    )


def _act_examples(tp: TextParser) -> sections.SectionConstructor:
    return sections.section(
        docs.text('Examples'),
        sections.constant_contents(
            docs.section_contents(tp.fnap(_ACT_EXAMPLES))
        )
    )


def _act_see_also_targets() -> List[see_also.SeeAlsoTarget]:
    return [
        phase_infos.ACT.cross_reference_target,
        concepts.ACTION_TO_CHECK_CONCEPT_INFO.cross_reference_target,
        concepts.ACTOR_CONCEPT_INFO.cross_reference_target,
    ]


def _instructions_see_also_targets() -> List[see_also.SeeAlsoTarget]:
    return [
        concepts.INSTRUCTION_CONCEPT_INFO.cross_reference_target,
    ]


def _suite_see_also_targets() -> List[see_also.SeeAlsoTarget]:
    return [
        PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_SUITE_SPEC),
        PredefinedHelpContentsPartReference(HelpPredefinedContentsPart.TEST_CASE_CLI),
    ]


_PHASES_INTRO = """\
A test case is a sequence of "phases".

Executing a test case means executing all of it's phases.


All phases are optional.


The phases are (in order of execution):
"""

############################################################
# MENTION
#
# Cooperation of
# - "act" phase
# - "action to check"
# - "actor"
#
# - "null" actor
############################################################
_ACT = """\
The contents of the {act} phase represents an {action_to_check:/q} ({ATC}),
and executing the {act} phase means executing this as {os_process:a}.


The {actor:/q} concept makes it possible
to have different kind of {ATC}s.
E.g. executable program files, source code files and {shell_command:s}.


The {actor}
interprets the contents of the {act} phase,
and thereby resolves the {ATC}.


A test case configures which {actor} to use.


The special "{null_actor}" {actor}
specifies a no-operations {ATC}.
It is used if the test case does not contain an {act} phase.
"""

# ACT EXAMPLES exists as test cases in examples/
_ACT_EXAMPLES = """\
An {ATC} that is a Python source file, executed with arguments:


```
[conf]

actor = -file python

[act]

my-python-logic_symbol_utils.py argument1 "second argument"
```


An {ATC} that is {shell_command_line:a}:


```
[act]

$ echo 'This is a' {shell_command_line} > &2
```
"""

_INSTRUCTIONS = """\
All phases except {act:syntax} is a sequence of instructions, zero or more.


Executing a phase with instructions means executing all it's instructions,
in the order they appear in the test case.


Instructions in different phases serve different purposes.


For example, the instruction set for the {assert:syntax} phase
contains instructions that serve as assertions.
"""

_SUITE_CONTENTS_INCLUSION = """\
A test suite can contain test case contents.

When a test case is run as part of a suite, this contents is included in the case.
"""

_PART_OF_SUITE = """\
A test case is considered part of a suite, depending on how it is run.


When run in the following ways, it is part of a suite:

    
  * Standalone
  
      * A suite file is given via command line arguments
      
      * A file "{default_suite_file_name}" exits in the same directory as the test case file
      
        The file "{default_suite_file_name}" must be a test suite.
        
        
        Note that the test case need not be listed in "{default_suite_file_name}".

  * Via test suite
  
    The test case file is listed in the suite.
"""
