import numpy as np
from pathlib import Path
from .io import load_dataset
from .interpolation.pytensor import interpolation_selection


class Innate:

    def __init__(self, grid=None, x_space=None, y_space=None, interpolator='pytensor'):

        # Object attributes
        self.grid = None
        self.interpl = None
        self.lib_interpl = None
        self.x_range, self.y_range = None, None

        # Initiate data and interpolators
        grid_path = Path(grid)
        self.grid = load_dataset(grid_path) if grid_path.is_file() else grid

        if interpolator is not None:

            print(f'\n- Compiling {interpolator} interpolator')

            if interpolator == 'pytensor':
                self.lib_interpl = interpolator
                self.x_range = np.linspace(x_space[0], x_space[1], x_space[2])
                self.y_range = np.linspace(y_space[0], y_space[1], y_space[2])
                self.interpl = interpolation_selection(self.grid, self.x_range, self.y_range, z_range=None,
                                                       interp_type='point')
                print('-- done')

        return
