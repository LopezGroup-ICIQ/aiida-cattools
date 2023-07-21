import logging
from typing import List, Union

from aiida_tools.vasp.runners import set_selective_dynamics_wc
from ase import Atoms
import pandas as pd

from aiida.common.exceptions import NotExistent, NotExistentAttributeError
from aiida.orm import QueryBuilder, load_node

from aiida_cattools.getters.misc import get_energy_405_exit

__all__ = [
    "get_wc_pk_from_energy",
    "get_wc_input_structure",
    "get_wc_output_structure",
    "get_wc_structural_change",
    "get_wc_magnetization",
]


def get_wc_pk_from_energy(aiida_type, target_energy, tol: float = 0.5):
    """
    Function to retrieve a workchain/calculation pk by the final energy.
    """
    query = QueryBuilder()
    query.append(
        aiida_type,
        filters={
            "attributes.exit_status": 0,
        },
    )
    pks = []
    for node in query.iterall():
        flat_node = node[0]
        try:
            energy = flat_node.outputs["misc"]["total_energies"]["energy_extrapolated"]
            if abs(energy - target_energy) < tol:
                pks.append(flat_node.pk)
                # print(flat_node.pk)
                # return flat_node.pk
        except:
            raise

    return pks


def get_energy_from_wc_pk(input_pk):
    final_energy = 0
    try:
        wc_node = load_node(input_pk)
    except NotExistent:
        logging.warn(
            f"Workchain {input_pk} NotExistent. Returning default value of 0."  # noqa: E501
        )
        return final_energy

    if wc_node.exit_status == 405:
        final_energy = get_energy_405_exit(input_pk=input_pk)
    else:
        try:
            # ? Not sure if this is the standard for VASP or QE?
            final_energy = wc_node.outputs.misc.get_dict()["total_energies"][
                "energy_extrapolated_electronic"
            ]
        except NotExistentAttributeError:
            logging.warn(
                f"Workchain with PK {input_pk} gave NotExistentAttributeError. Returning default value of 0."  # noqa: E501
            )

    return final_energy


def get_wc_input_structure(
    input_pk: int, return_type: str = "ase"
) -> Union[List[Atoms], List[int]]:
    if input_pk == 0:
        if return_type == "ase":
            return [Atoms()]
        elif return_type == "pk":
            return [0]

    wc_node = load_node(input_pk)
    process_label = wc_node.process_label
    aiida_sd = wc_node.inputs.structure
    if return_type == "pk":
        return [aiida_sd.pk]
    elif return_type == "ase":
        structure_ase = aiida_sd.get_ase()

        if process_label == "RelaxWorkChain":  # VASP
            # Attach selective dynamics for VASP
            structure_ase = set_selective_dynamics_wc(
                wc_node=wc_node, ase_structure=structure_ase
            )
            # print(structure_ase)
        else:
            # ? Implement handling of QE here?
            pass

        return [structure_ase]
    else:
        return [Atoms()]


def get_wc_output_structure(
    input_pk: int, return_type: str = "ase"
) -> Union[List[Atoms], List[int]]:
    if input_pk == 0:
        if return_type == "ase":
            return [Atoms()]
        elif return_type == "pk":
            return [0]

    wc_node = load_node(input_pk)

    if wc_node.exit_status != 0:
        # todo: Implement here that the last output of each called workchain is
        # used
        # ! Now this preaks with the pk
        # raise Exception(f"Node with id {input_pk} has non-zero exit status")
        print(f"Node with id {input_pk} has non-zero exit status")
        if return_type == "ase":
            return [Atoms()]
        elif return_type == "pk":
            return [0]

    process_label = wc_node.process_label
    if process_label == "RelaxWorkChain":  # VASP
        structure_sd = wc_node.outputs.relax.structure
    elif process_label == "PwRelaxWorkChain":  # QE
        structure_sd = wc_node.outputs.output_structure
    elif process_label == "VaspWorkChain":  # QE
        logging.warn(
            f"VaspWorkChain ({input_pk}) does not return a StructureData node. Returning input structure instead."
        )  # noqa: E501
        structure_sd = wc_node.inputs.structure

    else:
        raise NotImplementedError(
            f"This type of workchain {process_label} is not yet implemented for node {input_pk}"  # noqa: E501
        )

    if return_type == "pk":
        return [structure_sd.pk]
    elif return_type == "ase":
        structure_ase = structure_sd.get_ase()
        if process_label == "RelaxWorkChain":  # VASP
            structure_ase = set_selective_dynamics_wc(
                wc_node=wc_node, ase_structure=structure_ase
            )
        return [structure_ase]
    else:
        raise ValueError(f"return_type {return_type} is not implemented")


def get_wc_structural_change(input_pk: int, return_type: str = "ase") -> List[Atoms]:
    initial_structure = get_wc_input_structure(input_pk, return_type=return_type)

    try:
        final_structure = get_wc_output_structure(input_pk, return_type=return_type)
    except (Exception, NotImplementedError) as exception:
        final_structure = [Atoms()]

    structure_list = [initial_structure, final_structure]

    return structure_list


def get_wc_magnetization(
    input_pk: int,
    mos_thresh: float = 0.7,
    mos_dict: dict = {"Ce": "f"},
    other_element: str = None,
) -> dict:
    """Retrieve num_ce3 based on an element for which it is counted, e.g. Ce and magnetic moment of another element, e.g. Mn.

    Args:
        aiida_calc (Union[int, ProcessNode]): ProcessNode or pk of a calculation.
        mos_thresh (float, optional): Threshold for magnetization. Defaults to 0.8.
        mos_dict (dict, optional): Atom type and orbital for num_ce3 determination. Defaults to {"Ce": "f"}.
        other_element (str, optional): Other element for which magnetic moment should be extracted. Defaults to None.

    Returns:
        dict: Dictionary with num_ce3 and magnetic moment of other element.
    """
    # ? Needs site_magnetization output node
    # ? Just sum up over f-orbital magnetizations for the Ce atoms
    output_dict = {"mag_df": None, "num_ce3": None, "ce3_mag": None, "elem_mag": None}
    # if isinstance(input_pk, int):

    if input_pk == 0:
        return output_dict
    else:
        wc_node = load_node(input_pk)
    # elif isinstance(input_pk, ProcessNode):
    #     aiida_node = input_pk
    # else:
    #     raise NotImplementedError

    try:
        node_symbols = wc_node.inputs.structure.get_site_kindnames()
    except:
        raise
    try:
        magnetization_dict = wc_node.outputs.site_magnetization.get_dict()

        mag_df = (
            pd.DataFrame.from_dict(
                magnetization_dict["site_magnetization"]["sphere"]["x"]["site_moment"]
            )
            .transpose()
            .abs()
        )
        mag_df["symbol"] = node_symbols
        output_dict["mag_df"] = mag_df

        num_ce3 = mag_df.loc[
            (mag_df["symbol"] == list(mos_dict.keys())[0])
            & (mag_df[list(mos_dict.values())[0]].abs() > mos_thresh)
        ].shape[0]
        output_dict["num_ce3"] = num_ce3

        ce3_mag = mag_df.loc[(mag_df["symbol"] == list(mos_dict.keys())[0])][
            "tot"
        ].sum()
        output_dict["ce3_mag"] = ce3_mag

        # magnetization_df.head(10)
        if other_element is not None:
            elem_df = mag_df.loc[mag_df["symbol"] == other_element]
            elem_mag = elem_df["tot"].values[0]
            output_dict["elem_mag"] = elem_mag

    except NotExistentAttributeError:
        pass

    return output_dict