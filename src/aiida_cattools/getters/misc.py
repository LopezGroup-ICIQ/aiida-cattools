import logging

from aiida.orm import load_node

__all__ = ["get_energy_405_exit"]


def get_energy_405_exit(input_pk):
    wc_node = load_node(input_pk)
    last_vaspcalc = wc_node.called_descendants[-1]

    if last_vaspcalc.exit_status == 1002:
        # exit_message = "the parser is not able to parse the maximum_stress quantity"
        energy = last_vaspcalc.outputs.misc.get_dict()["total_energies"][
            "energy_extrapolated_electronic"
        ]
        return energy
    else:
        logging.warning(
            f"VaspWorkChain {input_pk} failed but not due to maximum stress error. Investigate further"
        )
        return 0
