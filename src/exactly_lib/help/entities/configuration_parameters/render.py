from exactly_lib.help.entities.configuration_parameters.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help.render import see_also as render_utils
from exactly_lib.util.description import DescriptionWithSubSections
from exactly_lib.util.textformat.constructor.environment import ConstructionEnvironment
from exactly_lib.util.textformat.constructor.section import \
    ArticleContentsConstructor
from exactly_lib.util.textformat.structure import document as doc
from exactly_lib.util.textformat.structure import structures as docs


class IndividualConfParamConstructor(ArticleContentsConstructor):
    def __init__(self, conf_param: ConfigurationParameterDocumentation):
        self.conf_param = conf_param

    def apply(self, environment: ConstructionEnvironment) -> doc.ArticleContents:
        purpose = self.conf_param.purpose()
        sub_sections = [
            docs.section('Default Value',
                         [self.conf_param.default_value_para()])
        ]
        sub_sections += self._rest_section(purpose)
        sub_sections += self._see_also_sections(environment)

        return doc.ArticleContents(docs.paras(purpose.single_line_description),
                                   docs.SectionContents([],
                                                        sub_sections))

    @staticmethod
    def _rest_section(purpose: DescriptionWithSubSections):
        rest = purpose.rest
        if rest.is_empty:
            return []
        sect = docs.section('Description',
                            rest.initial_paragraphs,
                            rest.sections)
        return [sect]

    def _see_also_sections(self, environment: ConstructionEnvironment) -> list:
        return render_utils.see_also_sections(self.conf_param.see_also_targets(),
                                              environment)
