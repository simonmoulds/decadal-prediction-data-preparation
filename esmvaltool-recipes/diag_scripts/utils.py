#!/usr/bin/env python3

import logging
from pathlib import Path
from pprint import pformat

import os
import iris
import numpy as np
import xarray
import re

from esmvaltool.diag_scripts.shared import (
    group_metadata,
    run_diagnostic,
    # save_data,
    # save_figure,
    select_metadata,
    sorted_metadata,
    get_diagnostic_filename,
    ProvenanceLogger,
)

# from esmvaltool.diag_scripts.shared.plot import quickplot

logger = logging.getLogger(Path(__file__).stem)


def get_provenance_record(attributes, ancestor_files):
    """Create a provenance record describing the diagnostic data and plot."""
    caption = (
        "Average {long_name} between {start_year} and {end_year} "
        "according to {dataset}.".format(**attributes)
    )
    record = {
        "caption": caption,
        "statistics": ["mean"],
        "domains": ["global"],
        "plot_types": ["zonal"],
        "authors": [
            "andela_bouwe",
            "righi_mattia",
        ],
        "references": [
            "acknow_project",
        ],
        "ancestors": ancestor_files,
    }
    return record


# Adapted from ESMValTool/esmvaltool/diag_scripts/shared/_base.py
def save_xarray_data(basename, provenance, cfg, ds, **kwargs):
    """Save the data used to create a plot to file.

    Parameters
    ----------
    basename: str
        The basename of the file.
    provenance: dict
        The provenance record for the data.
    cfg: dict
        Dictionary with diagnostic configuration.
    cube: iris.cube.Cube
        Data cube to save.
    **kwargs:
        Extra keyword arguments to pass to :obj:`iris.save`.

    See Also
    --------
    ProvenanceLogger: For an example provenance record that can be used
        with this function.
    """
    if "target" in kwargs:
        raise ValueError(
            "Please use the `basename` argument to specify the output file"
        )

    filename = get_diagnostic_filename(basename, cfg)
    logger.info("Saving analysis results to %s", filename)
    ds.to_netcdf(filename)
    with ProvenanceLogger(cfg) as provenance_logger:
        provenance_logger.log(filename, provenance)


def _extract_ts(x, xmin, xmax, ymin, ymax):
    x_copy = x.copy()
    # lon_name = get_longitude_name(x_copy)
    # lat_name = get_latitude_name(x_copy)
    # if (x_copy.coord(lon_name).bounds is None):
    #     x_copy.coord(lon_name).guess_bounds()
    # if (x_copy.coord(lat_name).bounds is None):
    #     x_copy.coord(lat_name).guess_bounds()
    # positive_lon = has_positive_longitude(x_copy)
    # xmin, xmax = transform_longitude(xmin, xmax, positive_lon)
    box = x_copy.intersection(longitude=(xmin, xmax), latitude=(ymin, ymax))
    grid_areas = iris.analysis.cartography.area_weights(box)
    ts = box.collapsed(
        ["latitude", "longitude"], iris.analysis.MEAN, weights=grid_areas
    )
    return ts


def _extract_field(x, xmin, xmax, ymin, ymax):
    x_copy = x.copy()
    subset = x_copy.intersection(longitude=(xmin, xmax), latitude=(ymin, ymax))
    return subset

# def compute_djfm(x): #, varname):
#     ds = xarray.DataArray.from_iris(x)
#     def is_djfm(month):
#         return (month >= 12) | (month <= 3)
#     ds_djfm = ds.sel(time=is_djfm(ds['time.month']))
#     yrs = []
#     for i in range(ds_djfm['time'].size):
#         yr = ds_djfm['time.year'].values[i]
#         month = ds_djfm['time.month'].values[i]
#         if month == 12:
#             yrs.append(yr)
#         else:
#             yrs.append(yr-1)
#     ds_djfm['season_start_year'] = (('time',), yrs)
#     ds_djfm['counter'] = (('time',), [1,] * len(yrs))
#     ds_djfm = ds_djfm.groupby('season_start_year').sum('time')
#     # Limit dataset to complete [boreal winter] seasons
#     print(ds_djfm)
#     complete_index = ds_djfm['counter'].values == 4
#     ds_djfm = ds_djfm.sel(season_start_year=complete_index)
#     # ds_djfm[varname] = ds_djfm[varname] / 4
#     ds_djfm = ds_djfm / 4
#     ds_djfm = ds_djfm.drop('counter')
#     ds_djfm = ds_djfm.to_iris()
#     return ds_djfm


def parse_filepath(fpath):
    # Parse CMIP-formatted filename to get key id variables
    fname = os.path.basename(fpath)
    fname = fname.split("_")
    project = fname[0]
    model = fname[1]
    mip = fname[2]
    exp = fname[3]
    if project == "CMIP5":
        ens = fname[4]
        init_year = exp.replace("decadal", "")
    elif project == "CMIP6":
        sub_exp = fname[4]
        sub_exp = sub_exp.split("-")
        ens = sub_exp[1]
        init_year = sub_exp[0].replace("s", "")
        # exp = sub_exp
    out = {
        "project": project,
        "model": model,
        "mip": mip,
        "experiment": exp,
        "ensemble": ens,
        "init_year": int(init_year),
    }
    return out


def _compute_djfm(x, filename, start_year=2, end_year=9):
    # Compute the mean value for DJFM season.
    #
    # Args:
    #   x         : Iris dataset.
    #   varname   : string. Variable name.
    #   init_year : int. Initialization year of `ds`.
    #   start_year: int. Start forecast lead time.
    #   end_year  : int. End forecast lead time.
    #
    # Returns:
    #   xarray dataset.

    meta = parse_filepath(filename)
    init_year = int(meta["init_year"])

    da = xarray.DataArray.from_iris(x)
    varname = str(da.name)
    ds = da.to_dataset()

    # Sometimes Iris "fixes" a non-monotonic time
    # dimension by adding another dimension
    # called 'dim_0' - account for this here
    dimnames = list(ds.dims.keys())
    time_dimname = "time"
    if "time" not in dimnames:
        if "dim_0" in dimnames:
            time_dimname = "dim_0"
        else:
            if len(dimnames) == 1:
                time_dimname = dimnames[0]
            else:
                raise ValueError("Ambiguous time dimension")

    # # If variable is preciptation we need to convert kg m-2 s-1 to mm/day
    # if varname == 'pr':
    #     # days_in_month = ds[time_dimname].dt.days_in_month
    #     # ds[varname] *= (days_in_month * 60 * 60 * 24) # mm/month
    #     ds[varname] *= (60 * 60 * 24) # mm/day

    ds["counter"] = (
        (time_dimname,),
        [
            1,
        ]
        * len(ds.time),
    )
    ds = ds.groupby("season_year").sum(time_dimname)
    # Limit dataset to complete [boreal winter] seasons
    complete_index = ds["counter"].values == 4
    ds = ds.sel(season_year=complete_index)

    # Divide by four to get mean value
    # if varname != 'pr':
    ds[varname] = ds[varname] / 4

    # Add lead time
    # [N.B. season_year (added automatically by Iris)
    # defines the year of final month in the season]
    ds["lead_time"] = (("season_year",), ds.season_year.values - int(init_year))

    def _is_yr2to9(year):  # , init_year):
        return (year >= start_year) & (year <= end_year)

    ds = ds.sel(season_year=_is_yr2to9(ds["lead_time"]))
    # ds = ds.drop(['counter','lead_time'])
    ds = ds.mean("season_year")
    da = ds[varname].to_iris()
    return da

def _extract_nao_ts(x):
    iceland_ts = _extract_ts(x, -25, -16, 63, 70)
    azores_ts = _extract_ts(x, -28, -20, 36, 40)
    nao = azores_ts - iceland_ts
    return nao


# NINO indices require SST
def _extract_nino1_ts(x):
    # Nino 1 - SST anomalies
    nino1 = _extract_ts(x, -90, -80, -10, -5)
    return nino1


def _extract_nino2_ts(x):
    # Nino 2 - SST anomalies
    nino2 = _extract_ts(x, -90, -80, -5, 0)
    return nino2


def _extract_nino12_ts(x):
    # Nino 1.2 - SST anomalies
    nino12 = _extract_ts(x, -90, -80, -10, 0)
    return nino12


def _extract_nino3_ts(x):
    # Nino 3 - SST anomalies
    nino3 = _extract_ts(x, -150, -90, -5, 5)
    return nino3


def _extract_nino34_ts(x):
    # Nino 3.4 - SST anomalies
    nino34 = _extract_ts(x, -170, -120, -5, 5)
    return nino34


def _extract_nino4_ts(x):
    # Nino 4 - SST anomalies
    nino4 = _extract_ts(x, 160, -150, -5, 5)
    return nino4


def _extract_iod_ts(x):
    # Dipole Mode Index [DMI - https://psl.noaa.gov/gcos_wgsp/Timeseries/DMI/]
    # SST
    iod_west = _extract_ts(x, 50, 70, -10, 10)
    iod_east = _extract_ts(x, 90, 110, -10, 0)
    return iod_west - iod_east


def _extract_pdv_ts(x):
    # Pacific Decadal Variability [PDV]
    # SST
    tropical = _extract_ts(x, -160, -110, -10, 6)
    northern = _extract_ts(x, -180, -145, 30, 45)
    return tropical - northern


def _extract_ipo_ts(x):
    # Interdecadal Pacific Oscillation
    # SST
    northern = _extract_ts(x, 140, -145, 25, 45)
    middle = _extract_ts(x, 170, -90, -10, 10)
    southern = _extract_ts(x, 150, -160, -50, -15)
    ipo = middle - 0.5 * (northern + southern)
    return ipo


def _extract_ea_ts(x):
    # East Atlantic
    # MSLP
    def _matlab_mod(a, b):
        return a - b * np.floor(a / b)

    xcoord = _matlab_mod(-27.5, 360.0)
    ycoord = 52.5
    xr = xarray.DataArray.from_iris(x)
    ea = xr.sel(lat=ycoord, lon=xcoord, method="nearest")
    ea = ea.to_iris()
    return ea


def _extract_amv_ts(x):
    # Atlantic Multidecadal Variability
    # T
    north_atlantic_ts = _extract_ts(x, -80, 0, 0, 60)
    global_ts = _extract_ts(x, -180, 180, -60, 60)
    amv = north_atlantic_ts - global_ts
    return amv


def _extract_european_precip_ts(x):
    # Northern Europe precipitation
    # P
    european_precip_ts = _extract_ts(x, -10, 25, 55, 70)
    return european_precip_ts


def _extract_uk_precip_ts(x):
    # UK precipitation
    # P
    uk_precip_ts = _extract_ts(x, -8, 2, 50, 59)
    return uk_precip_ts


def _extract_uk_temp_ts(x):
    # UK temperature
    # T
    uk_temp_ts = _extract_ts(x, -8, 2, 50, 59)
    return uk_temp_ts


def _extract_sahel_precip_ts(x):
    # Sahelian preciptiation
    # P
    sahel_precip_ts = _extract_ts(x, -16, 36, 10, 20)
    return sahel_precip_ts


def _extract_uk_precip_field(x):
    uk_precip_field = _extract_field(x, -8, 2, 50, 59)
    return uk_precip_field


# NOT USED:
#
# def is_yr2to9(year, month, yr_start, yr_end, month_start, month_end):
#     try:
#         start_index = np.where(
#             (year == yr_start)
#             & (month == month_start)
#         )[0][0]
#         end_index = np.where((year == yr_end) & (month == month_end))[0][0]
#     except IndexError:
#         raise
#     index = np.array([False] * len(year))
#     index[slice(start_index, end_index+1)] = True
#     return index


# def compute_mean_djfm(ds, varname):
#     def is_djfm(month):
#         return (month >= 12) | (month <= 3)
#     ds_djfm = ds.sel(time=is_djfm(ds['time.month']))
#     yrs = []
#     for i in range(ds_djfm['time'].size):
#         yr = ds_djfm['time.year'].values[i]
#         month = ds_djfm['time.month'].values[i]
#         if month == 12:
#             yrs.append(yr)
#         else:
#             yrs.append(yr-1)
#     ds_djfm['season_start_year'] = (('time',), yrs)
#     ds_djfm['counter'] = (('time',), [1,] * len(yrs))
#     ds_djfm = ds_djfm.groupby('season_start_year').sum('time')
#     # Limit dataset to complete [boreal winter] seasons
#     complete_index = ds_djfm['counter'].values == 4
#     ds_djfm = ds_djfm.sel(season_start_year=complete_index)
#     ds_djfm[varname] = ds_djfm[varname] / 4
#     ds_djfm = ds_djfm.drop('counter')
#     return ds_djfm


# def get_forecast_init_year(attributes):
#     """Get forecast initialization year."""
#     project = attributes['project']
#     if project == 'CMIP5':
#         return int(re.search(r"decadal(\d{4})", attributes['exp']).group(1))
#     elif project == 'CMIP6':
#         return int(re.search(r"s(\d{4})", attributes['sub_experiment']).group(1))
#     else:
#         raise
