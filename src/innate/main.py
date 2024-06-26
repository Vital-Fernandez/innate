import logging
import numpy as np
from pathlib import Path
from .io import InnateError, load_dataset
from .approximation import Approximator

_logger = logging.getLogger('Innate')

def reconstruct_axes_range(data_label, axes, data_cfg, data_shape):

    axes_range = {}
    for i, dim in enumerate(axes):

        linspace_idcs = data_cfg.get(f'{dim}_range')
        if linspace_idcs is None:
            raise InnateError(
                f'The input grid "{data_label}" configuration does not include a range for the axis "{dim}"')

        axes_range[dim] = np.linspace(linspace_idcs[0], linspace_idcs[1], linspace_idcs[2])

        # Check the sizes are the same
        if axes_range[dim].size != data_shape[i]:
            _logger.warning(f'The parameter "{dim}" input dimensions ({data_shape[i]}) and '
                            f'axes dimensions ({axes_range[dim].size}) are different ')

    return axes_range


class Grid:

    def __init__(self, grid_label, data_array, data_cfg, tensor_library='pytensor'):

        # Class attributes
        self.label = None
        self.description = None
        self.data = None
        self.axes = None
        self.shape = None
        self.axes_range = None

        # Assign attribute values
        self.label = grid_label
        self.description = data_cfg['parameter']
        self.data = data_array
        self.axes = data_cfg['axes']
        self.shape = self.data.shape
        self.axes_range = reconstruct_axes_range(grid_label, self.axes, data_cfg, self.shape)

        # Declare the function attributes treatments
        approx_techniques = data_cfg.get('approximation')
        self.approx = Approximator(self, approx_techniques, data_cfg)

        # # Initiate data and interpolators
        # grid_path = Path(grid)
        # self.grid = load_dataset(grid_path) if grid_path.is_file() else grid

        # if interpolator is not None:

            # print(f'\n- Compiling {interpolator} interpolator')
            #
            # if interpolator == 'pytensor':
            #     self.lib_interpl = interpolator
            #     self.x_range = np.linspace(x_space[0], x_space[1], x_space[2])
            #     self.y_range = np.linspace(y_space[0], y_space[1], y_space[2])
            #     self.interpl = interpolation_selection(self.grid, self.x_range, self.y_range, z_range=None,
            #                                            interp_type='point')
            #     print('-- done')

        return


class DataSet(dict):

    def __init__(self, array_dict, common_cfg, local_cfg, **kwargs):

        # Attributes
        self.data_labels = None
        self.shape_array = None

        # Unpack the individual grids into the class dictionary
        self._compile_grids(array_dict, common_cfg, local_cfg, **kwargs)

        return

    @classmethod
    def from_file(cls, fname, grid_cfg=None):

        # Load and parse the input data
        array_dict, common_cfg, local_cfg = load_dataset(fname)

        # Update the input configuration with the parameters from the user

        return cls(array_dict, common_cfg, local_cfg)

    def _compile_grids(self, array_dict, common_cfg, local_cfg, **kwargs):

        # Extract the keys from the data and configuration containers to create a master list for the Grid set
        common_set = set(array_dict.keys()) & set(common_cfg.keys()) & set(local_cfg.keys())
        self.data_labels = np.array(list(common_set))

        # Loop throught the dataset and create the grids
        for i, data_label in enumerate(self.data_labels):

            # Extract the Grid data
            grid_array = array_dict.get(data_label)
            data_glob_conf = common_cfg.get(data_label)
            data_local_conf = local_cfg.get(data_label)

            # Local entries update the new
            grid_cfg = data_glob_conf if data_local_conf is None else {**data_glob_conf, **data_local_conf}
            self[data_label] = Grid(data_label, grid_array, grid_cfg, **kwargs)

        return

    def extract_approximation(self, technique, label_list=None):

        label_list = label_list if label_list is not None else list(self.keys())

        approx_dict = {}
        for label in label_list:

            if technique in self[label].approx.interp.techniques:
                approx_dict[label] = getattr(self[label].approx.interp, technique)

            elif technique in self[label].approx.reg.techniques:
                approx_dict[label] = getattr(self[label].approx.reg, technique)

            else:
                _logger.critical(f'Input approximation "{technique}" is not available for dataset "{label}"')

        return approx_dict

