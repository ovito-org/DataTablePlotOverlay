# This Python Viewport Overlay modifier places chosen data table plots from your pipeline onto the rendered image.

from ovito.vis import *
from ovito.data import *
from traits.api import *
from ovito.traits import *
import matplotlib 
import numpy as np 

class DataTablePlotOverlay(ViewportOverlayInterface):
    
    identifier = Str("", label="Data table identifier", ovito_placeholder="e.g. coordination-rdf")
    plot_mode = Map({"Auto-detect":"Auto-detect", "Line":"Line", "Distribution histogram":"Histogram", "Category bar chart":"BarChart", "Scatter":"Scatter"}, label="Plot type")  

    group1 = "Positioning" 
    alignment =  Map({"Top left": (0.,1.,"north west"), "Top":(0.5, 1., "north"), "Top right":(1.,1., "north east"), "Right":(1., 0.5, "east"), "Bottom right": (1.,0., "south east"), "Bottom": (0.5,0., "south"), "Bottom left":(0.,0., "south west"), "Left":(0.,0.5, "west")}, label="Alignment", ovito_group=group1)  
    px = Range(low=-1., high=1., value=0.0, label="X-offset", ovito_unit="percent", ovito_group=group1)
    py = Range(low=-1., high=1., value=0.0, label="Y-offset", ovito_unit="percent", ovito_group=group1)      
    w = Range(low=0.05, high=1, value=0.5, label="Width", ovito_unit="percent", ovito_group=group1) 
    h = Range(low=0.05, high=1, value=0.5, label="Height", ovito_unit="percent", ovito_group=group1)
    alpha = Range(low=0., high=1., value = 1., label="Opacity", ovito_unit="percent", ovito_group=group1)
    
    group2 = "Figure style"
    title = Str(label="Title", ovito_placeholder="‹auto›", ovito_group=group2)
    x_label = Str(label="X-axis label", ovito_placeholder="‹auto›", ovito_group=group2)
    y_label = Str(label="Y-axis label", ovito_placeholder="‹auto›", ovito_group=group2)
    use_color = Bool(label="Use uniform color", value = False, ovito_group=group2)
    color = ColorTrait(default=(0.401, 0.435, 1.0), ovito_group=group2, label = "Unicolor")  
    font_size = Range(value = 1., low=0.01, label="Text scaling", ovito_unit="percent", ovito_group=group2)
     
    fix_y_range = Bool(value = False, label="Fix y-range", ovito_group=group2)
    y_range_max = Float(5.0, label="Y max", ovito_group=group2)
    y_range_min = Float(0.0, label="Y min", ovito_group=group2) 

    y_minor_ticks = Bool(label="Minor y-ticks", ovito_group=group2)
    x_minor_ticks = Bool(label="Minor x-ticks", ovito_group=group2)      
                                                                                                                                                          
    def render(self, canvas: ViewportOverlayInterface.Canvas, data: DataCollection, **kwargs):
        
        if data == None:
            return 
        
        if data.tables == {}:
           raise RuntimeError('No data tables found in selected pipeline.')
        
        # List available Data Table identifiers                
        log = "Available data tables: \n"
        for table in list(data.tables.keys()):
            log += "  *  " + table + "\n"
        print(log)    
        if self.identifier not in data.tables:
            if self.identifier == '':
                return
            print (f'Data Table "{self.identifier}" not found. ')
            return
                
        with canvas.mpl_figure(pos=(self.alignment_[0] + self.px, self.alignment_[1] + self.py), size=(self.w, self.h), font_scale = self.font_size, anchor=self.alignment_[2], alpha=self.alpha, tight_layout=True) as fig:
            
            if self.use_color == True:
                #Overwrite matplotlib's default color cycle 
                matplotlib.pyplot.rcParams['axes.prop_cycle'] = matplotlib.pyplot.cycler(color=[self.color])
            else:
                matplotlib.pyplot.rcParams['axes.prop_cycle'] = matplotlib.pyplot.cycler('color', ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'])

            plot_data = data.tables[self.identifier].xy()
            plot = data.tables[self.identifier]
            
            # OVITO's internal plot type assigned to the chosen data table
            mode = str(data.tables[self.identifier].plot_mode).split(".")[1]

            # Plot type chosen by the user
            ## Auto-detect
            if self.plot_mode_ == "Auto-detect":
                if mode == "NoPlot":
                    raise RuntimeError("Auto-detection of plot mode not possible. Please choose from drop-down.") 
            else:
                mode = self.plot_mode_
    
            if plot_data.shape[0] < 2 and mode != "Scatter":
                    raise RuntimeError(f"Not enough data points for {mode} plot.")
            if plot_data.shape[0] > 100 and mode in ["Histogram", "BarChart"]:
                    raise RuntimeError(f"Too many data points for {mode} plot.")
            
            ax = fig.subplots()            
            ax.patch.set_alpha(self.alpha)

            ## All other plot types                            
            if mode == "Line":
                for i in range(1, plot_data.shape[1]):
                    ax.plot(plot_data[:,0], plot_data[:,i])
            elif mode == "Histogram":
                for i in range(1, plot_data.shape[1]):
                    ax.bar(plot_data[:,0], plot_data[:,i], width=0.8*(plot_data[:,0][0]-plot_data[:,0][1]))
            elif mode == "BarChart":
                if plot.x is not None:
                    if plot.x.types:
                        labels = [[type.name, type.id, type.color] for type in plot.x.types]
                        sorted_labels = sorted(labels, key=lambda x: x[1])
                        labels = [label[0] for label in sorted_labels]
                        colors = [label[2] for label in sorted_labels]
                        type_ids = [label[1] for label in sorted_labels]
                    for i in range(1, plot_data.shape[1]):
                        if self.use_color == False:
                            ax.bar(labels, plot_data[:,i][type_ids], color=colors, width=0.8*(plot_data[:,0][0]-plot_data[:,0][1]))
                        else:
                            ax.bar(labels, plot_data[:,i][type_ids], color=self.color, width=0.8*(plot_data[:,0][0]-plot_data[:,0][1]))
                    if any([len(label) > 10 for label in labels]):
                        ax.set_xticks(ax.get_xticks(), ax.get_xticklabels(), rotation=45, ha='right')
                else:
                    for i in range(1, plot_data.shape[1]):
                        ax.bar(plot_data[:,0], plot_data[:,i], width=(plot_data[:,0][0]-plot_data[:,0][1]))  
            elif mode == "Scatter":
                for i in range(1, plot_data.shape[1]):
                    ax.scatter(plot_data[:,0], plot_data[:,i])     
            
            # Change axis labels and title to user input if specified
            # otherwise use info from data table 
            if self.x_label != "":
                ax.set_xlabel(self.x_label)
            else:
                if plot.x is not None:
                    ax.set_xlabel(plot.x.identifier)
                else:
                    ax.set_xlabel(plot.axis_label_x)
            if self.y_label != "":
                ax.set_ylabel(self.y_label)
            else:
                ax.set_ylabel(plot.y.identifier)
            if self.title != "":
                ax.set_title(self.title) 
            else:
                ax.set_title(plot.title)
                
            # Show legend if data table has more than one y-component
            if plot.y.component_count >= 2 and plot.y.component_names is not None:   
                    ax.legend(plot.y.component_names, loc ="best", handlelength=0.7)
  
            # Show minor tics on axes    
            if self.y_minor_ticks == True:
                ax.yaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
            if self.x_minor_ticks == True:
                ax.xaxis.set_minor_locator(matplotlib.ticker.AutoMinorLocator())
               
            if self.fix_y_range:
                ax.set_ylim(self.y_range_min, self.y_range_max)