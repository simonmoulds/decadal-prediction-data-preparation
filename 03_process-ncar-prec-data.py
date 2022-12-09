#!/usr/bin/env python3

import os
import glob
import numpy as np
import iris
import iris.pandas
import iris.coord_categorisation
import xarray
import yaml
import click

from tqdm import tqdm

VALID_Y_NAMES = ["latitude", "lat"]
VALID_X_NAMES = ["longitude", "lon"]
VALID_TIME_NAMES = ["t", "time"]


def _get_latitude_name(x):
    coord_nms = _coord_names(x)
    return [nm for nm in coord_nms if nm in VALID_Y_NAMES][0]


def _coord_names(x):
    # Coordinate names from an Iris cube
    return tuple([coord.name() for coord in x.coords()])


def _get_time_name(x):
    coord_nms = _coord_names(x)
    return [nm for nm in coord_nms if nm in VALID_TIME_NAMES][0]


def _get_longitude_name(x):
    coord_nms = _coord_names(x)
    return [nm for nm in coord_nms if nm in VALID_X_NAMES][0]


def _matlab_mod(a, b):
    # Analog of Matlab's mod() function
    return a - b * np.floor(a / b)


def _has_positive_longitude(x):
    lon_name = _get_longitude_name(x)
    lon = x.coord(lon_name).points
    positive_lon = np.all(lon >= 0)

    return positive_lon


def _transform_longitude(xmin, xmax, positive_lon):
    # Transform standard (-180 to 180) longitude
    # value to (0 to 360) value, as is commonly
    # (always?) used by CMIP models
    if positive_lon:
        xmin = _matlab_mod(xmin, 360.0)
        xmax = _matlab_mod(xmax, 360.0)
    if xmin > xmax:
        xmin -= 360
    return xmin, xmax


def _regrid_cube(source, target):
    # Ensure grid coords have the same name
    target_lon_name = _get_longitude_name(target)
    target_lat_name = _get_latitude_name(target)
    source_lon_name = _get_longitude_name(source)
    source_lat_name = _get_latitude_name(source)
    source.coord(source_lon_name).rename(target_lon_name)
    source.coord(source_lat_name).rename(source_lat_name)

    # Make sure coord_systems are the same (this feels a bit hacky...)
    for coord_nm in [target_lat_name, target_lon_name]:
        source.coord(coord_nm).coord_system = target.coord(coord_nm).coord_system

    # Perform the regridding
    regrid_source = source.regrid(target, iris.analysis.Linear())
    return regrid_source


def _extract_ts(x, xmin, xmax, ymin, ymax):
    # work on a copy
    x_copy = x.copy()
    lon_name = _get_longitude_name(x_copy)
    lat_name = _get_latitude_name(x_copy)
    if x_copy.coord(lon_name).bounds is None:
        x_copy.coord(lon_name).guess_bounds()
    if x_copy.coord(lat_name).bounds is None:
        x_copy.coord(lat_name).guess_bounds()
    positive_lon = _has_positive_longitude(x_copy)
    xmin, xmax = _transform_longitude(xmin, xmax, positive_lon)
    box = x_copy.intersection(longitude=(xmin, xmax), latitude=(ymin, ymax))
    grid_areas = iris.analysis.cartography.area_weights(box)
    ts = box.collapsed(
        ["latitude", "longitude"], iris.analysis.MEAN, weights=grid_areas
    )
    return ts


def _extract_european_precip_ts(x):
    europe_prec = _extract_ts(x, -10, 25, 55, 70)
    return europe_prec


def _extract_uk_precip_ts(x):
    uk_prec = _extract_ts(x, -8, 2, 50, 59)
    return uk_prec


def _extract_field(x, xmin, xmax, ymin, ymax):
    x_copy = x.copy()
    subset = x_copy.intersection(longitude=(xmin, xmax), latitude=(ymin, ymax))
    return subset


def _extract_uk_precip_field(x):
    # uk_precip_field = _extract_field(x, -8, 2, 50, 59)
    uk_precip_field = _extract_field(x, -10, 2, 50, 60)
    return uk_precip_field


def _extract_precip_field(x):
    return x

# def _extract_index(ds, index_name, column_name=None):
#     if index_name == "european_precip":
#         ds_index = _extract_european_precip_ts(ds)
#     elif index_name == "uk_precip":
#         ds_index = _extract_uk_precip_ts(ds)
#     else:
#         raise "Index not yet implemented"

#     if column_name is None:
#         column_name = index_name

#     # Convert to data frame
#     df = iris.pandas.as_data_frame(ds_index)
#     df = df.rename(columns={0: column_name})
#     df.index.name = "time"
#     df = df.reset_index(level="time")
#     tm = df["time"].values
#     df["year"] = [tm.year for tm in tm]
#     df["month"] = [tm.month for tm in tm]
#     df = df.drop("time", axis=1)
#     # Check for any duplicated values which we have to remove
#     _, idx = np.unique(tm, return_index=True)
#     df = df.iloc[idx]
#     df.reset_index()
#     return df

def _get_filename(path, init_year, member, variable):
    ptn = (
        path
        + "/"
        + variable
        + "/*"
        + str(init_year)
        + "*"
        + str(member).zfill(3)
        + "*"
        + variable
        + "*.nc"
    )
    f = glob.glob(ptn)
    if len(f) != 1:
        raise
    return f[0]


def _compute_djfm(
    x, init_year, start_year=2, end_year=9
):  # , varname, init_year, start_year=2, end_year=9):
    da = xarray.DataArray.from_iris(x)
    varname = str(da.name)
    ds = da.to_dataset()
    time_dimname = "time"
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
    # Divide by four to get mean value, unless precipitation
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
    # da = ds[varname].to_iris()
    return ds[varname]


def _get_output_filename(
    init_year, member, project="CMIP6", model="CESM1-1-CAM5-CMIP5"
):
    fn = (
        project
        + "_"
        + model
        + "_Amon_dcppA-hindcast_s"
        + str(init_year)
        + "-"
        + "r"
        + str(member)
        + "i1p1f1"
        + "_pr_gn_"
        + str(init_year + 1)
        + "-"
        + str(init_year + 8)
        + ".nc"
    )
    return fn


@click.command()
@click.option("--config", default="config.yml", help="YAML configuration file")
def main(config):
    # config = "test-config.yml"  # LOCAL TESTING ONLY - REMOVE
    # config = "~/decadal-flood-prediction/arc-config.yml"
    with open(config, "r") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    ncar_path = config["aux_data"]["ncar_precip"]
    output_dir = ncar_path

    # Regrid using HadSLP data as target
    hadslp2r_filename = os.path.join(
        config["observed_data"]["hadslp2r"], "slp.mnmean.real.nc"
    )
    target = iris.load_cube(hadslp2r_filename, "slp")

    # Create output directories
    european_precip_outdir = os.path.join(
        output_dir,
        "recipe1/work/european_precip/european_precip"
    )
    uk_precip_outdir = os.path.join(
        output_dir,
        "recipe1/work/uk_precip/uk_precip"
    )
    # uk_precip_field_outdir = os.path.join(
    #     output_dir,
    #     "recipe1/work/uk_precip_field/uk_precip_field"
    # )
    precip_field_outdir = os.path.join(
        output_dir,
        "recipe1/work/precip_field/precip_field"
    )
    os.makedirs(european_precip_outdir, exist_ok=True)
    os.makedirs(uk_precip_outdir, exist_ok=True)
    os.makedirs(precip_field_outdir, exist_ok=True)
    # os.makedirs(uk_precip_field_outdir, exist_ok=True)

    init_years = [i for i in range(1960, 2015)]
    members = [i for i in range(1, 41)]
    variables = ["PRECC", "PRECL"]
    for i in tqdm(range(len(init_years))):
        init_year = init_years[i]
        for j in range(len(members)):
            member = members[j]
            european_precip_dict = {}
            uk_precip_dict = {}
            # uk_precip_field_dict = {}
            precip_field_dict = {}

            for k in range(len(variables)):
                variable = variables[k]
                source_fn = _get_filename(ncar_path, init_year, member, variable)
                # source_fn = 'data-raw/ncar_prec_data/b.e11.BDP.f09_g16.1983-11.001.cam.h0.PRECC.198311-199312.nc'
                xr_source = xarray.open_dataset(source_fn)[variable]
                source = xr_source.to_iris()
                ds = _regrid_cube(source, target)
                iris.coord_categorisation.add_season(
                    # ds, "time", seasons=["djfm", "am", "jjas", "on"]
                    ds, "time", seasons=["sondjfm", "amjja"]
                )
                iris.coord_categorisation.add_season_year(
                    # ds, "time", seasons=["djfm", "am", "jjas", "on"]
                    ds, "time", seasons=["sondjfm", "amjja"]
                )
                ds = ds.extract(iris.Constraint(season="sondjfm"))

                # European precip
                european_precip = _extract_european_precip_ts(ds)
                european_precip = xarray.DataArray.from_iris(european_precip)
                european_precip.name = "european_precip"
                european_precip_dict[variable] = european_precip

                # UK precip
                uk_precip = _extract_uk_precip_ts(ds)
                uk_precip = xarray.DataArray.from_iris(uk_precip)
                uk_precip.name = "uk_precip"
                uk_precip_dict[variable] = uk_precip

                # # UK precip field
                # uk_precip_field = _extract_uk_precip_field(ds)
                # uk_precip_field = xarray.DataArray.from_iris(uk_precip_field)
                # uk_precip_field.name = "uk_precip_field"
                # uk_precip_field_dict[variable] = uk_precip_field

                # Global precip field
                precip_field = _extract_precip_field(ds)
                precip_field = xarray.DataArray.from_iris(precip_field)
                precip_field.name = "precip_field"
                precip_field_dict[variable] = precip_field

            european_precip = (
                european_precip_dict["PRECC"] + european_precip_dict["PRECL"]
            )
            uk_precip = (
                uk_precip_dict["PRECC"] + uk_precip_dict["PRECL"]
            )
            # uk_precip_field = (
            #     uk_precip_field_dict['PRECC'] + uk_precip_field_dict['PRECL']
            # )
            precip_field = (
                precip_field_dict['PRECC'] + precip_field_dict['PRECL']
            )

            # Convert m/s to mm/s
            european_precip *= 1000.0
            uk_precip *= 1000.0
            # uk_precip_field *= 1000.0
            precip_field *= 1000.0

            fn = _get_output_filename(init_year, member)
            european_precip.to_netcdf(os.path.join(european_precip_outdir, fn))
            uk_precip.to_netcdf(os.path.join(uk_precip_outdir, fn))
            precip_field.to_netcdf(os.path.join(precip_field_outdir, fn))
            # uk_precip_field.to_netcdf(os.path.join(uk_precip_field_outdir, fn))


if __name__ == "__main__":
    main()


# # TESTING:
# config = "test-config.yml"
# with open(config, 'r') as f:
#     config = yaml.load(f, Loader=yaml.FullLoader)
# hadslp2r_filename = os.path.join(
#     config['observed_data']['hadslp2r'],
#     'slp.mnmean.real.nc'
# )
# target = iris.load_cube(hadslp2r_filename, 'slp')
# source = iris.load_cube('data-raw/ncar_prec_data/b.e11.BDP.f09_g16.1983-11.001.cam.h0.PRECC.198311-199312.nc', 'PRECC')
# ds = _regrid_cube(source, target)
# # European precipitation
# europe_precip_df = _extract_index(ds, "european_precip")
# europe_precip_df['days_in_month'] = europe_precip_df.apply(
#     lambda x: monthrange(int(x['year']), int(x['month']))[1],
#     axis=1
# )
# europe_precip_df['european_precip'] *= (60 * 60 * 24 * europe_precip_df['days_in_month'])
# europe_precip_df = europe_precip_df.drop('days_in_month', axis=1)

# # UK precipitation
# uk_precip_df = _extract_index(ds, "uk_precip")
# uk_precip_df['days_in_month'] = uk_precip_df.apply(
#     lambda x: monthrange(int(x['year']), int(x['month']))[1],
#     axis=1
# )
# uk_precip_df['uk_precip'] *= (60 * 60 * 24 * uk_precip_df['days_in_month'])
# uk_precip_df = uk_precip_df.drop('days_in_month', axis=1)

# # Get spatial plot
# time_dimname = 'time'
# varname = 'PRECC'
# init_year = 1983

# def is_djfm(month):
#     return (month >= 12) | (month <= 3)

# da = xarray.DataArray.from_iris(ds)
# days_in_month = da[time_dimname].dt.days_in_month
# da *= (days_in_month * 60 * 60 * 24)
# da = da.sel(time = is_djfm(da['time.month']))
# ds = da.to_dataset()

# tm_month = ds['time.month'].values
# tm_year = ds['time.year'].values
# season_year = tm_year
# season_year[tm_month == 12] += 1

# ds['season_year'] = ((time_dimname,), season_year)
# ds['counter'] = ((time_dimname,), [1, ] * len(ds.time))
# ds = ds.groupby('season_year').sum(time_dimname)

# # Limit dataset to complete [boreal winter] seasons
# complete_index = ds['counter'].values == 4
# ds = ds.sel(season_year=complete_index)
# # Divide by four to get mean value
# ds[varname] = ds[varname] / 4

# # Add lead time
# # [N.B. season_year (added automatically by Iris)
# # defines the year of final month in the season]
# ds['lead_time'] = (('season_year',), ds.season_year.values - int(init_year))
# def _is_yr2to9(year): #, init_year):
#     return (year >= 2) & (year <= 9)
# ds = ds.sel(season_year=_is_yr2to9(ds['lead_time']))
# ds = ds.mean('season_year')
# da = ds[varname].to_iris()
