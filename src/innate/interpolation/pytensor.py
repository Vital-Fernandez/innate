import itertools
import logging
from ..io import InnateError

_logger = logging.getLogger('Innate')


try:
    import pytensor.tensor as tt
    pytensor_check = True
except ImportError:
    pytensor_check = False


def as_tensor_variable(x, dtype="float64", **kwargs):
    t = tt.as_tensor_variable(x, **kwargs)
    if dtype is None:
        return t
    return t.astype(dtype)


def interpolation_selection(grid_dict, x_range, y_range, z_range=None, interp_type='point'):

    # Container for interpolators
    interp_dict = {}

    for line, data_grid in grid_dict.items():

        # 2D Point interpolation
        if interp_type == 'point':
            interp_i = RegularGridInterpolator([x_range, y_range], data_grid[:, :, None], nout=1)

        # Line interpolation
        elif interp_type == 'axis':
            data_grid_reshape = data_grid.reshape((x_range.size, y_range.size, -1))
            interp_i = RegularGridInterpolator([x_range, y_range], data_grid_reshape)

        # 3D point
        elif interp_type == 'cube':
            interp_i = RegularGridInterpolator([x_range, y_range, z_range], data_grid)

        # Evaluate and store it
        interp_dict[line] = interp_i.evaluate

    return interp_dict


def interpolation_coordinates(data_grid, axes_range_list, z_range=None, interp_type='point'):

    # 2D Point interpolation
    if interp_type == 'point':
        interp_i = RegularGridInterpolator(axes_range_list, data_grid[:, :, None], nout=1)

    # Line interpolation
    elif interp_type == 'axis':
        data_grid_reshape = data_grid.reshape((axes_range_list[0].size, axes_range_list[1].size, -1))
        interp_i = RegularGridInterpolator(axes_range_list, data_grid_reshape)

    # 3D point
    elif interp_type == 'cube':
        interp_i = RegularGridInterpolator(axes_range_list, data_grid)

    else:
        raise InnateError(f'The interpolation type ({interp_type}) is not recognized,'
                          f' please use "point", "axis" or "cube"')

    return interp_i.evaluate


def regular_grid_interp(points, values, coords, *, fill_value=None):

    """
    Linear interpolation on a regular grid in arbitrary dimensions.

    The data must be defined on a filled regular grid, but the spacing may be
    uneven in any of the dimensions.

    Parameters
    ----------
    points : list of array-like
        A list of vectors with shapes ``(m1,), ... (mn,)``. These define the grid points in each dimension.
    values : array-like
        A tensor defining the values at each point in the grid defined by ``points``. This must have the shape ``(m1, ... mn, ..., nout)``.

    Returns
    -------
    result : array-like
        Interpolated values at the requested points.

    """

    points = [as_tensor_variable(p) for p in points]
    ndim = len(points)
    values = as_tensor_variable(values)
    coords = as_tensor_variable(coords)

    # Find where the points should be inserted
    indices = []
    norm_distances = []
    out_of_bounds = tt.zeros(coords.shape[:-1], dtype=bool)
    for n, grid in enumerate(points):
        x = coords[..., n]
        i = tt.extra_ops.searchsorted(grid, x) - 1
        out_of_bounds |= (i < 0) | (i >= grid.shape[0] - 1)
        i = tt.clip(i, 0, grid.shape[0] - 2)
        indices.append(i)
        norm_distances.append((x - grid[i]) / (grid[i + 1] - grid[i]))

    result = tt.zeros(tuple(coords.shape[:-1]) + tuple(values.shape[ndim:]))
    for edge_indices in itertools.product(*((i, i + 1) for i in indices)):
        weight = tt.ones(coords.shape[:-1])
        for ei, i, yi in zip(edge_indices, indices, norm_distances):
            weight *= tt.where(tt.eq(ei, i), 1 - yi, yi)
        result += values[edge_indices] * weight

    if fill_value is not None:
        result = tt.switch(out_of_bounds, fill_value, result)

    return result


class RegularGridInterpolator:

    """

    Linear interpolation on a regular grid in arbitrary dimensions.

    The data must be defined on a filled regular grid, but the spacing may be
    uneven in any of the dimensions.

    Parameters
    ----------
    points : list of array-like
        A list of vectors with shapes ``(m1,), ... (mn,)``. These define the grid points in each dimension.
    values : array-like
        A tensor defining the values at each point in the grid defined by ``points``. This must have the shape ``(m1, ... mn, ..., nout)``.

    Returns
    -------
    result : array-like
        Interpolated values at the requested points.

    """

    def __init__(self, points, values, fill_value=None, **kwargs):

        # Check pytensor has been installed
        if pytensor_check:
            self.ndim = len(points)
            self.points = points
            self.values = values
            self.fill_value = fill_value

        else:
            _logger.critical(f'PyTensor is not installed, this interpolation cannot be applied.')
            raise InnateError(f'Need to install PyTensor to use this function')

    def evaluate(self, t):
        """Interpolate the data

        Args:
            t: A matrix defining the coordinates where the interpolation
                should be evaluated. This must have the shape
                ``(ntest, ndim)``.
        """
        return regular_grid_interp(self.points, self.values, t, fill_value=self.fill_value)