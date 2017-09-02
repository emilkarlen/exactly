from exactly_lib.help import header_texts
from exactly_lib.help.program_modes.help.cli_syntax import HelpCliSyntaxDocumentation
from exactly_lib.help.utils.cli_program.cli_program_documentation_rendering import \
    ProgramDocumentationSectionContentsRenderer
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment
from exactly_lib.help.utils.rendering.section_hierarchy_rendering import SectionHierarchyGenerator, leaf, parent
from exactly_lib.help_texts import cross_reference_id as cross_ref
from exactly_lib.util.textformat.structure import document as doc


def generator(header: str) -> SectionHierarchyGenerator:
    return parent(
        header,
        [],
        [
            ('cli-syntax',
             leaf(header_texts.COMMAND_LINE_SYNTAX,
                  ProgramDocumentationSectionContentsRenderer(HelpCliSyntaxDocumentation()))
             ),
        ]
    )


class HtmlDocGeneratorForHelpHelp:
    def __init__(self, rendering_environment: RenderingEnvironment):
        self.rendering_environment = rendering_environment

    def apply(self, targets_factory: cross_ref.CustomTargetInfoFactory) -> (list, doc.SectionContents):
        cli_syntax_targets_factory = cross_ref.sub_component_factory('cli-syntax',
                                                                     targets_factory)
        cli_syntax_target = cli_syntax_targets_factory.root(header_texts.COMMAND_LINE_SYNTAX)
        cli_syntax_contents = self._cli_syntax_contents()

        ret_val_contents = doc.SectionContents(
            [],
            [
                doc.Section(cli_syntax_target.anchor_text(),
                            cli_syntax_contents),
            ]
        )
        ret_val_targets = [
            cross_ref.TargetInfoNode(cli_syntax_target, []),
        ]
        return ret_val_targets, ret_val_contents

    def _cli_syntax_contents(self) -> doc.SectionContents:
        renderer = ProgramDocumentationSectionContentsRenderer(HelpCliSyntaxDocumentation())
        return renderer.apply(self.rendering_environment)
