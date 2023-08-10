import re
from typing import Union

from ase.atoms import Atoms
from ase.constraints import FixAtoms

from aiida.orm import CalcJobNode, Node, WorkChainNode


def set_selective_dynamics(ase_in: Atoms) -> dict:
    """Converts selective dynamics from ase.Atoms to dict that can be used in aiida.

    Args:
        ase_in (ase.Atoms): Structure in ase.Atoms format.

    Returns:
        dict: 'positions_dof' key with list of lists of bools.
    """
    try:
        constrained_indices = ase_in.constraints[0].get_indices()
        dynamics_list = []
        for iatom in range(len(ase_in)):
            if iatom in constrained_indices:
                dynamics_list.append([False, False, False])
            else:
                dynamics_list.append([True, True, True])
    except IndexError:
        dynamics_list = [[True, True, True]] * len(ase_in)

    dynamics_dict = {"positions_dof": dynamics_list}
    return dynamics_dict


def set_selective_dynamics_wc(
    ase_in: Atoms,
    wc_node: Union[CalcJobNode, WorkChainNode, Node],
) -> Atoms:
    """CHANGED: Now, adds the dynamics of an aiida-vasp calculation to an already exsting ase.Atoms object.

    Args:
        wc_node (CalcJobNode):

    Returns:
        Atoms: ase Atoms instance with selective dynamics attached.
    """

    constraints = wc_node.inputs.parameters.get_dict()["dynamics"]["positions_dof"]
    constraints_flattened = [all(constraint) for constraint in constraints]
    constraints_indices = [
        index for index, value in enumerate(constraints_flattened) if value is not True
    ]
    fixatoms = FixAtoms(indices=constraints_indices)
    ase_out = ase_in.copy()
    ase_out.set_constraint(fixatoms)

    return ase_out


def set_hubbard_values(
    ase_in: Atoms,
    hubbard_overrides: dict = None,
) -> dict:
    """Set up Hubbard (LDAUL, LDAUU, LDAUJ) values for atoms based on a mapping dictionary.

    Args:
        aiida_structure (StructureData): Structure for which the U should be set.
        u_mapping (dict, optional): Custom mapping. Defaults to None.

    Returns:
        dict: Output mapping that can be passed to AiiDA.
    """

    default_mapping = {
        "Ce": (3, 5.5, 1.0),
        "Ce_3": (3, 5.5, 1.0),
        "La": (3, 5.5, 1.0),
    }

    if hubbard_overrides is None:
        u_mapping = default_mapping
    else:
        u_mapping = {**default_mapping, **hubbard_overrides}

    u_list = []
    # Overly complicated to not get duplicated strings for multiple atoms of the same kind, preserved ordering, atoms appearing at different positions, etc.
    chemical_formula = ase_in.get_chemical_formula(mode="reduce")
    # print(chemical_formula)
    symbols_string = re.sub("[0-9]", "", chemical_formula)
    # print(symbols_string)
    symbols_list = re.findall("[A-Z][^A-Z]*", symbols_string)
    # print(symbols_list)

    for symbol in symbols_list:
        u_list.append(u_mapping.get(symbol, (-1, 0.0, 0.0)))
    # print(u_list)

    output_dict = {
        "ldaul": [_[0] for _ in u_list],
        "ldauu": [_[1] for _ in u_list],
        "ldauj": [_[2] for _ in u_list],
    }

    return output_dict
