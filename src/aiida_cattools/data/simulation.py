from dataclasses import dataclass
from pathlib import Path
from pprint import pprint
from typing import Optional, Union  # Protocol
import uuid

from aiida_quantumespresso.workflows.pw.relax import PwRelaxWorkChain
from aiida_vasp.workchains.relax import RelaxWorkChain

from aiida.common.exceptions import NotExistentAttributeError
from aiida.orm import load_node
from aiida.orm.utils import OrmEntityLoader

from aiida_cattools.getters.wc import get_energy_from_pk

# ? Should this inherit from any AiiDA data type at all?
# ? Should this contain the catalyst/chemistry specifications
# ? or should those be in the catalyst system class?

# From Pol's InitialDatabase class
[
    # "name",
    # "material_id",
    # "structure",
    # "phase",
    # "formula",
    # "symmetry",
    # "base",
    # "perturb",
    # "unique_id",
    # "supercell",
    # "surface",
    # "bulk",
    # "cluster",
    # "temperature",
    # "magnetic_properties",
    # "calc_energy",
    # "calc_energy_per_atom",
    # "calc_energy_toten",
    # "calc_performed",
    # "calc_type",
    # "calc_output",
]


@dataclass
# class BaseSimulation
class Simulation:
    """Dataclass that compiles all the data associated with a simulation."""

    # ? General data
    global_uuid: Optional[str] = str(uuid.uuid4())
    label: Optional[str] = ""
    wc_pk: Optional[int] = 0
    comment: Optional[str] = ""
    local_path: Optional[Path] = Path()

    # ? Catalyst/chemical specifications
    chem_formula: Optional[str] = ""
    surf_facet: Optional[str] = ""
    active_metal: Optional[str] = ""  # Possibly instance of mendeleev
    site_subst: Optional[bool] = ""
    surf_vac: Optional[int] = 0
    subsurf_vac: Optional[int] = 0
    ads_site: Optional[str] = ""
    ads_formula: Optional[str] = ""

    # ? Simulation specifications
    functional: Optional[str] = "pbe"
    wc_type: Optional[Union[RelaxWorkChain, PwRelaxWorkChain]] = RelaxWorkChain
    wc_status: Optional[str] = ""  # ! # Possibly instance of CalcJobState
    # input_wc_sd_pk: Optional[int] # ? Add here, outside, or with getter method?

    # ? Simulation output
    final_energy: Optional[float] = 0
    site_mos: Optional[int] = 0  # ? I don't like the default value

    def set_output_energy(self):
        self.final_energy = get_energy_from_pk(input_pk=self.wc_pk)

    def get_output_energy(self):
        return self.final_energy
