from typing import Union

import numpy as np
import pandas as pd

from aiida.orm import Group, load_group

from aiida_cattools.getters.wc import (
    get_wc_input_structure,
    get_wc_output_structure,
    get_wc_structural_change,
)


def get_group_structures(
    group_input: Union[list, Group],
    sort_pks: bool = True,
    which_ones: str = "output",
    return_type: str = "ase",
):
    # todo: Use the EntityLoader class to load from label, pk, uuid, etc.
    # todo: Option for this function to use a list of pks or nodes
    if isinstance(group_input, Group):
        group_pks = [node.pk for node in group_input.nodes]
        # Could remove the option and just make it always the default, to sort the
        # nodes by submission, that is, pk
        if sort_pks is True:
            group_pks = sorted(group_pks)
    elif isinstance(group_input, (list, np.ndarray, pd.Series)):
        # ! I don't want them to be sorted here to retain the order from the df
        group_pks = group_input
    elif isinstance(group_input, str):
        group = load_group(group_input)
        group_pks = [node.pk for node in group.nodes]
        # Could remove the option and just make it always the default, to sort the
        # nodes by submission, that is, pk
        if sort_pks is True:
            group_pks = sorted(group_pks)

    function_dict = {
        "input": get_wc_input_structure,
        "output": get_wc_output_structure,
        "change": get_wc_structural_change,
    }

    group_sds = []
    for input_pk in group_pks:
        structures = function_dict[which_ones](
            input_pk=input_pk, return_type=return_type
        )
        group_sds.extend(structures)

    if which_ones == "change":
        group_sds = [structure for sublist in group_sds for structure in sublist]

    return group_sds
