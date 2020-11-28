from typing import List

from exactly_lib.common.help.instruction_documentation_with_text_parser import \
    InstructionDocumentationWithTextParserBase
from exactly_lib.common.help.syntax_contents_structure import InvokationVariant, invokation_variant_from_args
from exactly_lib.common.instruction_setup import SingleInstructionSetup
from exactly_lib.common.report_rendering import text_docs
from exactly_lib.definitions import misc_texts, formatting
from exactly_lib.definitions.cross_ref.app_cross_ref import SeeAlsoTarget
from exactly_lib.definitions.entity import syntax_elements, concepts
from exactly_lib.impls.description_tree.tree_structured import WithCachedNodeDescriptionBase
from exactly_lib.impls.exception import pfh_exception
from exactly_lib.impls.instructions.assert_.utils import instruction_of_matcher
from exactly_lib.impls.text_render.header_rendering import unexpected_attribute__major_block
from exactly_lib.impls.types.integer_matcher import parse_integer_matcher
from exactly_lib.impls.types.matcher.impls import property_getters
from exactly_lib.impls.types.matcher.impls import property_matcher_describers
from exactly_lib.impls.types.matcher.impls.property_getters import PropertyGetterAdvConstant
from exactly_lib.impls.types.matcher.property_getter import PropertyGetterDdv, PropertyGetter, PropertyGetterAdv
from exactly_lib.impls.types.matcher.property_matcher import PropertyMatcherSdv
from exactly_lib.processing import exit_values
from exactly_lib.section_document.element_parsers import token_stream_parser
from exactly_lib.section_document.element_parsers.section_element_parsers import InstructionParser
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.source_location import FileSystemLocationInfo
from exactly_lib.tcfs.sds import SandboxDs
from exactly_lib.tcfs.tcds import TestCaseDs
from exactly_lib.test_case.hard_error import HardErrorException
from exactly_lib.test_case.phases.assert_ import AssertPhaseInstruction, WithAssertPhasePurpose
from exactly_lib.type_val_prims.description.tree_structured import StructureRenderer
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.str_ import str_constructor
from exactly_lib.util.textformat.structure.document import SectionContents


def setup(instruction_name: str) -> SingleInstructionSetup:
    return SingleInstructionSetup(
        Parser(),
        TheInstructionDocumentation(instruction_name))


_PROPERTY_NAME = misc_texts.EXIT_CODE.singular


class TheInstructionDocumentation(InstructionDocumentationWithTextParserBase,
                                  WithAssertPhasePurpose):
    def __init__(self, name: str):
        super().__init__(name, {
            'INTEGER_MATCHER': syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.argument.name,
            'EXIT_CODE': _PROPERTY_NAME,
            'action_to_check': formatting.concept_(concepts.ACTION_TO_CHECK_CONCEPT_INFO),
            'PASS': exit_values.EXECUTION__PASS.exit_identifier,
        })

    def single_line_description(self) -> str:
        return self._tp.format('Tests the {EXIT_CODE} of the {action_to_check}')

    def outcome(self) -> SectionContents:
        return self._tp.section_contents(_OUTCOME)

    def invokation_variants(self) -> List[InvokationVariant]:
        return [
            invokation_variant_from_args([
                syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.single_mandatory,
            ]),
        ]

    def see_also_targets(self) -> List[SeeAlsoTarget]:
        return [
            syntax_elements.INTEGER_MATCHER_SYNTAX_ELEMENT.cross_reference_target
        ]


class Parser(InstructionParser):
    def __init__(self):
        self._matcher_parser = parse_integer_matcher.parsers(False).full

    def parse(self,
              fs_location_info: FileSystemLocationInfo,
              source: ParseSource) -> AssertPhaseInstruction:
        with token_stream_parser.from_parse_source(source,
                                                   consume_last_line_if_is_at_eol_after_parse=True) as token_parser:
            matcher = self._matcher_parser.parse_from_token_parser(token_parser)

            property_matcher = PropertyMatcherSdv(
                matcher,
                property_getters.PropertyGetterSdvConstant(_ExitCodeGetterDdv()),
                property_matcher_describers.IdenticalToMatcher()
            )

            token_parser.report_superfluous_arguments_if_not_at_eol()

            return instruction_of_matcher.Instruction(
                property_matcher,
                unexpected_attribute__major_block(misc_texts.EXIT_CODE.singular),
            )


class _ExitCodeGetter(PropertyGetter[None, int], WithCachedNodeDescriptionBase):
    def __init__(self, sds: SandboxDs):
        super().__init__()
        self._sds = sds

    def _structure(self) -> StructureRenderer:
        return _PROPERTY_GETTER_STRUCTURE

    def get_from(self, model: None) -> int:
        sds = self._sds
        try:
            f = sds.result.exitcode_file.open()
        except IOError:
            rel_path = sds.relative_to_sds_root(sds.result.exitcode_file)
            err_msg = text_docs.single_line(
                str_constructor.FormatMap(
                    'Cannot read {exit_code} from file {file}',
                    {
                        'exit_code': _PROPERTY_NAME,
                        'file': rel_path,
                    }
                )
            )
            raise pfh_exception.PfhHardErrorException(err_msg)
        try:
            contents = f.read()
        except IOError:
            raise pfh_exception.PfhHardErrorException(
                text_docs.single_line(
                    str_constructor.Concatenate([
                        _FAILED_TO_READ_CONTENTS_FROM,
                        sds.result.exitcode_file,
                    ])
                ))
        finally:
            f.close()

        try:
            return int(contents)
        except ValueError:
            msg = text_docs.single_line(
                str_constructor.FormatMap(
                    'The contents of the file for {exit_code} ("{file}") is not an integer: "{contents}"',
                    {
                        'exit_code': _PROPERTY_NAME,
                        'file': sds.result.exitcode_file,
                        'contents': contents,
                    })
            )
            raise HardErrorException(msg)


class _ExitCodeGetterDdv(PropertyGetterDdv[None, int]):
    def structure(self) -> StructureRenderer:
        return _PROPERTY_GETTER_STRUCTURE

    def value_of_any_dependency(self, tcds: TestCaseDs) -> PropertyGetterAdv[None, int]:
        return PropertyGetterAdvConstant(_ExitCodeGetter(tcds.sds))


_PROPERTY_GETTER_STRUCTURE = renderers.header_only(_PROPERTY_NAME)

_OUTCOME = """\
{PASS} iff the {EXIT_CODE} of the {action_to_check} satisfies {INTEGER_MATCHER}.
"""

_FAILED_TO_READ_CONTENTS_FROM = 'Failed to read contents from '
