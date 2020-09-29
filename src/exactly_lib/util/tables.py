from typing import TypeVar, List

T = TypeVar('T')


def extend_each_sub_list_to_max_sub_list_length(list_of_lists: List[List[T]],
                                                fill_value: T) -> List[List[T]]:
    max_num_elements = max([len(element_list) for element_list in list_of_lists])
    ret_val = []
    for elements in list_of_lists:
        normalised = elements + (max_num_elements - len(elements)) * [fill_value]
        ret_val.append(normalised)
    return ret_val


def transpose(rows: List[List[T]]) -> List[List[T]]:
    if not rows:
        return []
    ret_val = []
    for _ in rows[0]:
        output_col = []
        for _ in rows:
            output_col.append([])
        ret_val.append(output_col)
    for i, row in enumerate(rows):
        for j, cell in enumerate(row):
            ret_val[j][i] = cell
    return ret_val
