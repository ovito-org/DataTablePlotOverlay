# Viewport overlay painting a data table graph onto the rendered image.

from ovito.vis import ViewportOverlayInterface
from ovito.data import DataTable, DataCollection
from traits.api import Map, Range, Str, Bool, Float
from ovito.traits import Color, Vector2, DataObjectReference
import matplotlib

class DataTablePlotOverlay(ViewportOverlayInterface):

    input_table = DataObjectReference(DataTable, label="Data source")
    plot_mode = Map({
            "Auto-detect": None, 
            "Line": DataTable.PlotMode.Line, 
            "Distribution histogram": DataTable.PlotMode.Histogram, 
            "Category bar chart": DataTable.PlotMode.BarChart, 
            "Scatter": DataTable.PlotMode.Scatter
        }, label="Plot type")

    group1 = "Positioning"
    alignment = Map({
            "Top left": (0., 1., "north west"), 
            "Top": (0.5, 1., "north"), 
            "Top right": (1.,1., "north east"), 
            "Right": (1., 0.5, "east"), 
            "Bottom right": (1., 0., "south east"), 
            "Bottom": (0.5, 0., "south"), 
            "Bottom left": (0., 0., "south west"), 
            "Left":(0., 0.5, "west")
        }, label="Alignment", ovito_group=group1)
    offset = Vector2(low=-1.0, high=1.0, default=(0.0, 0.0), label="Offset", ovito_unit="percent", ovito_group=group1)
    size = Vector2(low=0.05, high=1.0, default=(0.5, 0.5), label="Size", ovito_unit="percent", ovito_group=group1)

    group2 = "Figure style"
    title = Str(label="Title", ovito_placeholder="‹auto›", ovito_group=group2)
    x_label = Str(label="X-axis label", ovito_placeholder="‹auto›", ovito_group=group2)
    y_label = Str(label="Y-axis label", ovito_placeholder="‹auto›", ovito_group=group2)
    use_color = Bool(label="Use uniform color", value=False, ovito_group=group2)
    color = Color(default=(0.401, 0.435, 1.0), ovito_group=group2, label="Unicolor")
    alpha = Range(low=0.0, high=1.0, value=1.0, label="Bg. opacity", ovito_unit="percent", ovito_group=group2)
    font_size = Range(value=1.0, low=0.01, label="Text scaling", ovito_unit="percent", ovito_group=group2)

    x_minor_ticks = Bool(label="X-axis minor ticks", ovito_group=group2)
    y_minor_ticks = Bool(label="Y-axis minor ticks", ovito_group=group2)

    group3 = "Plot range"
    fix_y_range = Bool(value=False, label="Fixed y-range:", ovito_group=group3)
    y_range_max = Float(5.0, label="Y-max", ovito_group=group3)
    y_range_min = Float(0.0, label="Y-min", ovito_group=group3)

    def render(self, canvas: ViewportOverlayInterface.Canvas, data: DataCollection, **kwargs):

        if data == None:
            raise RuntimeError("No pipeline selected.")
        if not self.input_table:
            print("No data table selected.")
            return

        # Look up selected data table in data collection.
        plot = self.input_table.get_from(data)
        if not plot:
            raise RuntimeError(f"Data table '{self.input_table}' not found in pipeline output.")
        if plot.y is None:
            raise RuntimeError(f"Data table '{self.input_table}' cannot be plotted because it has no data y-axis.")

        with canvas.mpl_figure(pos=(self.alignment_[0] + self.offset[0], self.alignment_[1] + self.offset[1]), size=self.size, font_scale = self.font_size, anchor=self.alignment_[2], alpha=self.alpha, tight_layout=True) as fig:

            # Select plot mode
            mode = self.plot_mode_
            if mode == None:
                mode = plot.plot_mode
                if mode == DataTable.PlotMode.NoPlot:
                    raise RuntimeError("Auto-detection of plot mode not possible. Please choose from drop-down list.")

            # Obtain data to be plotted
            plot_data = plot.xy()
            if plot_data.shape[0] < 2 and mode != DataTable.PlotMode.Scatter:
                    raise RuntimeError(f"Not enough data points for {mode.name} plot.")
            if plot_data.shape[0] > 100 and mode in [DataTable.PlotMode.Histogram, DataTable.PlotMode.BarChart]:
                    raise RuntimeError(f"Too many data points for {mode.name} plot.")

            ax = fig.subplots()
            ax.patch.set_alpha(self.alpha)

            if mode == DataTable.PlotMode.Line:
                for i in range(1, plot_data.shape[1]):
                    ax.plot(plot_data[:,0], plot_data[:,i])
            elif mode == DataTable.PlotMode.Histogram:
                for i in range(1, plot_data.shape[1]):
                    ax.bar(plot_data[:,0], plot_data[:,i], width=0.8*(plot_data[:,0][1]-plot_data[:,0][0]))
            elif mode == DataTable.PlotMode.BarChart:
                if plot.x is not None:
                    if plot.x.types:
                        labels = [[type.name, type.id, type.color] for type in plot.x.types]
                        sorted_labels = sorted(labels, key=lambda x: x[1])
                        labels = [label[0] for label in sorted_labels]
                        colors = [label[2] for label in sorted_labels]
                        type_ids = [label[1] for label in sorted_labels]
                    for i in range(1, plot_data.shape[1]):
                        if self.use_color == False:
                            ax.bar(labels, plot_data[:,i][type_ids], width=0.8*(plot_data[:,0][1]-plot_data[:,0][0]))
                        else:
                            ax.bar(labels, plot_data[:,i][type_ids], color=self.color, width=0.8*(plot_data[:,0][1]-plot_data[:,0][0]))
                    if any([len(label) > 10 for label in labels]):
                        ax.set_xticks(ax.get_xticks(), ax.get_xticklabels(), rotation=45, ha='right')
                else:
                    for i in range(1, plot_data.shape[1]):
                        ax.bar(plot_data[:,0], plot_data[:,i], width=(plot_data[:,0][0]-plot_data[:,0][1]))
            elif mode == DataTable.PlotMode.Scatter:
                for i in range(1, plot_data.shape[1]):
                    ax.scatter(plot_data[:,0], plot_data[:,i])

            # Change axis labels and title to user input if specified;
            # otherwise use info from data table
            if self.x_label:
                ax.set_xlabel(self.x_label)
            else:
                if plot.x is not None:
                    ax.set_xlabel(plot.x.identifier)
                else:
                    ax.set_xlabel(plot.axis_label_x)
            ax.set_ylabel(self.y_label if self.y_label else plot.y.identifier)
            ax.set_title(self.title if self.title else plot.title)

            # Show legend if data table has more than one y-component
            if plot.y.component_count >= 2 and plot.y.component_names is not None:
                    ax.legend(plot.y.component_names, loc="best", handlelength=0.7)

            # Show minor ticks on axes
            if self.y_minor_ticks:
                ax.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
            if self.x_minor_ticks:
                ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())

            if self.fix_y_range:
                ax.set_ylim(self.y_range_min, self.y_range_max)