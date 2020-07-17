from typing import Sequence

from exactly_lib.common.help.syntax_contents_structure import SyntaxElementDescription, invokation_variant_from_args
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.test_case_utils.matcher.impls.run_program import documentation
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser


class RunSyntaxDescription(documentation.SyntaxDescriptionBase):
    _ARG_POS = a.Named('PATH-ARGUMENT-POSITION')

    def __init__(self):
        self.__tp = None

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return [
            a.Single(a.Multiplicity.OPTIONAL, self._ARG_POS),
            syntax_elements.PROGRAM_SYNTAX_ELEMENT.single_mandatory
        ]

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        from exactly_lib.definitions.primitives import file_matcher
        return [
            SyntaxElementDescription(
                self._ARG_POS.name,
                self._tp().fnap(_PATH_ARG_POS__DESCRIPTION),
                [
                    invokation_variant_from_args(
                        [a.Single(a.Multiplicity.MANDATORY, file_matcher.PROGRAM_ARG_OPTION__LAST)],
                        self._tp().fnap(_PATH_ARG_POS__LAST__DESCRIPTION)
                    ),
                    invokation_variant_from_args(
                        [a.Single(a.Multiplicity.MANDATORY, file_matcher.PROGRAM_ARG_OPTION__MARKER)],
                        self._tp().fnap(_PATH_ARG_POS__MARKER__DESCRIPTION)
                    ),
                ]
            )
        ]

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return self._tp().fnap(_MATCHER__DESCRIPTION)

    def _tp(self) -> TextParser:
        if self.__tp is None:
            from exactly_lib.definitions.entity import types
            from exactly_lib.definitions import matcher_model
            from exactly_lib.definitions import formatting
            from exactly_lib.definitions import misc_texts
            from exactly_lib.definitions.primitives import file_matcher
            self.__tp = TextParser({
                'MODEL': matcher_model.FILE_MATCHER_MODEL,
                'PATH_ARGUMENT_POSITION': formatting.syntax_element(self._ARG_POS.name),
                'PATH_ARG_MARKER': formatting.syntax_element(file_matcher.PROGRAM_ARG_OPTION__MARKER.argument),
                'program': types.PROGRAM_TYPE_INFO.name,
                'PROGRAM': syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
                'exit_code': misc_texts.EXIT_CODE,
            })

        return self.__tp


_MATCHER__DESCRIPTION = """\
Runs {program:a}. Matches iff the {exit_code} is 0.


The path of the {MODEL} to match is given as an argument
according to {PATH_ARGUMENT_POSITION}, if given,
or as the last argument, if {PATH_ARGUMENT_POSITION} is not given.


Transformations of the output from {PROGRAM} are ignored.
"""

_PATH_ARG_POS__DESCRIPTION = """\
Specifies which argument(s) to the {program} that will be
the path of the {MODEL}.
"""

_PATH_ARG_POS__LAST__DESCRIPTION = """\
The path of the {MODEL} will be the last argument to {PROGRAM}.
"""

_PATH_ARG_POS__MARKER__DESCRIPTION = """\
The path of the {MODEL} will replace every argument to {PROGRAM}
that equals {PATH_ARG_MARKER}.
"""
