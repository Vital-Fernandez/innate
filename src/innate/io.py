import logging
from pathlib import Path
from . import _setup_cfg

_logger = logging.getLogger('Innate')

REF_entry = _setup_cfg['parameter_labels']['param']

try:
    from astropy.io import fits
    astropy_check = True
except ImportError:
    astropy_check = False

try:
    import h5netcdf
    h5netcdf_check = True
except ImportError:
    h5netcdf_check = False


# Define library error function
class InnateError(Exception):
    """InnateError exception function"""


def load_dataset(fname: str):

    # Check the file location
    fname = Path(fname)
    ext = fname.suffix

    if not fname.is_file():
        raise InnateError(f'Not dataset file found at {fname}')

    # Run the appropriate file saving workflow
    match ext:

        case '.fits':
            return fits_file_load(fname)

        case '.nc':
            return h5netcdf_file_load(fname)

        case _:
            return KeyError(f'The extension "{ext}" is not recognized, please use ".nc" or ".fits"')


def save_dataset(fname: str, grid_dict: dict, common_cfg: dict, custom_cfg: dict):

    """

    :param fname:
    :type str or Pathlib: path.Pathlib

    :param cfg_dict:

    :param grid_dict:

    """

    # Check the file location
    fname = Path(fname)
    ext = fname.suffix

    # Check there is input data
    if len(grid_dict) == 0:
        raise InnateError(f'Output data grid does not contain any entry')

    # Run the appropriate file saving workflow
    match ext:

        case '.fits':
            return fits_file_save(fname, grid_dict, common_cfg, custom_cfg)

        case '.nc':
            return h5netcdf_file_save(fname, grid_dict, common_cfg, custom_cfg)

        case _:
            return KeyError(f'The extension "{ext}" is not recognized, please use ".nc" or ".fits"')


def fits_file_save(fname: str, grid_dict: dict, common_cfg: dict, custom_cfg: dict):

    if astropy_check:

        # Create a primary HDU
        hdu_list = fits.HDUList([fits.PrimaryHDU()])

        # Generate the fits file
        for key, grid in grid_dict.items():
            hdu_i = fits.ImageHDU(grid, name=key)
            hdu_list.append(hdu_i)

        # Write the fits file
        hdu_list.writeto(fname, overwrite=True)

    else:
        raise InnateError(f'To open ".fits" files (astropy.io.fits) you need to install the astropy package')

    return


def fits_file_load(fname: str):

    grid_dict, cfg_dict = {}, {}

    if astropy_check:
        with fits.open(fname) as hdu_list:
            for i in range(1, len(hdu_list)):
                grid_dict[hdu_list[i].name] = hdu_list[i].data
    else:
        raise InnateError(f'To open ".fits" files (astropy.io.fits) you need to install the astropy package')

    return grid_dict, cfg_dict


def h5netcdf_file_save(fname: str, grid_dict: dict, common_cfg: dict, custom_cfg: dict):

    if h5netcdf_check:

        # Use the first item for the dimensions # TODO this might cause issues if grids have different size
        grid_0 = grid_dict[list(grid_dict.keys())[0]]
        data_shape = grid_0.shape

        if len(data_shape) != len(common_cfg['axes']):
            raise InnateError(f'Data set shape ({data_shape}) size is different from configuration axes'
                              f' ({common_cfg["axes"]}) size')

        with h5netcdf.File(fname, 'w') as f:

            # Unique dimensions for all the datase
            for i, axis in enumerate(common_cfg['axes']):
                f.dimensions[axis] = data_shape[i]

            # Iterate over the data grids
            for grid_name, grid in grid_dict.items():
                var = f.create_variable(grid_name, common_cfg['axes'], data=grid)
                var.attrs[REF_entry] = str(grid_name)

                # Common grid entries
                if common_cfg is not None:
                    for key, value in common_cfg.items():
                        var.attrs[key] = value

                # Local entries
                if custom_cfg is not None:
                    local_cfg = custom_cfg.get(grid_name)
                    if local_cfg is not None:
                        for key, value in local_cfg.items():
                            var.attrs[f'{grid_name}_{key}'] = value

    else:
        raise InnateError(f'To open ".nc" (h5netcdf) files you need to install the h5netcdf package')

    return


def h5netcdf_file_load(fname: str):

    grid_dict, common_cfg, local_cfg = {}, {}, {}

    if h5netcdf_check:
        with h5netcdf.File(fname, 'r') as f:

            # Loop through the grid
            for var_name in f.variables:

                # Unpack the library container
                var = f.variables[var_name]

                # Scientific data
                grid_dict[var_name] = var[...]

                # Unpack the configuration parameters
                common_cfg[var_name], local_cfg[var_name] = {}, {}
                for attr in var.attrs:

                    # Global conf
                    if not attr.startswith(var_name):
                        common_cfg[var_name][attr] = var.attrs[attr]

                    # Local conf
                    else:
                        local_cfg[var_name][attr[len(var_name)+1:]] = var.attrs[attr]

                # Convert to None if empty configuration
                if len(grid_dict[var_name]) == 0:
                    grid_dict[var_name] = None

                if len(common_cfg[var_name]) == 0:
                    common_cfg[var_name] = None

                if len(local_cfg[var_name]) == 0:
                    local_cfg[var_name] = None

    else:
        raise InnateError(f'To open ".nc" (h5netcdf) files you need to install the h5netcdf package')

    # Parse the file
    return grid_dict, common_cfg, local_cfg



