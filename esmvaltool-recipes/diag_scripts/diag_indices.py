#!/usr/bin/env python3

import logging
from pathlib import Path

import iris
import xarray

from esmvaltool.diag_scripts.shared import (
    group_metadata,
    run_diagnostic,
    # get_diagnostic_filename,
    # ProvenanceLogger,
)

from utils import (
    _extract_nao_ts,
    _extract_ea_ts,
    _extract_amv_ts,
    _extract_european_precip_ts,
    _extract_uk_precip_ts,
    _extract_uk_temp_ts,
    _extract_nino1_ts,
    _extract_nino2_ts,
    _extract_nino12_ts,
    _extract_nino3_ts,
    _extract_nino34_ts,
    _extract_nino4_ts,
    _extract_iod_ts,
    _extract_pdv_ts,
    _extract_ipo_ts,
    _extract_sahel_precip_ts,
    # _extract_uk_precip_field,
    _extract_precip_field,
    _extract_temp_field,
    # _extract_cr_precip_field,
    # _extract_cr_temp_field,
    _compute_djfm,
    get_provenance_record,
    save_xarray_data,
)


logger = logging.getLogger(Path(__file__).stem)


def compute_diagnostic(filename, attributes, index):
    logger.debug("Loading %s", filename)
    logger.debug("Running example computation")
    x = iris.load_cube(filename)
    if index == "nao":
        x_index = _extract_nao_ts(x)
    elif index == "nino1":
        x_index = _extract_nino1_ts(x)
    elif index == "nino2":
        x_index = _extract_nino2_ts(x)
    elif index == "nino12":
        x_index = _extract_nino12_ts(x)
    elif index == "nino3":
        x_index = _extract_nino3_ts(x)
    elif index == "nino34":
        x_index = _extract_nino34_ts(x)
    elif index == "nino4":
        x_index = _extract_nino4_ts(x)
    elif index == "iod":
        x_index = _extract_iod_ts(x)
    elif index == "pdv":
        x_index = _extract_pdv_ts(x)
    elif index == "ipo":
        x_index = _extract_ipo_ts(x)
    elif index == "sahel_precip":
        x_index = _extract_sahel_precip_ts(x)
    elif index == "ea":
        x_index = _extract_ea_ts(x)
    elif index == "amv":
        x_index = _extract_amv_ts(x)
    elif index == "european_precip":
        x_index = _extract_european_precip_ts(x)
    elif index == "uk_precip":
        x_index = _extract_uk_precip_ts(x)
    elif index == "uk_temp":
        x_index = _extract_uk_temp_ts(x)
    # elif index == "uk_precip_field":
    #     x_index = _extract_uk_precip_field(x)
    elif index == "precip_field":
        x_index = _extract_precip_field(x)
    elif index == "temp_field":
        x_index = _extract_temp_field(x)
    # elif index == "cr_precip_field":
    #     x_index = _extract_cr_precip_field(x)
    # elif index == "cr_temp_field":
    #     x_index = _extract_cr_temp_field(x)
    elif index == "psl_field":
        x_index = _compute_djfm(x, filename)
    elif index == "tas_field":
        x_index = _compute_djfm(x, filename)
    elif index == "pr_field":
        x_index = _compute_djfm(x, filename)
    else:
        raise ValueError("Unrecognised index")
    ds = xarray.DataArray.from_iris(x_index)
    ds.name = index
    return ds


def main(cfg):
    # Get a description of the preprocessed data that we will use as input.
    input_data = cfg["input_data"].values()
    index = cfg["index"].lower()
    # Loop over datasets in alphabetical order
    groups = group_metadata(input_data, "variable_group", sort="dataset")
    for group_name in groups:
        logger.info("Processing variable %s", group_name)
        for attributes in groups[group_name]:
            logger.info("Processing dataset %s", attributes["dataset"])
            input_file = attributes["filename"]
            ds = compute_diagnostic(input_file, attributes, index)
            output_basename = Path(input_file).stem
            if group_name != attributes["short_name"]:
                output_basename = group_name + "_" + output_basename
            provenance_record = get_provenance_record(
                attributes, ancestor_files=[input_file]
            )
            save_xarray_data(output_basename, provenance_record, cfg, ds)


if __name__ == "__main__":
    with run_diagnostic() as config:
        main(config)
