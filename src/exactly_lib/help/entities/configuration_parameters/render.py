from exactly_lib.help.entities.configuration_parameters.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help.utils.rendering import see_also_section as render_utils
from exactly_lib.help.utils.rendering.section_contents_renderer import RenderingEnvironment, SectionContentsRenderer
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure.structures import para, section


class IndividualConfParamRenderer(SectionContentsRenderer):
    def __init__(self, conf_param: ConfigurationParameterDocumentation):
        self.conf_param = conf_param

    def apply(self, environment: RenderingEnvironment) -> doc.SectionContents:
        purpose = self.conf_param.purpose()
        initial_paragraphs = [para(purpose.single_line_description)]
        sub_sections = [
            section('Default Value',
                    [self.conf_param.default_value_para()])
        ]
        sub_sections += self._rest_section(purpose)
        sub_sections += self._see_also_sections(environment)

        return doc.SectionContents(initial_paragraphs,
                                   sub_sections)

    @staticmethod
    def _rest_section(purpose: DescriptionWithSubSections):
        rest = purpose.rest
        if rest.is_empty:
            return []
        sect = section('Description',
                       rest.initial_paragraphs,
                       rest.sections)
        return [sect]

    def _see_also_sections(self, environment: RenderingEnvironment) -> list:
        return render_utils.see_also_sections(self.conf_param.see_also_targets(),
                                              environment)
