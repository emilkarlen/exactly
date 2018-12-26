from exactly_lib.definitions import formatting
from exactly_lib.definitions.entity import directives, concepts
from exactly_lib.definitions.entity.concepts import ACTOR_CONCEPT_INFO
from exactly_lib.definitions.formatting import AnyInstructionNameDictionary
from exactly_lib.help.program_modes.test_case.contents.specification.utils import Setup
from exactly_lib.help.render import see_also
from exactly_lib.section_document.syntax import section_header, LINE_COMMENT_MARKER
from exactly_lib.test_case.phase_identifier import DEFAULT_PHASE
from exactly_lib.test_case_utils.string_matcher import matcher_options as contents_opts
from exactly_lib.util.textformat.constructor import paragraphs, sections
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h, generator
from exactly_lib.util.textformat.textformat_parser import TextParser


def root(header: str, setup: Setup) -> generator.SectionHierarchyGenerator:
    tp = _text_parser(setup)

    def paragraphs_of(template: str) -> paragraphs.ParagraphItemsConstructor:
        return paragraphs.constant(tp.fnap(template))

    def initial_paragraphs_of(template: str) -> sections.SectionContentsConstructor:
        return sections.contents(paragraphs_of(template))

    file_inclusion_doc = sections.contents(
        paragraphs_of(FILE_INCLUSION_DOC),
        [see_also.SeeAlsoSectionConstructor(
            see_also.items_of_targets(_FILE_INCLUSION_SEE_ALSO_TARGETS)
        )]
    )
    return h.hierarchy(
        header,
        initial_paragraphs=paragraphs_of(_INTRO),
        children=[
            h.child_leaf('phases',
                         'Phases',
                         initial_paragraphs_of(PHASES_DOC)
                         ),
            h.child_leaf('phase-contents',
                         'Phase contents',
                         initial_paragraphs_of(PHASES_CONTENTS_DOC)
                         ),
            h.child_hierarchy('instructions',
                              'Instructions',
                              paragraphs_of(INSTRUCTIONS_DOC),
                              [h.child_leaf('description',
                                            'Instruction descriptions',
                                            initial_paragraphs_of(INSTRUCTIONS_DESCRIPTION_DOC))
                               ]
                              ),
            h.child_leaf('file-inclusion',
                         'File inclusion',
                         file_inclusion_doc
                         ),
            h.child_leaf('com-empty',
                         'Comments and empty lines',
                         initial_paragraphs_of(OTHER_DOC)
                         ),
        ]
    )


def _text_parser(setup: Setup) -> TextParser:
    return TextParser({
        'phase_declaration_for_NAME': section_header('NAME'),
        'instruction': AnyInstructionNameDictionary(),
        'default_phase': setup.phase_names[DEFAULT_PHASE.identifier].syntax,
        'phase': setup.phase_names,
        'actor': formatting.concept_(ACTOR_CONCEPT_INFO),
        'CONTENTS_EQUALS_ARGUMENT': contents_opts.EQUALS_ARGUMENT,
        'CONTENTS_EMPTY_ARGUMENT': contents_opts.EMPTY_ARGUMENT,
        'line_comment_char': LINE_COMMENT_MARKER,
        'file_inclusion_directive_in_text': formatting.keyword(directives.INCLUDING_DIRECTIVE_INFO.singular_name),
        'file_inclusion_directive': directives.INCLUDING_DIRECTIVE_INFO.singular_name,
    })


_FILE_INCLUSION_SEE_ALSO_TARGETS = [
    concepts.DIRECTIVE_CONCEPT_INFO.cross_reference_target,
    directives.INCLUDING_DIRECTIVE_INFO.cross_reference_target,
]

_INTRO = """\
Syntax is line oriented.


Top level elements start at the beginning of a line,
and line ends mark the end of elements, although some may span several lines.
"""

PHASES_DOC = """\
"{phase_declaration_for_NAME}" on a single line declares the start of phase NAME.

This line marks the start the {phase[assert]} phase, for example:


```
[assert]
```


The following lines will belong to this phase.


File contents before the first phase declaration belong to the default phase,
which is {default_phase}.


The order of the different phases in the test case file is irrelevant.
The phases are always executed in the same order,
regardless of the order they appear in the test case file.


A phase can be declared more than once.

Contents of multiple declarations are merged, and executed in the order it appears in the file.

Here, {instruction[exit_code]} is executed before {instruction[stderr]}:


```
[assert]

exit-code == 0

[act]

helloworld

[assert]

stderr {CONTENTS_EMPTY_ARGUMENT}
```
"""

PHASES_CONTENTS_DOC = """\
All phases except the {phase[act]} phase consist of a sequence of "instructions" (see below).


The contents of the {phase[act]} phase depends on which {actor} is used.

By default, it is expected to contain a single command line.
"""

INSTRUCTIONS_DOC = """\
Instructions start at the beginning of the line with a space separated identifier that
is the name of the instruction.


The name may optionally be followed by arguments. Most instructions use a syntax for
options, arguments and quoting that resembles the unix shell.

The exact syntax depends on the particular instruction.


An instruction may span several lines, as this form of {instruction[stdout]} does:


```
stdout {CONTENTS_EQUALS_ARGUMENT} <<EOF
Hello, World!
EOF
```
"""

INSTRUCTIONS_DESCRIPTION_DOC = """\
An instruction may optionally be preceded by a "description" -
a free text within quotes that is
displayed together with the instruction source line in error messages.

The purpose of a description is to describe the meaning of the instruction using
text that is easier to understand than the source line.

A description is a quoted string using shell syntax.


For example, a free text may be easier to understand than a shell command:


```
{phase[assert]:syntax}

'PATH should contain /usr/local/bin'

$ tr ':' '\\n' < ../result/stdout | grep '^/usr/local/bin$'
```


A description may span several lines.
"""

OTHER_DOC = """\
Lines beginning with "{line_comment_char}" are comments.

Comments may only appear on lines between instructions and phase headers.


Empty lines that are not part of an instruction are ignored.


Empty lines, and lines with comment line syntax, may be part of instruction and
the {phase[act]} phase, though,
as in the {instruction[stdout]} instruction here:


```
stdout {CONTENTS_EQUALS_ARGUMENT} <<EOF
this assertion expects 4 lines of output
{line_comment_char} this is the second line of the expected output

the above empty line is part of the expected output
EOF
```
"""

FILE_INCLUSION_DOC = """\
Parts of a test case can be put in an external file,
using the {file_inclusion_directive_in_text} directive:


```
{file_inclusion_directive} external-part-of-test-case.xly
```
"""
