from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, SyntaxElementDescription
from exactly_lib.help.entities.syntax_elements.contents_structure import SyntaxElementDocumentation
from exactly_lib.help.utils.textformat_parser import TextParser
from exactly_lib.help_texts import instruction_arguments
from exactly_lib.help_texts.argument_rendering import cl_syntax
from exactly_lib.help_texts.entity import syntax_element
from exactly_lib.help_texts.entity import types
from exactly_lib.help_texts.entity.syntax_element import STRING_SYNTAX_ELEMENT
from exactly_lib.help_texts.names import formatting
from exactly_lib.instructions.utils.documentation import documentation_text
from exactly_lib.instructions.utils.documentation.relative_path_options_documentation import \
    relativity_options_paragraph
from exactly_lib.test_case_file_structure.path_relativity import PathRelativityVariants, RelOptionType
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem


class _Documentation(SyntaxElementDocumentation):
    def __init__(self):
        super().__init__(syntax_element.PATH_SYNTAX_ELEMENT)

        self._string_name = a.Named(STRING_SYNTAX_ELEMENT.singular_name)
        self._relativity_name = instruction_arguments.RELATIVITY_ARGUMENT

        self._parser = TextParser({
            'RELATIVITY_OPTION': self._relativity_name.name,
            'PATH_STRING': self._string_name.name,
            'posix_syntax': documentation_text.POSIX_SYNTAX,
            'string_type': formatting.keyword(types.STRING_TYPE_INFO.name.singular),
            'string_syntax_element': STRING_SYNTAX_ELEMENT.singular_name,
        })

    def invokation_variants(self) -> list:
        return [
            InvokationVariant(
                cl_syntax.cl_syntax_for_args(self._cl_arguments())
            )
        ]

    def syntax_element_descriptions(self) -> list:
        return [
            self._string_sed(),
            self._relativity_sed(),
        ]

    def main_description_rest(self) -> list:
        return self._parser.fnap(_MAIN_DESCRIPTION_REST)

    def see_also_targets(self) -> list:
        return [
            STRING_SYNTAX_ELEMENT.cross_reference_target,
        ]

    def _relativity_sed(self) -> SyntaxElementDescription:
        description_rest = self._parser.fnap(_RELATIVITY_DESCRIPTION_REST)
        description_rest.append(self._relativity_options_paragraph())

        return SyntaxElementDescription(self._relativity_name.name,
                                        description_rest)

    def _string_sed(self) -> SyntaxElementDescription:
        return SyntaxElementDescription(self._string_name.name,
                                        self._parser.fnap(_STRING_DESCRIPTION_REST))

    def _cl_arguments(self) -> list:
        return [
            a.Single(a.Multiplicity.OPTIONAL,
                     self._relativity_name),
            a.Single(a.Multiplicity.MANDATORY,
                     self._string_name),

        ]

    def _relativity_options_paragraph(self) -> ParagraphItem:
        variants = PathRelativityVariants(RelOptionType, True)
        return relativity_options_paragraph(self._string_name.name,
                                            variants)


DOCUMENTATION = _Documentation()

_MAIN_DESCRIPTION_REST = """\
If {PATH_STRING} is an absolute path, then {RELATIVITY_OPTION} must not be given.

If {PATH_STRING} is a relative path, then if {RELATIVITY_OPTION} is ...


  * given
  
    {PATH_STRING} is relative to the directory specified by {RELATIVITY_OPTION}

  * not given
  
    {PATH_STRING} is relative to the default relativity root directory,


The default relativity depends on the instruction,
and also on the argument position of the instruction. 
"""

_STRING_DESCRIPTION_REST = """\
A relative or absolute path, using {posix_syntax}.


It is a value of type {string_type}, and thus uses {string_syntax_element} syntax.
"""

_RELATIVITY_DESCRIPTION_REST = """\
An option that specifies the directory that {PATH_STRING} is relative to.


The available relativities depends on the instruction,
and also on the argument position of the instruction. 


Forms:
"""
