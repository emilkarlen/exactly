from shellcheck_lib.cli.program_modes.help.program_modes.main_program.contents import help_invokation_variants
from shellcheck_lib.help.program_modes.main_program.contents import test_case_overview_help
from shellcheck_lib.help.utils.render import SectionContentsRenderer, RenderingEnvironment
from shellcheck_lib.util.textformat.structure import document as doc


class OverviewRenderer(SectionContentsRenderer):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        return doc.SectionContents(test_case_overview_help(), [])


class InvokationVariantsRenderer(SectionContentsRenderer):
    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        pi = help_invokation_variants()
        return doc.SectionContents([pi], [])
