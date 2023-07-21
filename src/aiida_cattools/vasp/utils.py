from aiida.orm import load_node

from aiida_cattools.getters.wc import get_wc_output_structure
from aiida_cattools.vasp.default_dicts import DEFAULT_INCAR_DICT
from aiida_cattools.vasp.runners import run_vasp_relax


def resubmit_failed_relax(pks_in: list, group_label: str):
    # ? This works for a list of pks, not just a single one
    pks_out = []
    for pk_in in pks_in:
        wc_node = load_node(pk_in)
        exit_status = wc_node.exit_status

        if exit_status == 0:
            pks_out.append(pk_in)
        else:
            # ! This might break -> Better handling
            resubmit_ase = get_wc_output_structure(pk_in)[0]
            # ! Use builder restart instead, and allow changing incar dict...
            resubmit_node = run_vasp_relax(
                ase_in=resubmit_ase,
                # ? Option to change the dict
                input_incar_dict=DEFAULT_INCAR_DICT,
                group_label=group_label,
            )
            pks_out.append(resubmit_node.pk)

    return pks_out
