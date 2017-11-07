from exactly_lib import program_info
from exactly_lib.help.entities.concepts.contents_structure import PlainConceptDocumentation
from exactly_lib.help.entities.types import all_types
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.entity.concepts import SYMBOL_CONCEPT_INFO, TYPE_CONCEPT_INFO
from exactly_lib.help_texts.names import formatting
from exactly_lib.help_texts.test_case.instructions import instruction_names
from exactly_lib.help_texts.type_system import TYPE_INFO_DICT
from exactly_lib.test_case_utils.parse.symbol_syntax import symbol_reference_syntax_for_name
from exactly_lib.type_system.value_type import ValueType
from exactly_lib.util.cli_syntax import option_syntax
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import structures as docs
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.structure.document import SectionContents


class _SymbolConcept(PlainConceptDocumentation):
    def __init__(self):
        super().__init__(SYMBOL_CONCEPT_INFO)
        list_symbol_name = 'LIST_SYMBOL'
        file_trans_symbol_name = 'REPLACE_ID'
        symbol_names = [
            list_symbol_name,
            file_trans_symbol_name,
        ]
        self._parser = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'symbol': SYMBOL_CONCEPT_INFO.singular_name,
            'data': all_types.DATA_TYPE_CATEGORY_NAME,
            'logic': all_types.LOGIC_TYPE_CATEGORY_NAME,
            'define_symbol': formatting.InstructionName(instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME),
            'def': instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME,

            'string_type': TYPE_INFO_DICT[ValueType.STRING].type_name,
            'list_type': TYPE_INFO_DICT[ValueType.LIST].type_name,
            'file_trans_type': TYPE_INFO_DICT[ValueType.LINES_TRANSFORMER].type_name,
            'max_type_width': max(map(lambda type_info: len(type_info.type_name),
                                      TYPE_INFO_DICT.values())),
            'LIST_SYMBOL': list_symbol_name,
            'FILE_TRANS_SYMBOL': file_trans_symbol_name,
            'max_symbol_name_width': max(map(len, symbol_names)),
            'ref_syntax_of_symbol_name': symbol_reference_syntax_for_name('symbol_name'),

            'exists_file': instruction_names.EXECUTION_MODE_INSTRUCTION_NAME,

            'stdout': instruction_names.CONTENTS_OF_STDOUT_INSTRUCTION_NAME,
            'transformed': instruction_arguments.LINES_TRANSFORMATION_ARGUMENT,
        })

    def purpose(self) -> DescriptionWithSubSections:
        rest_paragraphs = self._parser.fnap(_REST_DESCRIPTION)
        sub_sections = [
            docs.section('Definition',
                         self._parser.fnap(_DEFINITION)),
            docs.section('Reference',
                         self._reference_paragraphs()),
        ]
        return DescriptionWithSubSections(self.single_line_description(),
                                          SectionContents(rest_paragraphs,
                                                          sub_sections))

    def see_also_targets(self) -> list:
        return [
            TYPE_CONCEPT_INFO.cross_reference_target,
        ]

    def _reference_paragraphs(self) -> list:
        from exactly_lib.test_case_utils.lines_transformer.parse_lines_transformer import SELECT_TRANSFORMER_NAME
        from exactly_lib.instructions.assert_.utils.file_contents_resources import EMPTINESS_CHECK_ARGUMENT
        from exactly_lib.instructions.assert_.utils.file_contents.instruction_options import EQUALS_ARGUMENT

        from exactly_lib.test_case_utils.parse.parse_here_doc_or_file_ref import FILE_ARGUMENT_OPTION
        from exactly_lib.help_texts.file_ref import REL_symbol_OPTION
        part_2_parser = TextParser({
            'program_name': formatting.program_name(program_info.PROGRAM_NAME),
            'symbol': SYMBOL_CONCEPT_INFO.singular_name,

            'def': instruction_names.SYMBOL_DEFINITION_INSTRUCTION_NAME,

            'string_type': TYPE_INFO_DICT[ValueType.STRING].type_name,
            'list_type': TYPE_INFO_DICT[ValueType.LIST].type_name,
            'max_type_width': max(map(lambda value_type: len(TYPE_INFO_DICT[value_type].type_name),
                                      [ValueType.LIST,
                                       ValueType.STRING])),

            'ref_syntax_of_symbol_name': symbol_reference_syntax_for_name('SYMBOL_NAME'),

            'stdout': instruction_names.CONTENTS_OF_STDOUT_INSTRUCTION_NAME,
            'transformed': instruction_arguments.WITH_TRANSFORMED_CONTENTS_OPTION,
            'select_transformer': SELECT_TRANSFORMER_NAME,
            'not': instruction_arguments.NEGATION_ARGUMENT_STR,
            'empty': EMPTINESS_CHECK_ARGUMENT,
            'equals': EQUALS_ARGUMENT,
            'file_option': option_syntax.option_syntax(FILE_ARGUMENT_OPTION),
            'rel_option': REL_symbol_OPTION,
            'ref_syntax_of_dir_name_symbol': symbol_reference_syntax_for_name('DIR_NAME_SYMBOL'),
            'ref_syntax_of_base_name_symbol': symbol_reference_syntax_for_name('BASE_NAME_SYMBOL'),
            'ref_syntax_of_2nd_element_symbol': symbol_reference_syntax_for_name('STRING_SYMBOL'),

            'special_syntax_with_invalid_symbol_name': symbol_reference_syntax_for_name('NOT/A_SYMBOL_NAME'),
            'special_syntax_with_valid_symbol_name_but_invalid_delimiter':
                symbol_reference_syntax_for_name('VALID_SYMBOL_NAME')[:-1],
            'special_syntax_with_invalid_space': symbol_reference_syntax_for_name('SYMBOL_NAME '),
        })

        ret_val = self._parser.fnap(_REFERENCE_1)
        ret_val.append(_symbol_reference_syntax_table())
        ret_val += part_2_parser.fnap(_REFERENCE_2)
        return ret_val


SYMBOL_CONCEPT = _SymbolConcept()

_REST_DESCRIPTION = """\
A {symbol} corresponds to a named constant, found in most programming languages.


Every {symbol} has a type according to {program_name}'s type system.


A symbol name must consist of only alphanumerical characters and underscore.
"""

_DEFINITION = """\
A {symbol} is defined by the {define_symbol} instruction:


```
{def} {string_type} SYMBOL_NAME = "the symbol value"
```


This defines a symbol SYMBOL_NAME to be the value "the symbol value",
which is a value of type {string_type}.


The type must be given explicitly.

For example:


```
{def} {string_type: <{max_type_width}} {LIST_SYMBOL: <{max_symbol_name_width}} = first second "the third"

{def} {file_trans_type: <{max_type_width}} {FILE_TRANS_SYMBOL: <{max_symbol_name_width}} = replace [0-9]{{10}} ID
```
"""

_REFERENCE_1 = """\
A {symbol} must be defined before it is referenced.


A {symbol} reference may appear as an instruction argument,
in most places where an argument of a certain type is expected.


There are two forms of {symbol} references:
"""


def _symbol_reference_syntax_table() -> ParagraphItem:
    return docs.first_column_is_header_table([
        [
            docs.text_cell('Plain symbol name'),
            docs.text_cell('SYMBOL_NAME'),
        ],
        [
            docs.text_cell('Special syntax'),
            docs.text_cell(symbol_reference_syntax_for_name('SYMBOL_NAME')),
        ],

    ],
        ' : ')


_REFERENCE_2 = """\
The special syntax is designed to reduce the risk of clashes
with the syntax of other programming languages and shell script, e.g.

This is important since {program_name} has limited capabilities for escaping and quoting.


Also, strings that resemble the special syntax will not be considered as errors,
since it is assumed that these strings might have the syntax needed for a different purpose.

For example, the following strings does not constitute {symbol} references,
and {program_name} will not complain:


```
{special_syntax_with_invalid_symbol_name}
{special_syntax_with_invalid_space}
{special_syntax_with_valid_symbol_name_but_invalid_delimiter}
```


The plain symbol name is used when a {symbol} reference is unambiguous.
Otherwise, the special syntax is needed.

For example:


```
{def} {string_type: <{max_type_width}} S = "reference to {ref_syntax_of_symbol_name}"

{def} {list_type: <{max_type_width}} L = first {ref_syntax_of_2nd_element_symbol} "third element"

{stdout} {transformed} ( {select_transformer} LINE_MATCHER_SYMBOL ) {not} {empty}

{stdout} {equals} {file_option} {rel_option} PATH_SYMBOL {ref_syntax_of_dir_name_symbol}/{ref_syntax_of_base_name_symbol}
```
"""
