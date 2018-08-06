from exactly_lib.common.err_msg.definitions import Block, Blocks


def prefix_first_block(prefix: Block, blocks: Blocks) -> Blocks:
    if not prefix:
        return blocks
    if not blocks:
        return [prefix]
    return [prefix + blocks[0]] + blocks[1:]
