from typing import Callable

from exactly_lib.definitions.entity import syntax_elements
from exactly_lib.symbol.logic.program.program_sdv import ProgramSdv
from exactly_lib.symbol.logic.string_transformer import StringTransformerSdv
from exactly_lib.test_case_file_structure.tcds import Tcds
from exactly_lib.test_case_utils.description_tree import custom_details
from exactly_lib.test_case_utils.string_transformer import names
from exactly_lib.test_case_utils.string_transformer.impl.run_program import primitive
from exactly_lib.test_case_utils.string_transformer.impl.utils import from_parts
from exactly_lib.type_system.description.tree_structured import StructureRenderer
from exactly_lib.type_system.logic.application_environment import ApplicationEnvironment
from exactly_lib.type_system.logic.logic_base_class import ApplicationEnvironmentDependentValue
from exactly_lib.type_system.logic.program.program import ProgramDdv, ProgramAdv
from exactly_lib.type_system.logic.string_transformer import StringTransformer, StringTransformerAdv
from exactly_lib.type_system.logic.string_transformer import StringTransformerDdv
from exactly_lib.util.description_tree import renderers
from exactly_lib.util.description_tree.renderer import NodeRenderer
from exactly_lib.util.description_tree.tree import Node
from exactly_lib.util.symbol_table import SymbolTable


def sdv(ignore_exit_code: bool, program: ProgramSdv) -> StringTransformerSdv:
    def get_mk_adv(program_ddv: ProgramDdv) -> Callable[[Tcds], StringTransformerAdv]:
        def mk_adv(tcds: Tcds) -> StringTransformerAdv:
            return _RunProgramAdv(ignore_exit_code,
                                  program_ddv.value_of_any_dependency(tcds))

        return mk_adv

    def mk_ddv(symbols: SymbolTable) -> StringTransformerDdv:
        program_ddv = program.resolve(symbols)
        return from_parts.Ddv(
            _RunProgramStructureRenderer(ignore_exit_code,
                                         program_ddv.structure()),
            program_ddv.validator,
            get_mk_adv(program_ddv),
        )

    return from_parts.Sdv(
        program.references,
        mk_ddv,
    )


class _RunProgramAdv(ApplicationEnvironmentDependentValue[StringTransformer]):
    def __init__(self,
                 ignore_exit_code: bool,
                 program: ProgramAdv,
                 ):
        self._ignore_exit_code = ignore_exit_code
        self._program = program

    def primitive(self, environment: ApplicationEnvironment) -> StringTransformer:
        program = self._program.primitive(environment)
        return primitive.transformer(
            _RunProgramStructureRenderer.NAME,
            environment,
            self._ignore_exit_code,
            program,
            _RunProgramStructureRenderer(self._ignore_exit_code,
                                         program.structure())
        )


class _RunProgramStructureRenderer(NodeRenderer[None]):
    NAME = ' '.join((
        names.RUN_PROGRAM_TRANSFORMER_NAME,
        syntax_elements.PROGRAM_SYNTAX_ELEMENT.singular_name,
    ))

    def __init__(self,
                 ignore_exit_code: bool,
                 program: StructureRenderer,
                 ):
        self._program = program
        self._ignore_exit_code = ignore_exit_code

    def render(self) -> Node[None]:
        return self._renderer().render()

    def _renderer(self) -> StructureRenderer:
        return renderers.NodeRendererFromParts(
            self.NAME,
            None,
            (
                custom_details.optional_option(names.RUN_WITH_IGNORED_EXIT_CODE_OPTION_NAME,
                                               self._ignore_exit_code),
                custom_details.TreeStructure(self._program),
            ),
            (),
        )
