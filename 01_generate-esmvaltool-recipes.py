#!/usr/bin/env python

import os
import pathlib
import yaml

CMIP5_ROOTDIR = os.path.join(os.getcwd(), "esmvaltool-recipes")
CMIP6_ROOTDIR = os.path.join(os.getcwd(), "esmvaltool-recipes")

CMIP5_MODELS = {
    "HadCM3": {"ensemble": "r(1:10)i3p1", "start_year": 1960, "end_year": 2009},
    "CanCM4": {"ensemble": "r(1:10)i1p1", "start_year": 1960, "end_year": 2010},  # 2011
    "GFDL-CM2p1": {
        "ensemble": "r(1:10)i1p1",
        "start_year": 1961,
        "end_year": 2010,  # 2012
    },
    "MPI-ESM-LR": {"ensemble": "r(1:3)i1p1", "start_year": 1960, "end_year": 2010},
    "MIROC5": {"ensemble": "r(1:6)i1p1", "start_year": 1959, "end_year": 2010},
}

CMIP6_MODELS = {
    "CanESM5": {
        "ensemble": "r(1:20)i1p2f1",
        "grid": "gn",
        "start_year": 1960,
        "end_year": 2010,
    },
    "EC-Earth3": {
        "ensemble": "r(1:10)i1p1f1",
        "grid": "gr",
        "start_year": 1960,
        "end_year": 2010,
    },
    "IPSL-CM6A-LR": {
        "ensemble": "r(1:10)i1p1f1",
        "grid": "gr",
        "start_year": 1960,
        "end_year": 2010,
    },
    "MIROC6": {
        "ensemble": "r(1:10)i1p1f1",
        "grid": "gn",
        "start_year": 1960,
        "end_year": 2010,
    },
    "HadGEM3-GC31-MM": {
        "ensemble": "r(1:10)i1p1f2",
        "grid": "gn",
        "start_year": 1960,
        "end_year": 2010,
    },
    "MPI-ESM1-2-HR": {
        "ensemble": "r(1:10)i1p1f1",
        "grid": "gn",
        "start_year": 1960,
        "end_year": 2010,
    },
    "CESM1-1-CAM5-CMIP5": {
        "ensemble": "r(1:40)i1p1f1",
        "grid": "gn",
        "start_year": 1960,
        "end_year": 2010,
    },
    "NorCPM1": {
        "ensemble": "r(1:10)i(1:2)p1f1",
        "grid": "gn",
        "start_year": 1960,
        "end_year": 2010,
    },
}


def get_cmip5_datasets(model=None):
    if model is not None:
        if model in CMIP5_MODELS.keys():
            models = {model: CMIP5_MODELS[model]}
        else:
            raise ValueError
    else:
        models = CMIP5_MODELS

    cmip5_datasets = []
    for model, meta in models.items():
        for yr in range(meta["start_year"], meta["end_year"] + 1):
            start_year = str(yr + 1)
            if model == "GFDL-CM2p1":
                end_year = str(yr + 9)
            else:
                end_year = str(yr + 10)
            d = (
                "{dataset: "
                + model
                + ", "
                + "project: "
                + "CMIP5, "
                + "exp: "
                + "decadal"
                + str(yr)
                + ", "
                + "ensemble: "
                + meta["ensemble"]
                + ", "
                + "start_year: "
                + start_year
                + ", "
                + "end_year: "
                + end_year
                + "}"
            )
            cmip5_datasets.append(d)
    return cmip5_datasets


def get_cmip6_datasets(model=None):
    if model is not None:
        if model in CMIP6_MODELS.keys():
            models = {model: CMIP6_MODELS[model]}
        else:
            raise ValueError
    else:
        models = CMIP6_MODELS

    cmip6_datasets = []
    for model, meta in models.items():
        for yr in range(meta["start_year"], meta["end_year"] + 1):
            start_year = str(yr + 1)
            end_year = str(yr + 9)
            d = (
                "{dataset: "
                + model
                + ", "
                + "project: "
                + "CMIP6, "
                + "activity: "
                + "DCPP, "
                + "exp: "
                + "dcppA-hindcast, "
                + "sub_experiment: "
                + "s"
                + str(yr)
                + ", "
                + "ensemble: "
                + meta["ensemble"]
                + ", "
                + "grid: "
                + meta["grid"]
                + ", "
                + "mip: "
                + "Amon, "
                + "start_year: "
                + start_year
                + ", "
                + "end_year: "
                + end_year
                + "}"
            )
            cmip6_datasets.append(d)
    return cmip6_datasets


def get_documentation(title, description):
    documentation_dict = {
        "documentation": {
            "title": title,
            "description": description,
            "authors": ["righi_mattia"],
        }
    }
    return documentation_dict


def get_s20_preprocessor():
    preprocessors_dict = {
        "preprocessors": {
            "general": {
                "regrid": {
                    "target_grid": {
                        "start_longitude": 0,
                        "end_longitude": 355,
                        "step_longitude": 5,
                        "start_latitude": 90,
                        "end_latitude": -90,
                        "step_latitude": -5,
                    },
                    "scheme": "linear",
                },
                # "extract_season": {"season": "djfm"},
                "extract_season": {"season": "sondjfm"},
            }
        }
    }
    return preprocessors_dict


def get_cvdp_preprocessor():
    preprocessors_dict = {
        "preprocessors": {
            "general": {
                "regrid": {
                    "target_grid": {
                        "start_longitude": 0,
                        "end_longitude": 355,
                        "step_longitude": 5,
                        "start_latitude": 90,
                        "end_latitude": -90,
                        "step_latitude": -5,
                    },
                    "scheme": "linear",
                }
            }
        }
    }
    return preprocessors_dict


def get_cvdp_diagnostic():
    diagnostics_dict = {
        "diagnostics": {
            "diagnostic1": {
                "description": "Run the NCAR CVDPackage",
                "variables": {
                    "ts": {"preprocessor": "general", "mip": "Amon"},
                    "tas": {"preprocessor": "general", "mip": "Amon"},
                    "pr": {"preprocessor": "general", "mip": "Amon"},
                    "psl": {"preprocessor": "general", "mip": "Amon"},
                },
                "scripts": {
                    "cvdp": {
                        "script": "cvdp/cvdp_wrapper.py",
                        "quickplot": {"plot_type": "pcolormesh"},
                    }
                },
            }
        }
    }
    return diagnostics_dict


def get_s20_grid_diagnostic(rootdir):
    diagnostics_dict = {
        "diagnostics": {
            "psl_field": {
                "title": "Mean sea-level pressure",
                "description": "Diagnostic to show mslp spatial grid",
                "variables": {"psl": {"preprocessor": "general", "mip": "Amon"}},
                "scripts": {
                    "psl_field": {
                        "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
                        "index": "psl_field",
                    }
                },
            },
            "tas_field": {
                "title": "Mean temperature",
                "description": "Diagnostic to show tas spatial grid",
                "variables": {"tas": {"preprocessor": "general", "mip": "Amon"}},
                "scripts": {
                    "tas_field": {
                        "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
                        "index": "tas_field",
                    }
                },
            },
            "pr_field": {
                "title": "Mean precipitation",
                "description": "Diagnostic to show pr spatial grid",
                "variables": {"pr": {"preprocessor": "general", "mip": "Amon"}},
                "scripts": {
                    "pr_field": {
                        "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
                        "index": "pr_field",
                    }
                },
            },
        }
    }
    return diagnostics_dict


def get_s20_diagnostic(rootdir):
    diagnostics_dict = {
        "diagnostics": {
            "nao": {
                "title": "NAO diagnostic",
                "description": "Diagnostic to compute the NAO index",
                "variables": {"psl": {"preprocessor": "general", "mip": "Amon"}},
                "scripts": {
                    "nao": {
                        "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
                        "index": "nao",
                    }
                },
            },
            "ea": {
                "title": "EA diagnostic",
                "description": "Diagnostic to compute the EA index",
                "variables": {"psl": {"preprocessor": "general", "mip": "Amon"}},
                "scripts": {
                    "ea": {
                        "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
                        "index": "ea",
                    }
                },
            },
            "amv": {
                "title": "AMV diagnostic",
                "description": "Diagnostic to compute the AMV index",
                "variables": {"tas": {"preprocessor": "general", "mip": "Amon"}},
                "scripts": {
                    "amv": {
                        "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
                        "index": "amv",
                    }
                },
            },
            "european_precip": {
                "title": "European precipitation diagnostic",
                "description": "Diagnostic to compute mean European precipitation",
                "variables": {"pr": {"preprocessor": "general", "mip": "Amon"}},
                "scripts": {
                    "european_precip": {
                        "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
                        "index": "european_precip",
                    }
                },
            },
            "uk_precip": {
                "title": "UK precipitation diagnostic",
                "description": "Diagnostic to compute mean UK precipitation",
                "variables": {"pr": {"preprocessor": "general", "mip": "Amon"}},
                "scripts": {
                    "uk_precip": {
                        "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
                        "index": "uk_precip",
                    }
                },
            },
            "uk_temp": {
                "title": "UK temperature diagnostic",
                "description": "Diagnostic to compute mean UK temperature",
                "variables": {"tas": {"preprocessor": "general", "mip": "Amon"}},
                "scripts": {
                    "uk_temp": {
                        "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
                        "index": "uk_temp",
                    }
                },
            },
            # "nino1": {
            #     "title": "Nino 1 diagnostic",
            #     "description": "Diagnostic to compute Nino 1 index",
            #     "variables": {"ts": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "nino1": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "nino1"
            #         }
            #     }
            # },
            # "nino2": {
            #     "title": "Nino 2 diagnostic",
            #     "description": "Diagnostic to compute Nino 1 index",
            #     "variables": {"ts": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "nino2": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "nino2"
            #         }
            #     }
            # },
            # "nino12": {
            #     "title": "Nino 12 diagnostic",
            #     "description": "Diagnostic to compute Nino 12 index",
            #     "variables": {"ts": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "nino12": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "nino12"
            #         }
            #     }
            # },
            # "nino3": {
            #     "title": "Nino 3 diagnostic",
            #     "description": "Diagnostic to compute Nino 3 index",
            #     "variables": {"ts": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "nino3": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "nino3"
            #         }
            #     }
            # },
            # "nino34": {
            #     "title": "Nino 34 diagnostic",
            #     "description": "Diagnostic to compute Nino 34 index",
            #     "variables": {"ts": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "nino34": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "nino34"
            #         }
            #     }
            # },
            # "nino4": {
            #     "title": "Nino 4 diagnostic",
            #     "description": "Diagnostic to compute Nino 4 index",
            #     "variables": {"ts": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "nino4": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "nino4"
            #         }
            #     }
            # },
            # "iod": {
            #     "title": "IOD diagnostic",
            #     "description": "Diagnostic to compute Nino 1 index",
            #     "variables": {"ts": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "iod": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "iod"
            #         }
            #     }
            # },
            # "pdv": {
            #     "title": "PDV diagnostic",
            #     "description": "Diagnostic to compute PDV index",
            #     "variables": {"ts": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "pdv": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "pdv"
            #         }
            #     }
            # },
            # "ipo": {
            #     "title": "IPO diagnostic",
            #     "description": "Diagnostic to IPO index",
            #     "variables": {"ts": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "ipo": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "ipo"
            #         }
            #     }
            # },
            # "sahel_precip": {
            #     "title": "Sahelian precipitation",
            #     "description": "Diagnostic to compute area-averaged Sahel precipitation",
            #     "variables": {"pr": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "sahel_precip": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "sahel_precip"
            #         }
            #     }
            # },
            "precip_field": {
                "title": "Global precipitation field",
                "description": "Diagnostic to compute global precipitation field",
                "variables": {"pr": {"preprocessor": "general", "mip": "Amon"}},
                "scripts": {
                    "precip_field": {
                        "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
                        "index": "precip_field"
                    }
                }
            },
            "temp_field": {
                "title": "Global temperature field",
                "description": "Diagnostic to compute global temperature field",
                "variables": {"pr": {"preprocessor": "general", "mip": "Amon"}},
                "scripts": {
                    "temp_field": {
                        "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
                        "index": "temp_field"
                    }
                }
            }#,
            # "cr_precip_field": {
            #     "title": "Costa Rica precipitation field",
            #     "description": "Diagnostic to compute Costa Rica precipitation field",
            #     "variables": {"pr": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "cr_precip_field": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "cr_precip_field"
            #         }
            #     }
            # },
            # "cr_temp_field": {
            #     "title": "Costa Rica temperature field",
            #     "description": "Diagnostic to compute Costa Rica temperature field",
            #     "variables": {"tas": {"preprocessor": "general", "mip": "Amon"}},
            #     "scripts": {
            #         "cr_temp_field": {
            #             "script": os.path.join(rootdir, "diag_scripts/diag_indices.py"),
            #             "index": "cr_temp_field"
            #         }
            #     }
            # }
        }
    }
    return diagnostics_dict


def get_project_rootdir(project):
    if project == "CMIP5":
        return CMIP5_ROOTDIR
    elif project == "CMIP6":
        return CMIP6_ROOTDIR
    else:
        raise ("Invalid project!")


def write_recipe(
    filename,
    documentation_dict,
    dataset_dict,
    preprocessor_dict=None,
    diagnostics_dict=None,
):
    with open(filename, "w") as f:
        # Write documentation
        yaml.dump(documentation_dict, f, default_flow_style=False, sort_keys=False)
        f.write("\n")
        # Write datasets
        f.write("datasets:\n")
        for i in range(len(dataset_dict)):
            d = dataset_dict[i]
            f.write("  - " + d + "\n")
        f.write("\n")
        # Write preprocessor
        if preprocessor_dict is not None:
            yaml.dump(preprocessor_dict, f, default_flow_style=False, sort_keys=False)
            f.write("\n")

        # Write diagnostics
        if diagnostics_dict is not None:
            yaml.dump(diagnostics_dict, f, default_flow_style=False, sort_keys=False)
    return None


def gen_s20_grid_recipe():
    documentation_dict = get_documentation("NAO", "Compute spatial fields for plotting")
    cmip5_datasets = get_cmip5_datasets()
    cmip6_datasets = get_cmip6_datasets()
    preprocessor_dict = get_s20_preprocessor()
    datasets = {"CMIP6": cmip6_datasets, "CMIP5": cmip5_datasets}
    for project, dataset in datasets.items():
        rootdir = get_project_rootdir(project)
        diagnostic_dict = get_s20_grid_diagnostic(rootdir)
        script_dir = pathlib.Path(__file__).parent.resolve()
        recipe_fn = os.path.join(
            script_dir,
            "esmvaltool-recipes",
            "recipe_s20_grid_" + project.lower() + "_autogen.yml",
        )
        write_recipe(
            recipe_fn, documentation_dict, dataset, preprocessor_dict, diagnostic_dict
        )


def gen_s20_recipe():
    documentation_dict = get_documentation(
        "NAO", "Compute indices for NAO-matching technique"
    )
    cmip5_datasets = get_cmip5_datasets()
    cmip6_datasets = get_cmip6_datasets()
    preprocessor_dict = get_s20_preprocessor()
    datasets = {"CMIP6": cmip6_datasets, "CMIP5": cmip5_datasets}
    for project, dataset in datasets.items():
        rootdir = get_project_rootdir(project)
        diagnostic_dict = get_s20_diagnostic(rootdir)
        script_dir = pathlib.Path(__file__).parent.resolve()
        recipe_fn = os.path.join(
            script_dir,
            "esmvaltool-recipes",
            "recipe_s20_" + project.lower() + "_autogen.yml",
        )
        write_recipe(
            recipe_fn, documentation_dict, dataset, preprocessor_dict, diagnostic_dict
        )


# def gen_s20_recipe():
#     documentation_dict = get_documentation(
#         "NAO", "Compute indices for NAO-matching technique"
#     )
#     cmip5_models = list(CMIP5_MODELS.keys())
#     cmip6_models = list(CMIP6_MODELS.keys())
#     models = cmip5_models + cmip6_models
#     preprocessor_dict = get_s20_preprocessor()
#     # datasets = {"CMIP6": cmip6_models, "CMIP5": cmip5_models}
#     for model in models:
#         if model in cmip5_models:
#             project = 'CMIP5'
#             dataset = get_cmip5_datasets(model=model)
#         elif model in cmip6_models:
#             project = 'CMIP6'
#             dataset = get_cmip6_datasets(model=model)

#         rootdir = get_project_rootdir(project)
#         diagnostic_dict = get_s20_diagnostic(rootdir)
#         script_dir = pathlib.Path(__file__).parent.resolve()
#         recipe_fn = os.path.join(
#             script_dir,
#             "esmvaltool-recipes",
#             "recipe_s20_" + project.lower() + '_' + model.replace('-', '_').lower() + "_autogen.yml",
#         )
#         write_recipe(
#             recipe_fn, documentation_dict, dataset, preprocessor_dict, diagnostic_dict
#         )


# def gen_cvdp_recipe():
#     documentation_dict = get_documentation(
#         "CVDP", "Execute CVDP package in ESMValTool framework"
#     )
#     cmip5_datasets = get_cmip5_datasets()
#     cmip6_datasets = get_cmip6_datasets()
#     preprocessor_dict = get_cvdp_preprocessor()
#     datasets = {"CMIP6": cmip6_datasets, "CMIP5": cmip5_datasets}
#     for project, dataset in datasets.items():
#         # rootdir = get_project_rootdir(project)
#         diagnostic_dict = get_cvdp_diagnostic()
#         script_dir = pathlib.Path(__file__).parent.resolve()
#         recipe_fn = os.path.join(
#             script_dir,
#             "esmvaltool-recipes",
#             "recipe_cvdp_" + project.lower() + "_autogen.yml",
#         )
#         write_recipe(
#             recipe_fn, documentation_dict, dataset, preprocessor_dict, diagnostic_dict
#         )


if __name__ == "__main__":
    gen_s20_recipe()
    gen_s20_grid_recipe()
    # gen_cvdp_recipe()
