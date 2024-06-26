import logging

from .pytensor import interpolation_coordinates
from .. import _setup_cfg

_logger = logging.getLogger('Innate')


class Interpolator:

    def __init__(self, grid, technique_list, tensor_library='pytensor', data_cfg=None):

        # Attributes
        self.rgi = None
        self.techniques = []

        # Confirm the data is available
        if grid.data is None:
            _logger.warning(f'The data set "{grid.label}" does not include a grid interpolation techniques cannot be used')

        # Constrain to
        algorithms = list(set(_setup_cfg['parameter_labels']['interp'].keys()) & set(technique_list))

        # Regular grid Interpolation
        if 'rgi' in algorithms:
            self.techniques.append('rgi')
            self.rgi = interpolation_coordinates(grid.data, list(grid.axes_range.values()), interp_type='point')

        return
