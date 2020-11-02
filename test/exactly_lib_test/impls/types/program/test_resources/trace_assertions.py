from exactly_lib.type_val_prims.program import commands
from exactly_lib.util.description_tree.tree import Detail
from exactly_lib_test.test_resources.value_assertions import value_assertion as asrt
from exactly_lib_test.test_resources.value_assertions.value_assertion import ValueAssertion
from exactly_lib_test.util.description_tree.test_resources import described_tree_assertions as asrt_d_tree


def matches_pgm_as_detail__py_interpreter() -> ValueAssertion[Detail]:
    return matches_pgm_as_detail__executable_file()


def matches_pgm_as_detail__executable_file() -> ValueAssertion[Detail]:
    return asrt_d_tree.is_tree_detail(
        asrt_d_tree.matches_node(
            header=asrt.equals(commands.CommandDriverForExecutableFile.NAME)
        )
    )
