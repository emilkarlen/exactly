from exactly_lib.definitions import formatting, misc_texts
from exactly_lib.definitions.entity import directives, concepts
from exactly_lib.definitions.entity.concepts import ACTOR_CONCEPT_INFO
from exactly_lib.definitions.formatting import AnyInstructionNameDictionary
from exactly_lib.definitions.primitives import string
from exactly_lib.definitions.test_case import phase_names
from exactly_lib.definitions.test_case.instructions import instruction_names
from exactly_lib.help.render import see_also
from exactly_lib.impls.types.condition import comparators
from exactly_lib.impls.types.string_matcher import matcher_options as contents_opts
from exactly_lib.section_document import defs
from exactly_lib.section_document.syntax import section_header, LINE_COMMENT_MARKER
from exactly_lib.tcfs import sds
from exactly_lib.test_case.phase_identifier import DEFAULT_PHASE
from exactly_lib.util.textformat.constructor import paragraphs, sections
from exactly_lib.util.textformat.section_target_hierarchy import hierarchies as h, generator
from exactly_lib.util.textformat.textformat_parser import TextParser


def root(header: str) -> generator.SectionHierarchyGenerator:
    tp = _text_parser()

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
                                            defs.INSTRUCTION_DESCRIPTION.plural.capitalize(),
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


def _text_parser() -> TextParser:
    return TextParser({
        'phase_declaration_for_NAME': section_header('NAME'),
        'instr': AnyInstructionNameDictionary(),
        'instruction': concepts.INSTRUCTION_CONCEPT_INFO.name,
        'instruction_description': defs.INSTRUCTION_DESCRIPTION,
        'description_delimiter': defs.DESCRIPTION_DELIMITER,
        'description_delimiter_char_name': defs.DESCRIPTION_DELIMITER_CHAR_NAME,
        'default_phase': phase_names.PHASE_NAME_DICTIONARY[DEFAULT_PHASE.identifier].syntax,
        'phase': phase_names.PHASE_NAME_DICTIONARY,
        'actor': formatting.concept_(ACTOR_CONCEPT_INFO),
        'CONTENTS_EQUALS_ARGUMENT': contents_opts.EQUALS_ARGUMENT,
        'CONTENTS_EMPTY_ARGUMENT': contents_opts.EMPTY_ARGUMENT,
        'line_comment_char': LINE_COMMENT_MARKER,
        'file_inclusion_directive_in_text': formatting.keyword(directives.INCLUDING_DIRECTIVE_INFO.singular_name),
        'file_inclusion_directive': directives.INCLUDING_DIRECTIVE_INFO.singular_name,
        'shell_command': formatting.misc_name_with_formatting(misc_texts.SHELL_COMMAND),
        'plain_string': misc_texts.PLAIN_STRING,
        'instruction__shell_cmd_line': instruction_names.SHELL_INSTRUCTION_NAME,
        'instruction__stdout': instruction_names.CONTENTS_OF_STDOUT_INSTRUCTION_NAME,
        'instruction__stderr': instruction_names.CONTENTS_OF_STDERR_INSTRUCTION_NAME,
        'instruction__exit_code': instruction_names.EXIT_CODE_INSTRUCTION_NAME,
        'INT_EQUALS_OPERATOR': comparators.EQ.name,
        'HERE_DOCUMENT_MARKER_PREFIX': string.HERE_DOCUMENT_MARKER_PREFIX,
        'MARKER': 'EOF',
        'sds_result_dir': sds.SUB_DIRECTORY__RESULT,
        'sds_stdout_file': sds.RESULT_FILE__STDOUT,
    })


_FILE_INCLUSION_SEE_ALSO_TARGETS = [
    concepts.DIRECTIVE_CONCEPT_INFO.cross_reference_target,
    directives.INCLUDING_DIRECTIVE_INFO.cross_reference_target,
]

_INTRO = """\
Syntax is line oriented.


Top level elements start at the beginning of a line,
and line ends mark the end of elements, although some may span several lines
(e.g. expressions inside parentheses).
"""

PHASES_DOC = """\
"{phase_declaration_for_NAME}" on a single line declares the start of phase NAME.

This line marks the start the {phase[assert]} phase, for example:


```
{phase[assert]:syntax}
```


The following lines will belong to this phase.


File contents before the first phase declaration belong to the default phase,
which is {default_phase}.


The order of the different phases in the test case file is irrelevant.
The phases are always executed in the same order,
regardless of the order they appear in the test case file.


A phase can be declared more than once.

Contents of multiple declarations are merged, and executed in the order it appears in the file.

Here, {instr[exit_code]} is executed before {instr[stderr]}:


```
{phase[assert]:syntax}

{instruction__exit_code} {INT_EQUALS_OPERATOR} 0

{phase[act]:syntax}

helloworld

{phase[assert]:syntax}

{instruction__stderr} {CONTENTS_EMPTY_ARGUMENT}
```
"""

PHASES_CONTENTS_DOC = """\
All phases except the {phase[act]} phase consist of a sequence of "{instruction:s}" (see below).


The contents of the {phase[act]} phase depends on which {actor} is used.

By default, it is expected to contain a single command line.
"""

INSTRUCTIONS_DOC = """\
{instruction:s/u} start at the beginning of the line with a space separated identifier that
is the name of the {instruction}.


The name may optionally be followed by arguments.
Most {instruction:s} use a syntax for options, arguments and quoting
that resembles the unix shell.
The order of options is relevant, though (unlike many unix tools).

The exact syntax depends on the particular {instruction}.


{instruction:a/u} may span several lines, as this form of {instr[stdout]} does:


```
{instruction__stdout} {CONTENTS_EQUALS_ARGUMENT} {HERE_DOCUMENT_MARKER_PREFIX}{MARKER}
Hello, World!
{MARKER}
```
"""

INSTRUCTIONS_DESCRIPTION_DOC = """\
{instruction:a/u} may optionally be preceded by {instruction_description:a/q} -
a free text that is displayed together with the {instruction} source code in error messages.

The purpose of {instruction_description:a} is to describe the meaning of the {instruction} using
text that is easier to understand than source code.


{instruction_description:a/u} is a {plain_string} within {description_delimiter_char_name:s} ({description_delimiter}).


For example, a free text may be easier to understand than {shell_command:a}:


```
{phase[assert]:syntax}

{description_delimiter}PATH should contain /usr/local/bin{description_delimiter}

{instruction__shell_cmd_line} tr ':' '\\n' < {sds_result_dir}/{sds_stdout_file} | grep '^/usr/local/bin$'
```


{instruction_description:a/u} may span several lines.
"""

OTHER_DOC = """\
Lines beginning with "{line_comment_char}" are comments.

Comments may only appear on lines between {instruction:s} and phase headers.


Empty lines that are not part of {instruction:a} are ignored.


Empty lines, and lines with comment line syntax, may be part of {instruction:s} and
the {phase[act]} phase, though,
as in the {instr[stdout]} {instruction} here:


```
{instruction__stdout} {CONTENTS_EQUALS_ARGUMENT} {HERE_DOCUMENT_MARKER_PREFIX}{MARKER}
this assertion expects 4 lines of output
{line_comment_char} this is the second line of the expected output

the empty line above is part of the expected output
{MARKER}
```
"""

FILE_INCLUSION_DOC = """\
Parts of a test case can be put in an external file,
using the {file_inclusion_directive_in_text} directive:


```
{file_inclusion_directive} external-part-of-test-case.xly
```
"""
