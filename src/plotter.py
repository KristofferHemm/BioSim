from pathlib import Path
from typing import Union, List

import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from biosim.island import Island


class Plotter:
    """
    Plotter module for plotting and displaying the simulation figures.
    Plots the following data:

        * Island Map
        * Population chart
        * Population distribution heatmap
        * Histogram for population fitness, weight and age
    """

    def __init__(self,
                 island: Island,
                 heatmap_vmax: dict = None,
                 y_max: Union[int, float] = None,
                 hist_specs: dict = None,
                 img_dir: str = None,
                 img_base: str = None,
                 img_fmt: str = None
                 ):
        """
        :param island: Island object to be plotted
        :param heatmap_vmax: vmax values for the heatmap figures
        :param y_max: y-axis limit for population chart
        :param hist_specs: Specifications for the histograms
        :param img_dir: Save directory for the images
        :param img_base: Image base filename
        :param img_fmt: Image format. E.g. "png" or "jpg"
        """
        self.island = island
        self.population_graph_y_max = y_max
        self.hist_specs = hist_specs
        self.img_dir = img_dir
        self.img_base = img_base
        self.img_fmt = img_fmt
        self.img_num = 0

        self.fig = plt.figure(figsize=(12, 8))

        # Main Grid of size 3X1
        gs0 = self.fig.add_gridspec(3, 1)

        # Define size of each subgrid
        gs00 = gs0[0].subgridspec(1, 3)
        gs01 = gs0[1].subgridspec(1, 3)
        gs02 = gs0[2].subgridspec(1, 3)

        self.ax11 = self.fig.add_subplot(gs00[0, 0])  # Island Map
        self.ax_text = self.fig.add_subplot(gs00[0, 1])  # Year Text
        self.ax13 = self.fig.add_subplot(gs00[0, 2])  # Population chart
        self.ax21 = self.fig.add_subplot(gs01[0, 0])  # Herbivore Heatmap
        self.ax22 = self.fig.add_subplot(gs01[0, 1])  # Carnivore Heatmap
        self.ax23 = self.fig.add_subplot(gs01[0, 2])  # Legend Plot
        self.ax31 = self.fig.add_subplot(gs02[0, 0])  # Fitness Histogram
        self.ax32 = self.fig.add_subplot(gs02[0, 1])  # Age Histogram
        self.ax33 = self.fig.add_subplot(gs02[0, 2])  # Weight Histogram

        # Set the aspect ratio of the heatmaps
        self.ax21.set_aspect('equal')
        self.ax22.set_aspect('equal')

        self.line1 = None
        self.line2 = None
        self.line3 = None
        self.line1_text = None
        self.line2_text = None
        self.line3_text = None

        self.text = "Year: {year:03}\n" \
                    "Population: {population:03}\n" \
                    "Herbivores: {herbivores:03}\n" \
                    "Carnivores: {carnivores:03}"
        self.text_obj = None
        self.herbivore_heatmap_vmax = heatmap_vmax['Herbivore'] if heatmap_vmax else 200
        self.carnivore_heatmap_vmax = heatmap_vmax['Carnivore'] if heatmap_vmax else 50
        self._create_figures()

    def _create_figures(self):
        """
        Initialize all the figures
        """
        self._create_map()
        self._create_population_graph()
        self._create_year_text()
        self._create_heatmap(self.ax21,
                             self.island.get_current_herbivore_population_state(),
                             self.herbivore_heatmap_vmax,
                             "Herbivore Heatmap")
        self._create_heatmap(self.ax22,
                             self.island.get_current_carnivore_population_state(),
                             self.carnivore_heatmap_vmax,
                             "Carnivore Heatmap")
        self._create_legend()
        self._create_histogram(self.ax31,
                               self.island.get_current_herbivore_fitness(),
                               self.island.get_current_carnivore_fitness(),
                               "Fitness")
        self._create_histogram(self.ax32,
                               self.island.get_current_herbivore_age(),
                               self.island.get_current_carnivore_age(),
                               "Age")
        self._create_histogram(self.ax33,
                               self.island.get_current_herbivore_weight(),
                               self.island.get_current_carnivore_weight(),
                               "Weight")

        plt.tight_layout()

    def update_figures(self, history: List):
        """Update all the figures

        :param history: The simulation history with the yearly population data
        """
        self._update_population_graph(history)

        self._update_year_text(history[-1]['year'],
                               history[-1]['population'],
                               history[-1]['herbivores'],
                               history[-1]['carnivores'])
        self._update_heatmap(self.ax21,
                             self.island.get_current_herbivore_population_state())
        self._update_heatmap(self.ax22,
                             self.island.get_current_carnivore_population_state())

        self._update_histogram(self.ax31,
                               self.island.get_current_herbivore_fitness(),
                               self.island.get_current_carnivore_fitness(),
                               "Fitness")
        self._update_histogram(self.ax32,
                               self.island.get_current_herbivore_age(),
                               self.island.get_current_carnivore_age(),
                               "Age")
        self._update_histogram(self.ax33,
                               self.island.get_current_herbivore_weight(),
                               self.island.get_current_carnivore_weight(),
                               "Weight")
        plt.pause(0.1)

    def save_fig(self, year):
        """
        Saves the figure to a file.

        """
        filename = Path(self.img_dir)/Path(self.img_base + f"_{year:05}." + self.img_fmt)
        self.fig.savefig(filename)

    def _create_map(self):
        """
        Create the island map plot
        """
        index_map = {'W': 0,
                     'L': 1,
                     'H': 2,
                     'D': 3}
        legend_map = {0: "Water",
                      1: "Lowland",
                      2: "Highland",
                      3: "Desert"}

        map_index = [[index_map[column] for column in row]
                     for row in self.island.geography.splitlines()]

        colormap = ListedColormap([[0.2, 0.6, 1.0],
                                   [0.0, 0.6, 0.0],
                                   [0.5, 1.0, 0.5],
                                   [1.0, 1.0, 0.5]])

        values = np.unique(np.array(map_index).ravel())

        self.ax11.set_title("Island Map")
        im = self.ax11.imshow(map_index, cmap=colormap, interpolation='none', vmax=colormap.N)
        shape = np.array(map_index).shape

        self.ax11.set_xticks([0, shape[1] - 1])
        self.ax11.set_xticklabels([1, shape[1]])
        self.ax11.set_yticks([0, shape[0] - 1])
        self.ax11.set_yticklabels([1, shape[0]])

        # get the colors of the values, according to the
        # colormap used by imshow
        colors = [im.cmap(im.norm(value)) for value in values]
        # create a patch (proxy artist) for every color
        patches = [mpatches.Patch(facecolor=colors[i],
                                  edgecolor='black',
                                  label=legend_map[values[i]])
                   for i in range(len(values))]
        # put those patched as legend-handles into the legend
        self.ax11.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2)

    def _create_year_text(self):
        """
        Create the center text cell that displays the year and the population
        """
        self.ax_text.axis('off')
        self.text_obj = self.ax_text.text(0.7, 0.5, self.text.format(year=0,
                                                                     population=0,
                                                                     herbivores=0,
                                                                     carnivores=0),
                                          horizontalalignment='right',
                                          verticalalignment='center',
                                          transform=self.ax_text.transAxes)

    def _update_year_text(self, year, population, herbivores, carnivores):
        """
        Update the center text
        """
        self.text_obj.set_text(self.text.format(year=year,
                                                population=population,
                                                herbivores=herbivores,
                                                carnivores=carnivores))

    def _set_population_graph_ylim(self):
        if self.population_graph_y_max:
            self.ax13.set_ylim([0, self.population_graph_y_max])

    def _create_population_graph(self):
        """
        Create the population graph
        """
        self.ax13.set_title("Population chart")
        self.ax13.set_ylabel("Population")
        self.ax13.set_xlabel("Years")

        total_population = self.island.num_animals
        herbivore_population = self.island.num_animals_per_species['Herbivore']
        carnivore_population = self.island.num_animals_per_species['Carnivore']
        # Line chart for the population numbers
        self.line1 = self.ax13.plot([1],
                                    [total_population],
                                    color="green",
                                    label='population')[0]
        # Text to the right of the figure showing the population numbers.
        self.line1_text = self.ax13.annotate(total_population,
                                             xy=(1, 0),
                                             xytext=(8, 0),
                                             xycoords=('axes fraction', 'data'),
                                             textcoords='offset points',
                                             color="green",
                                             size=8)

        self.line2 = self.ax13.plot([1],
                                    [herbivore_population],
                                    color="blue",
                                    label='herbivores')[0]
        self.line2_text = self.ax13.annotate(herbivore_population,
                                             xy=(1, 0),
                                             xytext=(8, 0),
                                             xycoords=('axes fraction', 'data'),
                                             textcoords='offset points',
                                             color="blue",
                                             size=8)

        self.line3 = self.ax13.plot([1],
                                    [carnivore_population],
                                    color="red",
                                    label='carnivores')[0]
        self.line3_text = self.ax13.annotate(carnivore_population,
                                             xy=(1, 0),
                                             xytext=(8, 0),
                                             xycoords=('axes fraction', 'data'),
                                             textcoords='offset points',
                                             color="red",
                                             size=8)
        self._set_population_graph_ylim()

    def _update_population_graph(self, history):
        """
        Update the population graph
        :param history: history of the population growth
        """
        years = [x['year'] for x in history]
        population = [x['population'] for x in history]
        herbivores = [x['herbivores'] for x in history]
        carnivores = [x['carnivores'] for x in history]

        self.line1.set_ydata(population)
        self.line2.set_ydata(herbivores)
        self.line3.set_ydata(carnivores)

        self.line1.set_xdata(years)
        self.line2.set_xdata(years)
        self.line3.set_xdata(years)

        self.line1_text.xy = (1, population[-1])
        self.line1_text.set_text(population[-1])

        self.line2_text.xy = (1, herbivores[-1])
        self.line2_text.set_text(herbivores[-1])

        self.line3_text.xy = (1, carnivores[-1])
        self.line3_text.set_text(carnivores[-1])

        self.ax13.relim()
        self.ax13.autoscale()
        self._set_population_graph_ylim()

    def _create_heatmap(self, axes, data: np.ndarray, vmax: int, title):
        """
        Create a heatmap figure using imshow
        :param axes: the axes where we want the figure
        :param data: the data to be displayed.
        :param vmax: the maximum value of the colormap
        :param title: the title the figure
        """
        axes.axis('off')
        axes.set_title(title)
        heatmap = axes.imshow(data,
                              cmap='plasma',
                              rasterized=True,
                              vmin=0,
                              vmax=vmax)
        self.fig.colorbar(heatmap, ax=axes)

    @staticmethod
    def _update_heatmap(axes, data):
        """
        Update the heatmap data
        :param axes: Axes of the heatmap
        :param data: New data to display
        """
        # The heatmap object is the first child of the axes
        heatmap = axes.get_children()[0]
        heatmap.set_array(data)

    @staticmethod
    def _get_hist_values(data: List, max_value: Union[int, float], bin_width: Union[int, float]):
        """
        Returns the values of the histogram
        :param data: The data to create the histogram of
        :param max_value: The max value to be present on the histogram
        :param bin_width: The bin width of the histogram
        :return: The values of the histogram
        """
        # If there is no data, return ([0],[0]) as the histogram values.
        if not data:
            return [0], [0]
        # Convert data to numpy array for faster max_value filtering
        data = np.array([data])
        # Filter out values larger than max_value if given
        if max_value:
            data = data[data < max_value]
            # If there is no data left, return ([0],[0]) as the histogram values.
            if len(data) == 0:
                return [0], [0]
        # Calculate the number of bins
        bins = np.arange(min(data), max(data) + bin_width, bin_width) if bin_width else 20
        # Create the histogram
        hist_data = np.histogram(data, bins=bins)
        # Return the X values and Y values for the histogram plot.
        # Remove the last edge from the X values to have equal length with Y values.
        return hist_data[1][:-1], hist_data[0]

    def _get_hist_specs(self, prop: str):
        """
        Return the maximum histogram value and the bin width from the
        histogram specification, if provided.
        :param prop: Property for which the specification is to be returned of.
        :return: the maximum histogram value and the bin width for the histogram.
        """
        max_value, bin_width = None, None
        if self.hist_specs:
            if prop in self.hist_specs.keys():
                max_value = self.hist_specs[prop]['max']
                bin_width = self.hist_specs[prop]['delta']
        return max_value, bin_width

    def _create_histogram(self, axes, herbivore_data: list, carnivore_data: list, title: str):
        """
        Create a histogram plot for the properties Fitness, Weight or Age
        :param axes: Axes to plot the histogram in
        :param herbivore_data: The herbivore data to plot
        :param carnivore_data: The carnivore data to plot
        :param title: Title of the Histogram. Also, the property being plotted.
        """
        axes.set_title(title)
        axes.step(*self._get_hist_values(herbivore_data, *self._get_hist_specs(title.lower())),
                  color='blue',
                  linewidth=2)
        axes.step(*self._get_hist_values(carnivore_data, *self._get_hist_specs(title.lower())),
                  color='red',
                  linewidth=2)

    def _update_histogram(self, axes, herbivore_data: list, carnivore_data: list, title: str):
        """
        Update the histogram plots for the properties
        :param axes: location of the histogram
        :param herbivore_data: The herbivore data to plot
        :param carnivore_data: The carnivore data to plot
        :param title: Title of the Histogram. Also, the property being plotted.
        """
        axes.get_children()[0].set_data(self._get_hist_values(herbivore_data,
                                                              *self._get_hist_specs(title.lower())))
        axes.get_children()[1].set_data(self._get_hist_values(carnivore_data,
                                                              *self._get_hist_specs(title.lower())))
        axes.relim()  # Update x and y limits of the plot
        axes.autoscale()  # Rescale the image

    def _create_legend(self):
        """
        Create the legend.
        Make a faux plot. Turn off axis to hide borders.
        """
        self.ax23.axis('off')
        self.ax23.plot([0], color="green", label='Population', linewidth=2)
        self.ax23.plot([0], color="blue", label='Herbivores', linewidth=2)
        self.ax23.plot([0], color="red", label='Carnivores', linewidth=2)
        self.ax23.legend(loc='center', edgecolor='1.0', fontsize='large')
