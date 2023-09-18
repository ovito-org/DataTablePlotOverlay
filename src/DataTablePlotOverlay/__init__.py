# This Python Viewport Overlay modifier places chosen data table plots from your pipeline onto the rendered image.

from ovito.vis import *
from ovito.data import *
from traits.api import *
from ovito.traits import *
import matplotlib 
import numpy as np 

class DataTablePlotOverlay(ViewportOverlayInterface):
    
    identifier = Str("", label="Data Table identifier", ovito_placeholder="e.g. coordination-rdf")
    plot_mode = Enum("Auto-detect", "Line", "Histogram", "BarChart", "Scatter", label="plot mode")  
    
    group1 = "Appearance in rendered image" 
    px = Range(low=0., high=1., value=0.05, label="X-Position", ovito_unit="percent", ovito_group=group1)
    py = Range(low=0., high=1., value=0.95, label="Y-Position", ovito_unit="percent", ovito_group=group1)      
    w = Range(low=0.05, high=1, value=0.25, label="Width", ovito_unit="percent", ovito_group=group1) 
    h = Range(low=0.05, high=1, value=0.25, label="Height", ovito_unit="percent", ovito_group=group1)
    alpha = Range(low=0., high=1., value = 0.5, label="Opacity", ovito_unit="percent", ovito_group=group1)
    anchor = Enum("north west", "center", "west", "south west", "south", "south east", "east", "north east", "north", label="Anchor", ovito_group=group1)  
    
    group2 = "Figure style settings"
    title = Str(label="Title", ovito_placeholder="‹auto›", ovito_group=group2)
    x_label = Str(label="X-axis label", ovito_placeholder="‹auto›", ovito_group=group2)
    y_label = Str(label="Y-axis label", ovito_placeholder="‹auto›", ovito_group=group2)
    use_color = Bool(label="Use uniform color", value = False, ovito_group=group2)
    color = ColorTrait(default=(0.401, 0.435, 1.0), ovito_group=group2)  
    font_size = Range(value = 1., low=0.01, label="Text scaling", ovito_unit="percent", ovito_group=group2)
    y_minor_ticks = Bool(label="Minor y-ticks", ovito_group=group2)
    x_minor_ticks = Bool(label="Minor x-ticks", ovito_group=group2)      
                                                                                                                                                          
    def render(self, canvas: ViewportOverlayInterface.Canvas, data: DataCollection, **kwargs):
        if data.tables == {}:
           raise RuntimeError('No data tables found in selected pipeline.')
        
        # List available Data Table identifiers                
        log = "Available data tables: \n"
        for table in list(data.tables.keys()):
            log += "  *  " + table + "\n"
        if self.identifier not in data.tables:
            raise RuntimeError(f'Data Table "{self.identifier}" not found. ' + log)
        print(log) 
                       
        with canvas.mpl_figure(pos=(self.px,self.py), size=(self.w, self.h), font_scale = self.font_size, anchor=self.anchor, alpha=self.alpha, tight_layout=True) as fig:
            
            if self.use_color == True:
                #Overwrite matplotlib's default color cycle 
                matplotlib.pyplot.rcParams['axes.prop_cycle'] = matplotlib.pyplot.cycler(color=[self.color])
           
            plot_data = data.tables[self.identifier].xy()
            plot = data.tables[self.identifier]
            
            # OVITO's internal plot type assigned to the chosen data table
            mode = str(data.tables[self.identifier].plot_mode).split(".")[1]
            
            # Plot type chosen by the user
            ## Auto-detect
            if self.plot_mode == "Auto-detect":
                if mode == "NoPlot":
                    raise RuntimeError("Auto-detection of plot mode not possible. Please choose from drop-down.") 
            else:
                mode = self.plot_mode
    
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
                    for i in range(1, plot_data.shape[1]):
                        if self.use_color == False:
                            ax.bar(labels, plot_data[:,i][:len(labels)], color=colors, width=0.8*(plot_data[:,0][0]-plot_data[:,0][1]))
                        else:
                            ax.bar(labels, plot_data[:,i][:len(labels)], color=self.color, width=0.8*(plot_data[:,0][0]-plot_data[:,0][1]))
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
            if self.x_label != "":
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
               