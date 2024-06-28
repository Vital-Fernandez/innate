import logging
import numpy as np
from matplotlib import pyplot as plt, rc_context, cm
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

def maximize_center_fig(maximize_check=False, center_check=False):

    if maximize_check:

        # Windows maximize
        mng = plt.get_current_fig_manager()

        try:
            mng.window.showMaximized()
        except:
            try:
                mng.resize(*mng.window.maxsize())
            except:
                _logger.debug(f'Unable to maximize the window')

    if center_check:

        try:
            mngr = plt.get_current_fig_manager()
            mngr.window.setGeometry(1100, 300, mngr.canvas.width(), mngr.canvas.height())
        except:
            _logger.debug(f'Unable to center plot window')

    return


def save_close_fig_swicth(file_path=None, bbox_inches=None, fig_obj=None, maximise=False, plot_check=True):

    # By default, plot on screen unless an output address is provided
    if plot_check:
        output_fig = None

        if file_path is None:

            # Tight layout
            if bbox_inches is not None:
                plt.tight_layout()

            # Window positioning and size
            maximize_center_fig(maximise)

            # Display
            plt.show()

        else:
            plt.savefig(file_path, bbox_inches=bbox_inches)

            # Close the figure in the case of printing
            if fig_obj is not None:
                plt.close(fig_obj)

    # Return the figure for output plotting
    else:
        output_fig = fig_obj

    return output_fig


class Plotter:

    def __init__(self, grid):

        self._grid = grid

        return

    def matrix_diagnostic(self, output_address=None, num_points=15, technique='rgi', in_fig=None, fig_cfg={}, ax_cfg={},
                          maximize=False):

        """
        This function plots the 2D grid array as a surface plot where at even intervals the scatter points color represent
        the absolute divergence between the array data and the selected approximation.

        Parameters
        ----------
        output_address : str, optional
            The file path to save the output figure. If None, the figure will be displayed on the screen.
        num_points : int, optional
            The number of points per axis to test the discrepancy between the grid data and the approximation. Default is 15.
        technique : str, optional
            The interpolation technique to use. Default is 'rgi'.
        in_fig : matplotlib.figure.Figure, optional
            An existing figure to plot on. If None, a new figure will be created.
        fig_cfg : dict, optional
            Configuration dictionary for the figure settings. Default is an empty dictionary.
        ax_cfg : dict, optional
            Configuration dictionary for the axes settings. Default is an empty dictionary.
        maximize : bool, optional
            Whether to maximize the figure window. Default is False.

        Returns
        -------
        in_fig : matplotlib.figure.Figure
            The figure object containing the diagnostic plot.

        Notes
        -----
        This function prepares the data by extracting the grid, parameters, and axes ranges. It computes the test points
        and the discrepancies between the interpolated and actual data values. The results are plotted on a figure,
        highlighting areas with discrepancies below and above 1%.

        Examples
        --------
        >>> fig = obj.matrix_diagnostic(output_address='output.png', num_points=20, technique='rgi')
        >>> plt.show(fig)
        """

        # Prepare the data
        grid = self._grid.data
        params = self._grid.axes
        axes_range = self._grid.axes_range
        y_range = axes_range[params[0]]
        x_range = axes_range[params[1]]

        # Compute test points
        intvl_X, intvl_Y = (x_range.size - 1) / (num_points - 1), (y_range.size - 1) / (num_points - 1)
        idcsX = np.array([int(round(i * intvl_X)) for i in range(num_points)])
        idcsY = np.array([int(round(i * intvl_Y)) for i in range(num_points)])
        X, Y = np.meshgrid(x_range[idcsX], y_range[idcsY])
        idcmeshX, idcsmeshY = np.meshgrid(idcsX, idcsY)

        # Compute discrepancy
        emis_mesh = np.column_stack((y_range[idcsY], x_range[idcsX]))
        emis_interp = self._grid.approx.interp.rgi(emis_mesh).eval()
        emis_data = grid[idcsmeshY, idcmeshX]
        percentage_difference = np.abs(1 - emis_interp / emis_data) * 100

        # Display check for the user figures
        display_check = True if in_fig is None else False

        # Adjust the default theme
        PLT_CONF = theme.fig_defaults(fig_cfg)
        ax_cfg = ax_cfg if ax_cfg is not None else {}

        # Create and fill the figure
        with rc_context(PLT_CONF):

            if in_fig is None:
                in_fig, in_ax = plt.subplots()
            else:
                in_ax = in_fig.add_subplot()

            # Plot plane
            in_ax.imshow(grid, aspect=0.05, extent=(x_range.min(), x_range.max(), y_range.min(), y_range.max()))

            # Plot discrepancy below
            idx_interest = percentage_difference < 5
            in_ax.scatter(X[idx_interest], Y[idx_interest], c="None", edgecolors='black', linewidths=0.35, label='Error below 1%')

            if np.sum(idx_interest == False) > 0:
                scatter_err = in_ax.scatter(X[~idx_interest], Y[~idx_interest], c=percentage_difference[~idx_interest],
                                   edgecolors='black', linewidths=0.1, cmap=cm.OrRd, label='Error above 1%')

                # Color bar
                cbar = in_fig.colorbar(scatter_err)
                cbar.ax.set_ylabel('Discrepancy (%)', rotation=270, labelpad=20)

            in_ax.set_ylabel(f'{params[0]}')
            in_ax.set_xlabel(f'{params[1]}')

            in_ax.legend(loc='upper right', framealpha=1)

            in_ax.update(ax_cfg)

            # By default, plot on screen unless an output address is provided
            in_fig = save_close_fig_swicth(output_address, 'tight', in_fig, maximize, display_check)

        return in_fig


        # # Generate fitted surface points
        # matrix_edge = int(np.sqrt(te_ne_grid[0].shape[0]))
        # surface_points = func_emis(te_ne_grid, *coeffs)
        #
        # # Compare pyneb values with values from fitting
        # percentage_difference = (1 - surface_points / emis_grid) * 100
        #
        # ion, wave, latex_label = lime.label_decomposition(line_label, scalar_output=True)
        #
        # # Generate figure
        # fig = plt.figure()
        # ax = fig.add_subplot(111)


        # # Plot plane
        # ax.imshow(surface_points.reshape((matrix_edge, matrix_edge)),
        #           aspect=0.03,
        #           extent=(te_ne_grid[1].min(), te_ne_grid[1].max(), te_ne_grid[0].min(), te_ne_grid[0].max()))
        #

        # # Plot plane
        # ax.imshow(surface_points.reshape((matrix_edge, matrix_edge)),
        #           aspect=0.03,
        #           extent=(te_ne_grid[1].min(), te_ne_grid[1].max(), te_ne_grid[0].min(), te_ne_grid[0].max()))
        #
        # # Points with error below 1.0 are transparent:
        # idx_interest = percentage_difference < 0.5
        # ax.scatter(te_ne_grid[1][idx_interest], te_ne_grid[0][idx_interest], c="None", edgecolors='black',
        #            linewidths=0.35, label='Error below 1%')
        #
        # if idx_interest.sum() < emis_grid.size:
        #     # Plot grid points
        #     sc_im = ax.scatter(te_ne_grid[1][~idx_interest], te_ne_grid[0][~idx_interest],
        #                        c=percentage_difference[~idx_interest],
        #                        edgecolors='black', linewidths=0.1, cmap=cm.OrRd, label='Error above 1%')
        #
        #     # Color bar
        #     cbar = fig.colorbar(sc_im)
        #     cbar.ax.set_ylabel('Discrepancy (%)', rotation=270, labelpad=20)
        #
        # # Add labels
        # ax.set_ylabel('Temperature $(K)$', fontsize=15)
        # ax.set_xlabel('Density ($cm^{-3}$)', fontsize=15)
        # title_label = f'{latex_label}, emissivity grid\n versus parametrisation'
        # title_label = f''
        # ax.set_title(title_label, fontsize=15)
        #
        # ax.set_ylim(te_ne_grid[0].min(), te_ne_grid[0].max())
        # ax.set_xlim(te_ne_grid[1].min(), te_ne_grid[1].max())
        #
        # # Display the plot
        # ax.legend(loc='lower right', framealpha=1)
        #
        # if output_address is None:
        #     plt.show()
        # else:
        #     plt.savefig(output_address, bbox_inches='tight')





        return