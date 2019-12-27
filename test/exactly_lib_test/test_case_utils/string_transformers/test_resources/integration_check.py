import unittest
from typing import Optional, Sequence, Callable

from exactly_lib.common.report_rendering.text_doc import TextRenderer
from exactly_lib.section_document.parse_source import ParseSource
from exactly_lib.section_document.parser_classes import Parser
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.symbol.symbol_usage import SymbolReference
from exactly_lib.test_case_utils.string_transformer import parse_string_transformer
from exactly_lib.type_system.logic.hard_error import HardErrorException
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironment, ApplicationEnvironmentDependentValue
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerDdv, \
    StringTransformerModel
from exactly_lib.util.file_utils import TmpDirFileSpaceAsDirCreatedOnDemand
from exactly_lib.util.symbol_table import SymbolTable, symbol_table_from_none_or_value
from exactly_lib_test.test_case_file_structure.test_resources.paths import fake_tcds
from exactly_lib_test.test_case_utils.parse.test_resources.arguments_building import Arguments
from exactly_lib_test.test_case_utils.parse.test_resources.single_line_source_instruction_utils import \
    equivalent_source_variants__with_source_check__for_expression_parser
from exactly_lib_test.test_case_utils.test_resources.validation import ValidationExpectation, all_validations_passes
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


class Arrangement:
    def __init__(self, symbols: Optional[SymbolTable] = None):
        self.symbols = symbol_table_from_none_or_value(symbols)


class Expectation:
    def __init__(
            self,
            source: ValueAssertion[ParseSource] = asrt.anything_goes(),
            symbol_references: ValueAssertion[Sequence[SymbolReference]] = asrt.is_empty_sequence,
            validation: ValidationExpectation = all_validations_passes(),
            main_result: ValueAssertion[StringTransformerModel] = asrt.anything_goes(),
            is_hard_error: Optional[ValueAssertion[TextRenderer]] = None,
            is_identity_transformer: ValueAssertion[bool] = asrt.equals(False)
    ):
        self.source = source
        self.symbol_references = symbol_references
        self.validation = validation
        self.main_result = main_result
        self.is_hard_error = is_hard_error
        self.is_identity_transformer = is_identity_transformer


is_pass = Expectation


def check(put: unittest.TestCase,
          source: ParseSource,
          model: StringTransformerModel,
          arrangement: Arrangement,
          expectation: Expectation):
    _Checker(put, source, model, parse_string_transformer.parser(), arrangement, expectation).check()


def check_with_custom_parser(put: unittest.TestCase,
                             source: ParseSource,
                             model: StringTransformerModel,
                             parser: Parser[StringTransformerSdv],
                             arrangement: Arrangement,
                             expectation: Expectation):
    _Checker(put, source, model, parser, arrangement, expectation).check()


class TestCaseWithCheckMethods(unittest.TestCase):
    def _check(self,
               source: ParseSource,
               model: StringTransformerModel,
               arrangement: Arrangement,
               expectation: Expectation
               ):
        check(self, source, model, arrangement, expectation)

    def _check_with_source_variants(self,
                                    arguments: Arguments,
                                    get_model: Callable[[], StringTransformerModel],
                                    arrangement: Arrangement,
                                    expectation: Expectation
                                    ):
        for source in equivalent_source_variants__with_source_check__for_expression_parser(self, arguments):
            self._check(source, get_model(), arrangement, expectation)


class _CheckIsDoneException(Exception):
    pass


class _Checker:
    def __init__(self,
                 put: unittest.TestCase,
                 source: ParseSource,
                 model: StringTransformerModel,
                 parser: Parser[StringTransformerSdv],
                 arrangement: Arrangement,
                 expectation: Expectation):
        self.put = put
        self.source = source
        self.model = model
        self.parser = parser
        self.arrangement = arrangement
        self.expectation = expectation
        self.tcds = fake_tcds()

    def check(self):
        try:
            self._check()
        except _CheckIsDoneException:
            pass

    def _check(self):
        transformer_sdv = self._parse()

        self.expectation.symbol_references.apply_with_message(self.put,
                                                              transformer_sdv.references,
                                                              'reference')

        transformer_ddv = self._resolve_ddv(transformer_sdv)

        self._check_validation_pre_sds(transformer_ddv)
        self._check_validation_post_sds(transformer_ddv)

        transformer = self._resolve_primitive_value(transformer_ddv)
        self._check_equivalent_structures(transformer_ddv, transformer)

        self._check_application(transformer)

    def _parse(self) -> StringTransformerSdv:
        sdv = self.parser.parse(self.source)
        asrt.is_instance(StringTransformerSdv).apply_with_message(self.put,
                                                                  sdv,
                                                                  'SDV')
        assert isinstance(sdv, StringTransformerSdv)

        self.expectation.source.apply_with_message(self.put,
                                                   self.source,
                                                   'source after parse')

        return sdv

    def _resolve_ddv(self, transformer_sdv: StringTransformerSdv) -> StringTransformerDdv:
        transformer_ddv = transformer_sdv.resolve(self.arrangement.symbols)

        asrt.is_instance(StringTransformerDdv).apply_with_message(self.put,
                                                                  transformer_ddv,
                                                                  'resolved value')

        assert isinstance(transformer_ddv, StringTransformerDdv)

        return transformer_ddv

    def _resolve_primitive_value(self, transformer_ddv: StringTransformerDdv) -> StringTransformer:
        adv = transformer_ddv.value_of_any_dependency(self.tcds)
        self.put.assertIsInstance(adv, ApplicationEnvironmentDependentValue)

        ae = ApplicationEnvironment(
            TmpDirFileSpaceAsDirCreatedOnDemand(self.tcds.sds.internal_tmp_dir / 'tmp-file-space')
        )
        ret_val = adv.applier(ae)

        asrt.is_instance(StringTransformer).apply_with_message(self.put,
                                                               ret_val,
                                                               'primitive value')

        self.expectation.is_identity_transformer.apply_with_message(
            self.put,
            ret_val.is_identity_transformer,
            'is identity transformer'
        )
        return ret_val

    def _check_validation_pre_sds(self, transformer_ddv: StringTransformerDdv):
        result = transformer_ddv.validator().validate_pre_sds_if_applicable(self.tcds.hds)

        self.expectation.validation.pre_sds.apply_with_message(self.put,
                                                               result,
                                                               'validation/pre sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_validation_post_sds(self, transformer_ddv: StringTransformerDdv):
        result = transformer_ddv.validator().validate_post_sds_if_applicable(self.tcds)

        self.expectation.validation.post_sds.apply_with_message(self.put,
                                                                result,
                                                                'validation/post sds')

        if result is not None:
            raise _CheckIsDoneException()

    def _check_application(self, transformer: StringTransformer):
        try:
            main_result = transformer.transform(self.model)
            self._check_application_result(main_result)
        except HardErrorException as ex:
            self._check_hard_error(ex)

    def _check_application_result(self, result: StringTransformerModel):
        if self.expectation.is_hard_error is not None:
            self.put.fail('HARD_ERROR not reported (raised)')

        self.expectation.main_result.apply_with_message(self.put,
                                                        result,
                                                        'result of main')

    def _check_hard_error(self, result: HardErrorException):
        if self.expectation.is_hard_error is None:
            self.put.fail('Unexpected HARD_ERROR')
        else:
            self.expectation.is_hard_error.apply_with_message(self.put, result.error,
                                                              'error message for hard error')
            raise _CheckIsDoneException()

    def _check_equivalent_structures(self,
                                     ddv: StringTransformerDdv,
                                     primitive: StringTransformer):
        structure_tree_of_ddv = ddv.structure().render()
        structure_tree_of_primitive = primitive.structure().render()
        structure_equals_ddv = asrt_d_tree.header_data_and_children_equal_as(structure_tree_of_ddv)
        structure_equals_ddv.apply_with_message(
            self.put,
            structure_tree_of_primitive,
            'structure of primitive should be same as that of ddv')
