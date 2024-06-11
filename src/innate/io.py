from pathlib import Path

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


def load_dataset(fname):

    # Container
    grid_dict = None

    # Check there is an input grid file
    if fname is not None:

        # Locate the file
        if fname.is_file():

            # Container for output grid
            grid_dict = {}

            ext = fname.suffix
            print(f'\n- Loading emissivity grid at {fname}')
            if ext == '.fits':

                if astropy_check:
                    with fits.open(fname) as hdu_list:
                        for i in range(1, len(hdu_list)):
                            grid_dict[hdu_list[i].name] = hdu_list[i].data
                else:
                    raise InnateError(f'To open {ext} (astropy.io.fits) files you need to install the astropy package')

            elif ext == '.nc':

                if h5netcdf_check:
                    with h5netcdf.File(fname, 'r') as f:
                        for var_name in f.variables:
                            grid_dict[var_name] = f.variables[var_name][...]
                else:
                    raise InnateError(f'To open {ext} (h5netcdf) files you need to install the h5netcdf package')

    return grid_dict


def save_dataset(fname, grid_dict):

    fname = Path(fname)
    ext = fname.suffix

    # Case of a .fits astropy file:
    if fname.suffix == '.fits':

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
            raise InnateError(f'To open {ext} (astropy.io.fits) files you need to install the astropy package')

    # Case of a .fits astropy file:
    elif ext == '.nc':

        if h5netcdf_check:

            # Use the first item for the dimensions
            grid_0 = grid_dict[list(grid_dict.keys())[0]]
            m, n = grid_0.shape

            with h5netcdf.File(fname, 'w') as f:

                # Unique dimensions for all the datase
                f.dimensions['m'], f.dimensions['n'] = m, n

                # Iterate over the dictionary and create a variable for each array
                for key, grid in grid_dict.items():
                    var = f.create_variable(key, ('m', 'n'), data=grid)
                    var.attrs['description'] = f'{key} emissivity'

        else:
            raise InnateError(f'To open {ext} (h5netcdf) files you need to install the h5netcdf package')

    else:
        raise KeyError(f'The extension "{ext}" is not recognized, please use ".nc" or ".fits"')

    return
