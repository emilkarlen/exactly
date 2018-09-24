from exactly_lib.definitions import misc_texts
from exactly_lib.definitions.cross_ref.concrete_cross_refs import PredefinedHelpContentsPartReference, \
    HelpPredefinedContentsPart
from exactly_lib.definitions.entity import concepts, actors
from exactly_lib.definitions.test_case import phase_names_plain, phase_infos
from exactly_lib.definitions.test_suite import file_names
from exactly_lib.help.program_modes.common.renderers import sections_short_list
from exactly_lib.help.program_modes.test_case.contents.specification.utils import Setup
from exactly_lib.help.render import see_also
from exactly_lib.test_case import phase_identifier
from exactly_lib.util.textformat.constructor import sections
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h, generator
from exactly_lib.util.textformat.structure.structures import *
from exactly_lib.util.textformat.textformat_parser import TextParser


def root(header: str, setup: Setup) -> generator.SectionHierarchyGenerator:
    tp = TextParser({
        'default_suite_file_name': file_names.DEFAULT_SUITE_FILE,
        'act': phase_infos.ACT.name,
        'action_to_check': concepts.ACTION_TO_CHECK_CONCEPT_INFO.name,
        'ATC': concepts.ACTION_TO_CHECK_CONCEPT_INFO.acronym,
        'actor': concepts.ACTOR_CONCEPT_INFO.name,
        'os_process': misc_texts.OS_PROCESS_NAME,
        'null_actor': actors.NULL_ACTOR.singular_name,
    })

    def const_paragraphs(header_: StrOrStringText,
                         paragraphs: List[ParagraphItem]) -> generator.SectionHierarchyGenerator:
        return h.leaf(header_,
                      sections.constant_contents(section_contents(paragraphs)))

    def phases_documentation() -> List[ParagraphItem]:
        return (tp.fnap(_PHASES_INTRO) +
                [sections_short_list(setup.test_case_help.phase_helps_in_order_of_execution,
                                     phase_identifier.DEFAULT_PHASE.section_name,
                                     phase_names_plain.SECTION_CONCEPT_NAME)])

    return h.hierarchy(
        header,
        children=[
            h.child('phases',
                    const_paragraphs('Phases',
                                     phases_documentation())
                    ),
            h.child('act',
                    const_paragraphs(tp.text('The {act} phase, {action_to_check:/q} and {actor:s/q}'),
                                     tp.fnap(_ACT))
                    ),
            h.child('instructions',
                    const_paragraphs('Instructions',
                                     tp.fnap(_INSTRUCTIONS))
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
            h.with_not_in_toc(
                h.leaf(
                    see_also.SEE_ALSO_TITLE,
                    see_also.SeeAlsoSectionContentsConstructor(
                        see_also.items_of_targets(_see_also_targets())
                    ))
            ),
        ]
    )


def _see_also_targets() -> List[see_also.SeeAlsoTarget]:
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
and executing the {act} phase means executing this as an {os_process}.


The {actor:/q} concept makes it possible
to have different kind of {ATC}s.
E.g. executable program files, source code files and shell commands.


The {actor}
interprets the contents of the {act} phase,
which gives the {ATC}.


A test case configures which {actor} to use.


The special "{null_actor}" {actor}
specifies a no-options {ATC}.
"""

_INSTRUCTIONS = """\
All phases except {act:syntax} is a sequence of instructions, zero or more.


Executing a phase with instructions means executing all it's instructions,
in the order they appear in the test case.
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
