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
    """
        Load the data grids and configuration from a digital file.

        Parameters
        ----------
        fname : str
            The file address or path of the file.

        Returns
        -------

        A dictionary with the data arrays, a dictionary with the global grids configuration and a dictionary with the local grid configuration.
            - For '.fits' files: (array_dict, common_cfg, local_cfg)
            - For '.nc' files: (array_dict, common_cfg, local_cfg)

        Raises
        ------
        InnateError
            If no dataset file is found at the specified location.
        KeyError
            If the file extension is not recognized.

        Notes
        -----
        This function checks the file extension and loads the dataset using the appropriate method:
        - '.fits' files are loaded using `fits_file_load`.
        - '.nc' files are loaded using `h5netcdf_file_load`.

        Examples
        --------
        >>> data = load_dataset('data/file.fits')
        >>> data = load_dataset('data/file.nc')
        """

    # Check the file location
    if type(fname).__name__ != 'UploadedFile':
        log_path = Path(fname)
        if not log_path.is_file():
            raise InnateError(f'Not dataset file found at {fname}')

        fname, ext = log_path, log_path.suffix

    else:
        fname, ext = fname, 'UploadedFile'

    # Run the appropriate file saving workflow
    match ext:

        case '.fits':
            return fits_file_load(fname)

        case '.nc':
            return h5netcdf_file_load(fname)

        case 'UploadedFile':
            return h5netcdf_file_load(fname)

        case _:
            return KeyError(f'The extension "{ext}" is not recognized, please use ".nc" or ".fits"')


def save_dataset(fname: str, grid_dict: dict, common_cfg: dict, custom_cfg: dict):

    """
    Save the data grids and configuration to a digital file.

    Parameters
    ----------
    fname : str or pathlib.Path
        The name of the file where the dataset will be saved.
    grid_dict : dict
        Dictionary containing the data grid to be saved.
    common_cfg : dict
        Dictionary containing common configuration parameters.
    custom_cfg : dict
        Dictionary containing custom configuration parameters.

    Returns
    -------
    None

    Raises
    ------
    KeyError
        If the file extension is not recognized.

    Notes
    -----
    This function checks the file extension and saves the dataset using the appropriate method:
    - '.fits' files are saved using `fits_file_save`.
    - '.nc' files are saved using `h5netcdf_file_save`.

    Examples
    --------
    >>> save_dataset('data/output.fits', grid_dict, common_cfg, custom_cfg)
    >>> save_dataset('data/output.nc', grid_dict, common_cfg, custom_cfg)
    """

    # Check the file location
    fname = Path(fname)
    ext = fname.suffix

    # Check there is input data
    if len(grid_dict) == 0:
        _logger.warning(f'Output dataset does not contain any grid entry')

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



