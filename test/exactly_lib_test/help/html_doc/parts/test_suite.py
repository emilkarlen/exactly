import unittest

from exactly_lib.help.contents_structure import test_suite_help
from exactly_lib.help.html_doc.parts import test_suite as sut
from exactly_lib.help.utils.section_contents_renderer import RenderingEnvironment
from exactly_lib_test.help.test_resources import CrossReferenceTextConstructorTestImpl
from exactly_lib_test.help.test_resources.section_generator import generator_generates_valid_data


def suite() -> unittest.TestSuite:
    return unittest.makeSuite(Test)


class Test(unittest.TestCase):
    def runTest(self):
        setup = test_suite_help()
        generator = sut.generator('header', setup, RENDERING_ENVIRONMENT)
        generator_generates_valid_data(self, generator)


RENDERING_ENVIRONMENT = RenderingEnvironment(CrossReferenceTextConstructorTestImpl())

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
