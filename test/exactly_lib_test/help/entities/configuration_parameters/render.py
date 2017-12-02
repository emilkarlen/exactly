import unittest

from exactly_lib.help.entities.configuration_parameters import all_configuration_parameters
from exactly_lib.help.entities.configuration_parameters import render as sut
from exactly_lib.help.entities.configuration_parameters.contents_structure import ConfigurationParameterDocumentation
from exactly_lib.help.entities.configuration_parameters.entity_configuration import CONF_PARAM_ENTITY_CONFIGURATION
from exactly_lib.help_texts.entity import conf_params
from exactly_lib.help_texts.entity.conf_params import ConfigurationParameterInfo
from exactly_lib.util.description import Description, DescriptionWithSubSections, from_simple_description
from exactly_lib.util.textformat.construction.section_contents_constructor import ConstructionEnvironment
from exactly_lib.util.textformat.structure.structures import text, para
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.util.textformat.test_resources import structure as struct_check


def suite() -> unittest.TestSuite:
    return unittest.TestSuite([
        unittest.makeSuite(TestIndividualConfigurationParameter),
        unittest.makeSuite(TestList),
    ])


class TestList(unittest.TestCase):
    def runTest(self):
        # ARRANGE #
        constructor = CONF_PARAM_ENTITY_CONFIGURATION.cli_list_constructor_getter.get_render(
            all_configuration_parameters.all_configuration_parameters())
        # ACT #
        actual = constructor.apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_section_contents.apply(self, actual)


class TestIndividualConfigurationParameter(unittest.TestCase):
    def test_conf_param_with_only_single_line_description(self):
        # ARRANGE #
        doc = ConfigurationParameterTestImpl('conf_param_name',
                                             Description(text('single line name'),
                                                         []),
                                             'default value')
        constructor = sut.IndividualConfParamConstructor(doc)
        # ACT #
        actual = constructor.apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_article_contents.apply(self, actual)

    def test_conf_param_with_complex_description(self):
        # ARRANGE #
        concept = ConfigurationParameterTestImpl('conf_param_name',
                                                 Description(text('single line name'),
                                                             [para('rest paragraph')]),
                                                 'default value')
        constructor = sut.IndividualConfParamConstructor(concept)
        # ACT #
        actual = constructor.apply(CONSTRUCTION_ENVIRONMENT)
        # ASSERT #
        struct_check.is_article_contents.apply(self, actual)


class ConfigurationParameterTestImpl(ConfigurationParameterDocumentation):
    def __init__(self,
                 conf_param_name: str,
                 description: Description,
                 default_value: str):
        super().__init__(ConfigurationParameterInfo(conf_param_name,
                                                    conf_param_name,
                                                    'ConfigurationParameterTestImpl single_line_description',
                                                    default_value,
                                                    conf_params.cross_ref(conf_param_name)))
        self.description = description
        self.default_value = default_value

    def default_value_str(self) -> str:
        return self.default_value

    def purpose(self) -> DescriptionWithSubSections:
        return from_simple_description(self.description)


CONSTRUCTION_ENVIRONMENT = ConstructionEnvironment(CrossReferenceTextConstructorTestImpl())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
