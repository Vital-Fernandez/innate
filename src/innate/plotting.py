import logging
import numpy as np
from matplotlib import pyplot as plt, rc_context
from . import _setup_cfg

_logger = logging.getLogger('Innate')


class Themer:

    def __init__(self, conf, style='default', library='matplotlib'):

        # Attributes
        self.conf = None
        self.style = None
        self.base_conf = None
        self.colors = None
        self.library = None

        # Assign default
        self.conf = conf.copy()
        self.library = library
        self.set_style(style)

        return

    def fig_defaults(self, user_fig=None, fig_type=None):

        # Get plot configuration
        if fig_type is None:
            fig_conf = self.base_conf.copy()
        else:
            fig_conf = {** self.base_conf, **self.conf[self.library][fig_type]}

        # Get user configuration
        fig_conf = fig_conf if user_fig is None else {**fig_conf, **user_fig}

        return fig_conf

    def ax_defaults(self, user_ax, x_units, y_units, norm_flux, fig_type='default', **kwargs):

        # Default wavelength and flux
        if fig_type == 'plane':

            # Spectrum labels x-wavelegth, y-flux # TODO without units
            ax_cfg = {'xlabel': f'{x_units:s}', 'ylabel': f'{y_units:s}'}

            # Update with the user configuration
            ax_cfg = ax_cfg if user_ax is None else {**ax_cfg, **user_ax}

        # Spatial cubes
        elif fig_type == 'cube':

            ax_cfg = {} if user_ax is None else user_ax.copy()

            # Define the title
            if ax_cfg.get('title') is None:

                title = r'{} band'.format(kwargs['line_bg'].latex_label[0])

                line_fg = kwargs.get('line_fg')
                if line_fg is not None:
                    title = f'{title} with {line_fg.latex_label[0]} contours'

                if len(kwargs['masks_dict']) > 0:
                    title += f'\n and spatial masks at foreground'

                ax_cfg['title'] = title

            # Define x axis
            if ax_cfg.get('xlabel') is None:
                ax_cfg['xlabel'] = 'x' if kwargs['wcs'] is None else 'RA'

            # Define y axis
            if ax_cfg.get('ylabel') is None:
                ax_cfg['ylabel'] = 'y' if kwargs['wcs'] is None else 'DEC'

            # Update with the user configuration
            ax_cfg = ax_cfg if user_ax is None else {**ax_cfg, **user_ax}

        # No labels
        else:
            ax_cfg = {}

            # Update with the user configuration
            ax_cfg = ax_cfg if user_ax is None else {**ax_cfg, **user_ax}

        return ax_cfg

    def set_style(self, style=None, fig_cfg=None, colors_conf=None):

        # Set the new style
        if style is not None:
            self.style = np.atleast_1d(style)
        else:
            self.style = np.atleast_1d('default')

        # Generate the default
        self.base_conf = self.conf[self.library]['default'].copy()
        for style in self.style:
            self.base_conf = {**self.base_conf, **self.conf[self.library][style]}

        # Add the new configuration
        if fig_cfg is not None:
            self.base_conf = {**self.base_conf, **fig_cfg}

        # Set the colors
        for i_style in self.style:
            if i_style in self.conf['colors']:
                self.colors = self.conf['colors'][style].copy()

        # Add the new colors
        if colors_conf is not None:
            self.colors = {**self.colors, **colors_conf}

        if self.colors is None:
            _logger.warning(f'The input style {self.style} does not have a LiMe color database')

        return


# LiMe figure labels and color formatter
theme = Themer(_setup_cfg)

