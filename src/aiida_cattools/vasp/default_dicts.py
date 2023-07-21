
from ase.data import chemical_symbols


DEFAULT_INCAR_DICT = {
    # ==> Input <== #
    "ISTART": 0,
    "ICHARG": 2,
    # ==> OUTPUT <== #
    "LWAVE": "F",
    "LCHARG": "F",
    "LORBIT": 11,
    "LOPTICS": "F",
    # ==> ELECTRONIC STRUCTURE + RELAXATION <== #
    "ISPIN": 2,
    "GGA": "PE",
    "ALGO": "N",
    "ENCUT": 500,
    "EDIFF": 1e-5,
    "NELM": 1000,
    "LREAL": "AUTO",
    # ==> IONIC RELAXATION <== #
    # "IBRION": 2,
    # "NSW": 500,
    "POTIM": 0.1,
    # "EDIFFG": -0.015, # ? Set in workchain
    # ==> U-TERM <== #
    "LDAU": "T",
    "LASPH": "T",
    "LDAUPRINT": 0,
    # ==> PARALLELISATION <== #
    "KPAR": 1,
    "NCORE": 4,
    "LPLANE": "T",
    "LSCALU": "F",
    # ==> DIPOLE INTERACTION <== #
    "LDIPOL": "T",
    "IDIPOL": 3,
    # ==> DOS RELATED VALUES <== #
    "ISMEAR": 0,
    "SIGMA": 0.05,
    # ==> LINEAR MIXING <== #
    "LMAXMIX": 6,
    "INIMIX": 0,
    "AMIX": 0.2,
    "BMIX": 0.0001,
    "AMIX_MAG": 0.8,
    "BMIX_MAG": 0.0001,
}

MOLECULE_INCAR_DICT = {
    **DEFAULT_INCAR_DICT,
    **{
        "LDIPOL": "F",
    },
}

HSE03_INCAR_DICT = {
    # ==> Input <== #
    "ISTART": 0,
    "ICHARG": 2,
    # ==> OUTPUT <== #
    "LWAVE": "F",
    "LCHARG": "F",
    "LORBIT": 11,
    "LOPTICS": "F",
    # ==> ELECTRONIC STRUCTURE + RELAXATION <== #
    "ISPIN": 2,
    "GGA": "PE",
    "ALGO": "All",
    "ENCUT": 500,
    "EDIFF": 1e-4,
    "NELM": 1000,
    "LREAL": "AUTO",
    # ==> IONIC RELAXATION <== #
    "NSW": 0,  # This sets IBRION to -1
    # "ISIF": 2,
    "POTIM": 0.1,
    # ==> IONIC RELAXATION <== #
    "LHFCALC": "T",
    "HFSCREEN": 0.3,
    "AEXX": 0.13,
    "AGGAX": 0.87,
    # ==> PARALLELISATION <== #
    "KPAR": 1,
    "NCORE": 4,
    "LPLANE": "T",
    "LSCALU": "F",
    # ==> DIPOLE INTERACTION <== #
    "LDIPOL": "T",
    "IDIPOL": 3,
    # ==> DOS RELATED VALUES <== #
    "ISMEAR": 0,
    "SIGMA": 0.05,
    # ==> LINEAR MIXING <== #
    "LMAXMIX": 6,
    "INIMIX": 0,
    "AMIX": 0.2,
    "BMIX": 0.0001,
    "AMIX_MAG": 0.8,
    "BMIX_MAG": 0.0001,
}

DEFAULT_POTENTIAL_MAPPING = {symb: symb for symb in chemical_symbols[1:]}
EXTRA_POTENTIAL_MAPPING = {
    "Ce_3": "Ce_3",
    "La": "Ce_3",
}
