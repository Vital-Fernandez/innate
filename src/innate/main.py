import logging
import numpy as np
from pathlib import Path
from .io import InnateError, load_dataset
from .approximation import Approximator
from .plotting import Plotter

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

    """

    A class used to represent an innate Grid, which consits in a (numpy) data array and a set of configuration entries.

    In the case of interpolation techniques the user can specify the tensor library, which is used to compile the approximations.

    Parameters
    ----------
    grid_label : str
       The label for the grid.
    data_array : array-like
       The data array.
    data_cfg : dict
       Configuration dictionary for the data, containing the array dimensions information.
    tensor_library : str, optional
       The tensor library to use (default is 'pytensor').

    Attributes
    ----------
    label : str
       The label for the grid.
    description : str
       Description of the data parameter.
    data : array-like
       The data array.
    axes : list
       List of axes for the data.
    shape : tuple
       Shape of the data array.
    axes_range : list
       Range of the axes for the data.
    approx : Approximator
       An approximator instance for handling data approximations.
    plot : Plotter
       A plotter instance for visualizing the data.

    Methods
    -------
    reconstruct_axes_range(grid_label, axes, data_cfg, shape)
       Reconstructs the range of axes for the grid.

    """

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

        # Plotting function
        self.plot = Plotter(self)

        return


class DataSet(dict):

    """

    A class used to represent a Dataset, inheriting from Python's built-in dictionary.

    This class is initialized with data arrays and configuration parameters,
    and it unpacks these into the class dictionary.

    Parameters
    ----------
    array_dict : dict
        Dictionary containing data arrays.
    common_cfg : dict
        Dictionary containing common configuration parameters.
    local_cfg : dict
        Dictionary containing local configuration parameters.

    Attributes
    ----------
    data_labels : None or list
        Placeholder for data labels. Initialized as None.
    shape_array : None or tuple
        Placeholder for the shape of the data arrays. Initialized as None.


    """

    def __init__(self, array_dict, common_cfg, local_cfg, **kwargs):



        # Attributes
        self.data_labels = None
        self.shape_array = None

        # Unpack the individual grids into the class dictionary
        self._compile_grids(array_dict, common_cfg, local_cfg, **kwargs)

        return

    @classmethod
    def from_file(cls, fname, grid_cfg=None):

        """
        Creates a DataSet dictionarly-like object from an input file address.

        Parameters
        ----------
        fname : str
            The file address or path of the file containing the dataset.
        grid_cfg : dict, optional
            Configuration parameters for the dataset provided by the user. These values will overwrite common entries on
             the fiel configuration parameter. Default is None.

        Returns
        -------
        DataSet
            A DataSet dictionarly-like object containing the scientific arrays, the data configuration and the
            approximation techniques.

        Notes
        -----
        This method loads and parses the input data from the specified file.
        It updates the input configuration with the parameters provided by the user.

        Examples
        --------
        >>> scientific_data = DataSet.from_file('data/file.txt', grid_cfg={'param': 'value'})
        """

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

