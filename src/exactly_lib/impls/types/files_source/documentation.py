from typing import Sequence, Optional, List

from exactly_lib.common.help import documentation_text
from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, SyntaxElementDescription, \
    InvokationVariant
from exactly_lib.definitions import formatting, misc_texts, file_types
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.cross_ref.name_and_cross_ref import cross_reference_id_list
from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.definitions.entity.syntax_elements import SyntaxElementInfo
from exactly_lib.impls.types.expression import grammar
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.str_ import english_text
from exactly_lib.util.textformat.structure.core import ParagraphItem
from exactly_lib.util.textformat.textformat_parser import TextParser
from . import syntax
from .defs import FileType, ModificationType


class CopySyntaxDescription(grammar.PrimitiveDescriptionWithNameAsInitialSyntaxToken):
    def __init__(self, path_argument: SyntaxElementInfo):
        self._path_argument = path_argument
        self._argument_usage_list = (path_argument.single_mandatory,)

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return self._argument_usage_list

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        tp = TextParser({
            'dir_file_type': file_types.DIRECTORY,
            'SRC_PATH': self._path_argument.singular_name,
        })
        return tp.fnap(_DESCRIPTION_OF_COPY)

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.PATH_SYNTAX_ELEMENT,
        ])


class FileListSyntaxDescription(grammar.PrimitiveDescriptionWithSyntaxElementAsInitialSyntaxToken):
    def __init__(self):
        super().__init__(_FILE_LIST_SYNTAX_ELEMENT_NAME)

    @property
    def argument_usage_list(self) -> Sequence[a.ArgumentUsage]:
        return ()

    @property
    def description_rest(self) -> Sequence[ParagraphItem]:
        return _TP.fnap(_FILE_LIST__HEADER)

    @property
    def syntax_elements(self) -> Sequence[SyntaxElementDescription]:
        return (
            _file_list_sed(_FILE_LIST_SYNTAX_ELEMENT_NAME),
            _file_spec_sed(),
            _file_name_sed(),
        )

    @property
    def see_also_targets(self) -> Sequence[SeeAlsoTarget]:
        return cross_reference_id_list([
            syntax_elements.STRING_SYNTAX_ELEMENT,
            syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT,
        ])


def _file_list_sed(name: str) -> SyntaxElementDescription:
    return SyntaxElementDescription(
        name,
        (),
        [
            invokation_variant_from_args([
                a.Single(a.Multiplicity.MANDATORY, a.Constant(syntax.FILE_LIST_BEGIN)),
                a.Single(a.Multiplicity.ONE_OR_MORE, a.Named(syntax.FILE_SPEC__SE_STR)),
                a.Single(a.Multiplicity.MANDATORY, a.Constant(syntax.FILE_LIST_END)),
            ],
                _TP.fnap(_FILE_LIST__DESCRIPTION_REST)),
        ]
    )


def _file_spec_sed() -> SyntaxElementDescription:
    return SyntaxElementDescription(
        syntax.FILE_SPEC__SE_STR,
        _TP.fnap(_FILE_SPEC_DESCRIPTION_REST),
        [
            file_spec.invokation_variant(_FILE_SPEC_RENDERING_ENV)
            for file_spec in _file_spec_forms()
        ]
    )


class FileSpecRenderingEnvironment:
    def __init__(self,
                 file_name_arg: a.ArgumentUsage,
                 include_file_type: bool,
                 tp: TextParser,
                 ):
        self.file_name_arg = file_name_arg
        self.include_file_type = include_file_type
        self.tp = tp


class FileSpecForm:
    def __init__(self,
                 file_type: FileType,
                 modification: Optional[ModificationType],
                 contents_arguments: Optional[SyntaxElementInfo],
                 description_tmpl: str,
                 path_existence_tmpl: str,
                 ):
        self.file_type = file_type
        self.modification = modification
        self.contents_arguments = contents_arguments
        self.description_tmpl = description_tmpl
        self.path_existence_tmpl = path_existence_tmpl

    def invokation_variant(self, environment: FileSpecRenderingEnvironment) -> InvokationVariant:
        arguments = []
        if environment.include_file_type:
            arguments += [self._file_type_arg()]

        arguments += [environment.file_name_arg]
        arguments += self._modification_args()
        arguments += self._contents_args()
        description = environment.tp.fnap(self.description_tmpl)
        description += environment.tp.fnap(self.path_existence_tmpl)

        return invokation_variant_from_args(
            arguments,
            description,
        )

    def _file_type_arg(self) -> a.ArgumentUsage:
        return a.Single(a.Multiplicity.MANDATORY,
                        a.Constant(syntax.FILE_TYPE_TOKENS[self.file_type]))

    def _modification_args(self) -> List[a.ArgumentUsage]:
        if self.modification is None:
            return []
        else:
            return [
                a.Single(a.Multiplicity.MANDATORY,
                         a.Constant(syntax.MODIFICATION_VARIANT_TOKENS[self.modification]))
            ]

    def _contents_args(self) -> List[a.ArgumentUsage]:
        return (
            []
            if self.contents_arguments is None
            else
            [self.contents_arguments.single_mandatory]
        )


def _file_spec_forms() -> Sequence[FileSpecForm]:
    return file_spec_forms__regular() + file_spec_forms__dir()


def file_spec_forms__regular() -> List[FileSpecForm]:
    return [
        FileSpecForm(
            FileType.REGULAR,
            None,
            None,
            _FILE_SPEC__REGULAR__IMPLICIT_EMPTY,
            _PATH__MUST_NOT_EXIST,
        ),
        FileSpecForm(
            FileType.REGULAR,
            ModificationType.CREATE,
            syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT,
            _FILE_SPEC__REGULAR__CREATE,
            _PATH__MUST_NOT_EXIST,
        ),
        FileSpecForm(
            FileType.REGULAR,
            ModificationType.APPEND,
            syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT,
            _FILE_SPEC__REGULAR__APPEND,
            _PATH__MUST_EXIST__REGULAR,
        ),
    ]


def file_spec_forms__dir() -> List[FileSpecForm]:
    return [
        FileSpecForm(
            FileType.DIR,
            None,
            None,
            _FILE_SPEC__DIR__IMPLICIT_EMPTY,
            _PATH__MUST_NOT_EXIST,
        ),
        FileSpecForm(
            FileType.DIR,
            ModificationType.CREATE,
            syntax_elements.FILES_SOURCE_SYNTAX_ELEMENT,
            _FILE_SPEC__DIR__CREATE,
            _PATH__MUST_NOT_EXIST,
        ),
        FileSpecForm(
            FileType.DIR,
            ModificationType.APPEND,
            syntax_elements.FILES_SOURCE_SYNTAX_ELEMENT,
            _FILE_SPEC__DIR__APPEND,
            _PATH__MUST_EXIST__DIR,
        ),
    ]


def _file_name_sed() -> SyntaxElementDescription:
    return SyntaxElementDescription(
        syntax.FILE_NAME.name,
        (),
        [invokation_variant_from_args([syntax_elements.STRING_SYNTAX_ELEMENT.single_mandatory])],
        _file_name_description(),
    )


def _file_name_description() -> Sequence[ParagraphItem]:
    ret_val = _TP.fnap(_FILE_NAME_DESCRIPTION_REST)
    ret_val += _TP.fnap(INTERMEDIATE_DIRS_ARE_CREATED)
    return ret_val


_FILE_SPEC__REGULAR__IMPLICIT_EMPTY = """\
Creates an empty {regular_file_type}.
"""

_FILE_SPEC__REGULAR__CREATE = """\
Creates {regular_file_type:a} with contents given by {regular_contents_type}.
"""

_FILE_SPEC__REGULAR__APPEND = """\
Appends contents to an existing {regular_file_type}.


Contents is given by {regular_contents_type}.
"""

_FILE_SPEC__DIR__IMPLICIT_EMPTY = """\
Creates an empty {dir_file_type}.
"""

_FILE_SPEC__DIR__CREATE = """\
Creates {dir_file_type:a} with contents given by {dir_contents_type}.
"""

_FILE_SPEC__DIR__APPEND = """\
Adds contents to an existing {dir_file_type}.


Contents is given by {dir_contents_type}.
"""

_PATH__MUST_NOT_EXIST = """\
The path must not exist.
"""

_PATH__MUST_EXIST__REGULAR = """\
The path must be an existing {regular_file_type}.
"""

_PATH__MUST_EXIST__DIR = """\
The path must be an existing {dir_file_type}.
"""

_FILE_LIST_SYNTAX_ELEMENT_NAME = 'FILE-LIST'

_FILE_LIST__HEADER = """\
A sequence of files, created or modified, relative the populated {dir_file_type}.
"""

_FILE_LIST__DESCRIPTION_REST = """\
There can be only one {FILE_SPEC} per line.


Files are created/modified in the order listed.


{SPACE_SEPARATION_PARAGRAPH} 
"""

_FILE_SPEC_DESCRIPTION_REST = """\
Creation or modification of a named file, relative the populated {dir_file_type}.


If given, {MODIFIERS} must appear on the same line as {FILE_NAME}.
"""

_FILE_NAME_DESCRIPTION_REST = """\
A relative path, using {posix_syntax}.


The path is relative the populated {dir_file_type}.


Must not contain {parent_dir}.
"""

INTERMEDIATE_DIRS_ARE_CREATED = """\
Intermediate {dir_file_type:s} as created, if required.
"""

_SPACE_SEPARATION_PARAGRAPH = 'All parts must be separated by {whitespace}.'

_TP = TextParser({
    'FILE_NAME': syntax.FILE_NAME.name,
    'FILE_SPEC': syntax.FILE_SPEC__SE_STR,
    'MODIFIERS': english_text.and_sequence([
        formatting.keyword(token)
        for token in syntax.MODIFICATION_VARIANT_TOKENS.values()
    ]),
    'parent_dir': formatting.string_constant('..'),
    'posix_syntax': documentation_text.POSIX_SYNTAX,
    'SPACE_SEPARATION_PARAGRAPH': _SPACE_SEPARATION_PARAGRAPH.format(whitespace=misc_texts.WHITESPACE),
    'dir_file_type': file_types.DIRECTORY,
    'regular_file_type': file_types.REGULAR,
    'regular_contents_type': syntax_elements.STRING_SOURCE_SYNTAX_ELEMENT.singular_name,
    'dir_contents_type': syntax_elements.FILES_SOURCE_SYNTAX_ELEMENT.singular_name,
})

_FILE_SPEC_RENDERING_ENV = FileSpecRenderingEnvironment(
    syntax.FILE_NAME__ARG,
    True,
    _TP,
)

_DESCRIPTION_OF_COPY = """\
A copy of the contents of {SRC_PATH} (recursive).


{SRC_PATH} must be an existing {dir_file_type}.
"""
