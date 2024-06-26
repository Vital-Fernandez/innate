import logging

from .io import InnateError
from .interpolation.methods import Interpolator
from .regression.methods import Regressor

_logger = logging.getLogger('Innate')


class Approximator:

    def __init__(self, grid, technique_list, data_cfg=None):

        if technique_list is None:
            _logger.critical(f'The data set "{grid.label}" does not include the approximation to include the "approximation"'
                             f'key in the configurations variable or file')

        # Methodology approaches
        self.interp = Interpolator(grid, technique_list, data_cfg=data_cfg)
        self.reg = Regressor(grid, technique_list, data_cfg=data_cfg)

        return