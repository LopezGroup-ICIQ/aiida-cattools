from aiida.orm import load_entity, load_node


def get_energy_from_pk(input_pk):
    final_energy = 0
    wc_node = load_node(input_pk)
    try:
        final_energy = wc_node.outputs.misc.get_dict()["total_energies"][
            "energy_extrapolated_electronic"
        ]
    except:  # NotExistentAttributeError:
        raise
        pass

    return final_energy
