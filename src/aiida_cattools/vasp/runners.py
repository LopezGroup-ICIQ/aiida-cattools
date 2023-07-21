from aiida.common.extendeddicts import AttributeDict
from aiida.engine import submit
from aiida.orm import Group, StructureData, load_code, load_group
from aiida.plugins import DataFactory, WorkflowFactory

from aiida_cattools.vasp.default_dicts import (
    DEFAULT_POTENTIAL_MAPPING,
    EXTRA_POTENTIAL_MAPPING,
)
from aiida_cattools.vasp.setters import set_hubbard_values, set_selective_dynamics


def run_vasp_relax(
    ase_in,
    input_incar_dict,
    group_label: str = None,
    calc_label: str = None,
):
    # code_string, incar, kmesh, structure, potential_family, potential_mapping, options
    """Main method to setup the calculation."""

    # CODE_PK = "14366"
    # vasp-6.3.0-std@MN4    14351  core.code.installed
    # vasp-6.3.0-gam@MN4    14366  core.code.installed
    POTENTIAL_FAMILY = "vasp-5.4-pbe"
    KMESH = [1, 1, 1]
    POTENTIAL_MAPPING = {**DEFAULT_POTENTIAL_MAPPING, **EXTRA_POTENTIAL_MAPPING}

    OPTIONS = AttributeDict()
    OPTIONS.qos = "class_a"
    OPTIONS.resources = {"num_machines": 1, "num_mpiprocs_per_machine": 48}
    OPTIONS.max_wallclock_seconds = 259200

    # Incar reproduced from INCAR file of pristine CeO2(100) slab
    incar_dict = dict(input_incar_dict, **set_hubbard_values(ase_in=ase_in))
    dynamics_dict = set_selective_dynamics(ase_in)
    parameter_dict = {
        "incar": incar_dict,
        "dynamics": dynamics_dict,
    }

    # We set the workchain you would like to call
    workchain = WorkflowFactory("vasp.relax")

    # And finally, we declare the options, settings and input containers
    settings = AttributeDict()
    inputs = AttributeDict()

    # Organize settings
    settings.parser_settings = {
        "output_params": [
            "total_energies",
            "maximum_force",
            "maximum_stress",
            "notifications",
            "run_status",
            "run_stats",
            "version",
        ],
        # ! Probably duplicated
        "add_trajectory": True,
        "add_structure": True,
        "add_site_magnetization": True,
    }

    # Set inputs for the following WorkChain execution
    # Set code
    # inputs.code = Code.get_from_string(CODE_PK)
    inputs.code = load_code("vasp-6.3.0-gam@MN4")

    # Set structure
    inputs.structure = StructureData(ase=ase_in)

    # ? Don't run final SCF, as should be converged already, and don't know how to restart
    # ? from CHGCAR, so often does not converge which is annoying
    inputs.perform_static = DataFactory("core.bool")(False)
    # Set k-points grid density
    kpoints = DataFactory("core.array.kpoints")()
    kpoints.set_kpoints_mesh(KMESH)
    inputs.kpoints = kpoints
    # Set parameters
    inputs.parameters = DataFactory("core.dict")(dict=parameter_dict)
    # Set potentials and their mapping
    inputs.potential_family = DataFactory("core.str")(POTENTIAL_FAMILY)
    inputs.potential_mapping = DataFactory("core.dict")(dict=POTENTIAL_MAPPING)
    # Set options
    inputs.options = DataFactory("core.dict")(dict=OPTIONS)
    # Set settings
    inputs.settings = DataFactory("core.dict")(dict=settings)
    # Set workchain related inputs, in this case, give more explicit output to report
    inputs.verbose = DataFactory("core.bool")(True)
    # Increase number of max_iterations
    inputs.max_iterations = DataFactory("core.int")(10)

    # Relaxation related parameters that is passed to the relax workchain
    relax = AttributeDict()
    # Turn on relaxation
    relax.perform = DataFactory("core.bool")(True)
    # Select relaxation algorithm
    relax.algo = DataFactory("core.str")("cg")
    # Set force cutoff limit (EDIFFG, but no sign needed)
    relax.force_cutoff = DataFactory("core.float")(0.015)
    # Turn on relaxation of positions (strictly not needed as the default is on)
    # The three next parameters correspond to the well known ISIF=3 setting
    relax.positions = DataFactory("core.bool")(True)
    # Set maximum number of ionic steps
    relax.steps = DataFactory("core.int")(1000)
    # Turn on convergence check
    # relax.convergence_on = DataFactory("core.bool")(True)
    # # Also increase number of max_iterations in convergence (not sure if this is actually used???)
    # relax.convergence_max_iterations = DataFactory("core.int")(10)
    inputs.relax = relax

    # Submit the requested workchain with the supplied inputs
    submit_node = submit(workchain, **inputs)
    if calc_label is not None:
        submit_node.label = calc_label

    if group_label is not None:
        try:
            submission_group = Group(group_label)
            submission_group.store()
        except:  # IntegrityError:
            submission_group = load_group(group_label)
        submission_group.add_nodes(submit_node)

    return submit_node


def run_vasp_hse03(
    ase_in, input_incar_dict, group_label: str = None, calc_label: str = None
):
    # code_string, incar, kmesh, structure, potential_family, potential_mapping, options
    """Main method to setup the calculation."""

    # CODE_PK = "14366"
    # vasp-6.3.0-std@MN4    14351  core.code.installed
    # vasp-6.3.0-gam@MN4    14366  core.code.installed
    POTENTIAL_FAMILY = "vasp-5.4-pbe"
    KMESH = [1, 1, 1]

    OPTIONS = AttributeDict()
    OPTIONS.qos = "class_a"
    OPTIONS.resources = {"num_machines": 1, "num_mpiprocs_per_machine": 48}
    OPTIONS.max_wallclock_seconds = 259200

    # Incar reproduced from INCAR file of pristine CeO2(100) slab
    incar_dict = dict(input_incar_dict)  # ! Remove U
    dynamics_dict = constraints_to_aiida(ase_in)
    parameter_dict = {
        "incar": incar_dict,
        "dynamics": dynamics_dict,
    }

    # We set the workchain you would like to call
    workchain = WorkflowFactory("vasp.vasp")

    # And finally, we declare the options, settings and input containers
    settings = AttributeDict()
    inputs = AttributeDict()

    # Organize settings
    settings.parser_settings = {
        "output_params": [
            "total_energies",
            "maximum_force",
            # "maximum_stress",
            "notifications",
            "run_status",
            "run_stats",
            "version",
        ],
        "add_site_magnetization": True,
    }

    # Set inputs for the following WorkChain execution
    # Set code
    # inputs.code = Code.get_from_string(CODE_PK)
    inputs.code = load_code("vasp-6.3.0-gam@MN4")

    # Set structure
    inputs.structure = StructureData(ase=ase_in)

    POTENTIAL_MAPPING = {**DEFAULT_POTENTIAL_MAPPING, **EXTRA_POTENTIAL_MAPPING}
    # ? Don't run final SCF, as should be converged already, and don't know how to restart
    # ? from CHGCAR, so often does not converge which is annoying
    # inputs.perform_static = DataFactory("core.bool")(True)
    # Set k-points grid density
    kpoints = DataFactory("core.array.kpoints")()
    kpoints.set_kpoints_mesh(KMESH)
    inputs.kpoints = kpoints
    # Set parameters
    inputs.parameters = DataFactory("core.dict")(dict=parameter_dict)
    # Set potentials and their mapping
    inputs.potential_family = DataFactory("core.str")(POTENTIAL_FAMILY)
    inputs.potential_mapping = DataFactory("core.dict")(dict=POTENTIAL_MAPPING)
    # Set options
    inputs.options = DataFactory("core.dict")(dict=OPTIONS)
    # Set settings
    inputs.settings = DataFactory("core.dict")(dict=settings)
    # Set workchain related inputs, in this case, give more explicit output to report
    inputs.verbose = DataFactory("core.bool")(True)
    # Increase number of max_iterations
    # inputs.max_iterations = DataFactory("core.int")(5)

    # Submit the requested workchain with the supplied inputs
    submit_node = submit(workchain, **inputs)
    if calc_label is not None:
        submit_node.label = calc_label

    if group_label is not None:
        try:
            submission_group = Group(group_label)
            submission_group.store()
        except:  # IntegrityError:
            submission_group = load_group(group_label)
        submission_group.add_nodes(submit_node)

    return submit_node
