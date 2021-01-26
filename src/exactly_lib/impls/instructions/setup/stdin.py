from typing import Sequence, List, Optional

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import invokation_variant_from_args, InvokationVariant, \
    SyntaxElementDescription
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.definitions import instruction_arguments, formatting, syntax_descriptions
from exactly_lib.definitions.argument_rendering.path_syntax import the_path_of
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.impls import file_properties
from exactly_lib.impls.file_properties import FileType
from exactly_lib.impls.instructions.setup.utils.instruction_utils import InstructionWithFileRefsBase
from exactly_lib.impls.types.path.path_check import PathCheck, PathCheckDdvValidator, PathCheckDdv
from exactly_lib.impls.types.string_or_path import parse_string_or_path
from exactly_lib.impls.types.string_or_path.doc import StringOrHereDocOrFile
from exactly_lib.impls.types.string_or_path.primitive import SourceType
from exactly_lib.impls.types.string_source.factory import RootStringSourceFactory
from exactly_lib.section_document.element_parsers.section_element_parsers import \
    InstructionParserWithoutSourceFileLocationInfo
from exactly_lib.section_document.element_parsers.token_stream_parser import from_parse_source, \
    TokenParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.symbol.sdv_structure import SymbolUsage
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.app_env import ApplicationEnvironment
from exactly_lib.test_case.os_services import OsServices
from exactly_lib.test_case.phases.act.adv_w_validation import AdvWValidation
from exactly_lib.test_case.phases.instruction_environment import InstructionEnvironmentForPostSdsStep
from exactly_lib.test_case.phases.setup.instruction import SetupPhaseInstruction
from exactly_lib.test_case.phases.setup.settings_builder import SetupSettingsBuilder
from exactly_lib.test_case.result import sh, svh
from exactly_lib.type_val_deps.types.path.path_ddv import PathDdv
from exactly_lib.type_val_deps.types.path.path_sdv import PathSdv
from exactly_lib.type_val_deps.types.string_.string_sdv import StringSdv
from exactly_lib.type_val_prims.string_source.string_source import StringSource
from exactly_lib.util.cli_syntax.elements import argument as a
from exactly_lib.util.textformat.textformat_parser import TextParser


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


RELATIVITY_OPTIONS_CONFIGURATION = parse_string_or_path.CONFIGURATION


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase):
    def __init__(self, name: str):
        super().__init__(name, {})
        self.path_arg = syntax_elements.PATH_SYNTAX_ELEMENT.argument
        self.string_or_here_doc_or_file_arg = StringOrHereDocOrFile(
            self.path_arg.name,
            instruction_arguments.RELATIVITY_ARGUMENT.name,
            RELATIVITY_OPTIONS_CONFIGURATION,
            the_path_of('the file that will be the contents of stdin.')
        )
        self._tp = TextParser({
            'HERE_DOCUMENT': formatting.syntax_element_(syntax_elements.HERE_DOCUMENT_SYNTAX_ELEMENT),
            'FILE': RELATIVITY_OPTIONS_CONFIGURATION.argument_syntax_name,
            'atc': formatting.concept(concepts.ACTION_TO_CHECK_NAME.singular),
            'Sym_refs_are_not_substituted': syntax_descriptions.symbols_are_not_substituted_in(
                'the file ' + RELATIVITY_OPTIONS_CONFIGURATION.argument_syntax_name
            ),
        })

    def single_line_description(self) -> str:
        return self._tp.format('Sets the contents of stdin for the {atc}')

    def invokation_variants(self) -> Sequence[InvokationVariant]:
        args = [a.Single(a.Multiplicity.MANDATORY, a.Constant(instruction_arguments.ASSIGNMENT_OPERATOR)),
                self.string_or_here_doc_or_file_arg.argument_usage(a.Multiplicity.MANDATORY),
                ]
        return [
            invokation_variant_from_args(args,
                                         self._tp.fnap(_DESCRIPTION_REST)),
        ]

    def syntax_element_descriptions(self) -> Sequence[SyntaxElementDescription]:
        return self.string_or_here_doc_or_file_arg.syntax_element_descriptions()

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return self.string_or_here_doc_or_file_arg.see_also_targets()


class Parser(InstructionParserWithoutSourceFileLocationInfo):
    def parse_from_source(self, source: ParseSource) -> SetupPhaseInstruction:
        with from_parse_source(source, consume_last_line_if_is_at_eof_after_parse=True) as token_parser:
            assert isinstance(token_parser, TokenParser), 'Must have a TokenParser'  # Type info for IDE

            token_parser.consume_mandatory_constant_string_that_must_be_unquoted_and_equal(
                [instruction_arguments.ASSIGNMENT_OPERATOR],
                lambda x: x
            )
            string_or_path = parse_string_or_path.parse_from_token_parser(token_parser,
                                                                          RELATIVITY_OPTIONS_CONFIGURATION)
            if string_or_path.source_type is not SourceType.HERE_DOC:
                token_parser.report_superfluous_arguments_if_not_at_eol()
                token_parser.consume_current_line_as_string_of_remaining_part_of_current_line()

            if string_or_path.is_path:
                return _InstructionForFile(string_or_path.path_sdv)
            else:
                return _InstructionForString(string_or_path.string_sdv)


class _InstructionForString(SetupPhaseInstruction):
    def __init__(self, stdin_contents: StringSdv):
        self.stdin_contents = stdin_contents

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.stdin_contents.references

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder,
             ) -> sh.SuccessOrHardError:
        contents = self.stdin_contents.resolve_value_of_any_dependency(
            environment.path_resolving_environment_pre_or_post_sds)

        settings_builder.stdin = _StdinOfString(contents)

        return sh.new_sh_success()


class _InstructionForFile(InstructionWithFileRefsBase):
    def __init__(self, stdin_contents: PathSdv):
        super().__init__((PathCheck(stdin_contents,
                                    file_properties.must_exist_as(FileType.REGULAR)),))
        self._file_path_check = PathCheck(stdin_contents,
                                          file_properties.must_exist_as(FileType.REGULAR))
        self.stdin_contents = stdin_contents

    def symbol_usages(self) -> Sequence[SymbolUsage]:
        return self.stdin_contents.references

    def validate_post_setup(self,
                            environment: InstructionEnvironmentForPostSdsStep,
                            ) -> svh.SuccessOrValidationErrorOrHardError:
        return svh.new_svh_success()

    def main(self,
             environment: InstructionEnvironmentForPostSdsStep,
             os_services: OsServices,
             settings_builder: SetupSettingsBuilder,
             ) -> sh.SuccessOrHardError:
        path_ddv = self.stdin_contents.resolve(environment.symbols)

        settings_builder.stdin = _StdinOfFile(path_ddv, environment.tcds)

        return sh.new_sh_success()


class _StdinOfFile(AdvWValidation[StringSource]):
    def __init__(self,
                 path: PathDdv,
                 tcds: TestCaseDs,
                 ):
        self._path = path
        self._tcds = tcds

    def validate(self) -> Optional[TextRenderer]:
        path_validator = PathCheckDdvValidator(
            PathCheckDdv(self._path, file_properties.must_exist_as(FileType.REGULAR))
        )
        return path_validator.validate_post_sds_if_applicable(self._tcds)

    def resolve(self, environment: ApplicationEnvironment) -> StringSource:
        string_source_factory = RootStringSourceFactory(environment.tmp_files_space)
        return string_source_factory.of_file__described(
            self._path.value_of_any_dependency__d(self._tcds)
        )


class _StdinOfString(AdvWValidation[StringSource]):
    def __init__(self, contents: str):
        self._contents = contents

    def validate(self) -> Optional[TextRenderer]:
        return None

    def resolve(self, environment: ApplicationEnvironment) -> StringSource:
        string_source_factory = RootStringSourceFactory(environment.tmp_files_space)
        return string_source_factory.of_const_str(self._contents)


_DESCRIPTION_REST = """\
Sets stdin to be the contents of a string, {HERE_DOCUMENT} or file.


{Sym_refs_are_not_substituted}
"""
