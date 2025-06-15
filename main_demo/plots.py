from demo_utils import documented, democode, push_group, pop_group, launch_demo, demosection
import dearcygui as dcg
import numpy as np
import random
import time
import datetime


# decorators:
# - documented: the description (markdown) is displayed
# - democode: the code is displayed and can edited (and run again)
# - demosection: the section is displayed in the table of contents,
#    the section name is extracted from the function name.

        
push_group("Introduction")

@demosection(dcg.Plot, dcg.PlotAxisConfig, dcg.PlotLegendConfig, dcg.AxisTag, dcg.PlotAnnotation)
@documented
def _intro(C: dcg.Context):
    """
    ## Introduction to Plots

    DearCyGui provides powerful plotting capabilities based on ImPlot, a high-performance plotting library designed for interactive visualization.
    
    ### Key Features
    
    - **Rich Plot Types**: Line plots, scatter plots, bar charts, pie charts, error bars, heatmaps, and more
    - **Interactive Navigation**: Pan, zoom, and data inspection with mouse and keyboard controls
    - **Drawings**: Very convenient way to have a canvas to draw with dcg.Draw* items
    - **Customizable Styling**: Complete control over colors, fonts, axes, legends and other visual elements
    - **Responsive Layout**: Plots automatically adapt to available space and can be resized
    - **Real-time Updates**: Updating the plot is efficient and can be done at high frame rates
    - **Annotations**: Add text, shapes, and images to highlight important information
    
    ### Plot Structure
    
    Plots in DearCyGui follow a hierarchical structure:
    
    1. **Plot Container**: A `dcg.Plot` object that defines the overall plot area
    2. **Series**: Various series types (PlotLine, PlotScatter, etc.) that visualize data
    3. **Axes**: three X and Y axes that can be independently configured
    4. **Annotations**: Optional text, shapes, and other decorative elements
    
    ### This Demo
    
    This demo will walk you through:
    
    - Creating various plot types for different visualization needs
    - Customizing axes, legends, and styling options
    - Working with advanced plot configurations
    - Adding interactivity to your plots
    - Annotating plots with text and shapes
    
    Each section contains working examples you can experiment with and adapt for your own applications.
    """
    pass

pop_group()  # End Introduction

push_group("Basic Plots")

push_group("Scatter Plots")

@demosection(dcg.Plot, dcg.PlotScatter)
@documented
def _scatter_plots(C: dcg.Context):
    """
    ### Scatter Plots

    Scatter plots consist of points plotted on a two-dimensional plane,
    where each point represents an observation in the dataset.
    
    This demo section demonstrates:
    - Basic scatter plots
    - Marker customization
    - Size and color mapping
    - Advanced scatter plotting using DrawInPlot
    
    Scatter plots are excellent for visualizing the relationship between two variables
    or for displaying data points where each point represents an individual observation.
    """
    pass

@demosection(dcg.Plot, dcg.PlotScatter)
@documented
@democode
def _scatter_basic(C: dcg.Context):
    """
    ### Basic Scatter Plot
    
    Scatter plots display the relationship between two variables by placing points at their corresponding (x,y) coordinates. This simple visualization can reveal patterns, clusters, and outliers in your data.

    How to produce a scatter plot:
    - Create a `dcg.Plot` object to define the plot area
    - Use `dcg.PlotScatter` to add points to the plot. It takes X and Y data arrays of equal length.
    - X, Y can be numpy arrays. Arrays of types int32, float32 or float64 will not generate an internal copy of the data.
    - Optionally, customize the plot with labels, colors, and markers.

    """
    with dcg.Plot(C, label="Basic Scatter", height=300, width=-1) as plot:
        # Generate some random data
        np.random.seed(42)  # For reproducibility
        x = np.random.rand(50)
        y = np.random.rand(50)
        
        # Create a basic scatter plot with default settings
        dcg.PlotScatter(C, label="Random Points", X=x, Y=y)
        
        # Add labels
        plot.X1.label = "X Axis"
        plot.Y1.label = "Y Axis"

@demosection(dcg.Plot, dcg.PlotScatter, dcg.PlotMarker, dcg.ThemeStyleImPlot, dcg.ThemeColorImPlot)
@documented
@democode
def _scatter_markers(C: dcg.Context):
    """
    ### Marker Customization
    
    DearCyGui provides various marker styles and styling customizations.

    #### Color customization:
    `ThemeColorImPlot` has various properties available to affect scatter plots:
    - `line`: This attribute affects the default color of many plot items,
        including scatter plots.
    - `marker_fill`: This attribute affects the fill color of markers.
    - `marker_outline`: This attribute affects the outline color of markers.

    #### Marker customization:
    `ThemeStyleImPlot` has various properties available to affect scatter plots:
    - `marker`: This attribute affects the shape of the markers and must a valid `dcg.PlotMarker` value:
        - `dcg.PlotMarker.CIRCLE`: A circular marker
        - `dcg.PlotMarker.SQUARE`: A square marker
        - `dcg.PlotMarker.DIAMOND`: A diamond marker
        - `dcg.PlotMarker.UP`: An upward-pointing triangle marker
        - `dcg.PlotMarker.DOWN`: A downward-pointing triangle marker
        - `dcg.PlotMarker.LEFT`: A left-pointing triangle marker
        - `dcg.PlotMarker.RIGHT`: A right-pointing triangle marker
        - `dcg.PlotMarker.CROSS`: A cross marker
        - `dcg.PlotMarker.PLUS`: A plus marker
        - `dcg.PlotMarker.ASTERISK`: An asterisk marker
    - `marker_size`: This attribute affects the radius of the markers.
    - `marker_weight`: This attribute affects the outline weight of markers in pixels.

    Below are some examples.
    """
    with dcg.Plot(C, label="Marker Styles", height=300, width=-1) as plot:
        # Generate data for multiple series
        t = np.linspace(0, 10, 30)
        x1 = t
        y1 = np.sin(t)
        x2 = t
        y2 = np.cos(t)
        x3 = t
        y3 = np.sin(t) * np.cos(t)
        
        # Different marker types
        dcg.PlotScatter(C, label="Circles", X=x1, Y=y1, 
                        theme=dcg.ThemeStyleImPlot(C,
                                                   marker=dcg.PlotMarker.CIRCLE,
                                                   marker_size=5))
        
        dcg.PlotScatter(C, label="Squares", X=x2, Y=y2, 
                        theme=dcg.ThemeStyleImPlot(C,
                                                   marker=dcg.PlotMarker.SQUARE,
                                                   marker_size=6))

        # Composed style
        with dcg.ThemeList(C) as theme:
            dcg.ThemeColorImPlot(C, marker_fill=(0, 255, 0), marker_outline=(0, 0, 255))
            dcg.ThemeStyleImPlot(C, marker=dcg.PlotMarker.DIAMOND, marker_size=7)
        
        dcg.PlotScatter(C, label="Diamonds", X=x3, Y=y3, 
                        theme=theme)
        
        # Add labels
        plot.X1.label = "X Value"
        plot.Y1.label = "Y Value"

@demosection(dcg.Plot, dcg.PlotScatter, dcg.PlotMarker, dcg.ThemeStyleImPlot, dcg.ThemeColorImPlot)
@documented
@democode
def _scatter_example(C: dcg.Context):
    """
    ### Practical Example: Iris Dataset
    
    Using scatter plots to visualize real data - in this case,
    a sample from the classic Iris dataset showing the relationship
    between sepal measurements, with species indicated by color.
    
    #### Data science insight:
    Notice how the setosa species (red) forms a distinct cluster,
    while versicolor (blue) and virginica (green) show some overlap.
    This visual pattern immediately suggests that setosa is more easily
    distinguishable using these measurements alone.
    """
    # Sample data inspired by the Iris dataset
    sepal_length = [5.1, 4.9, 4.7, 7.0, 6.4, 6.9, 6.3, 5.8, 7.1]
    sepal_width = [3.5, 3.0, 3.2, 3.2, 3.2, 3.1, 2.5, 2.7, 3.0]
    species = ["setosa", "setosa", "setosa", "versicolor", "versicolor", "versicolor", "virginica", "virginica", "virginica"]
    
    # Map species to colors
    species_colors = {
        "setosa": (255, 0, 0),      # Red
        "versicolor": (0, 0, 255),  # Blue
        "virginica": (0, 255, 0)    # Green
    }
    
    with dcg.Plot(C, label="Iris Dataset", height=300, width=-1) as plot:
        # Plot each species as a separate series for better legend
        for s, color in species_colors.items():
            indices = [i for i, species_name in enumerate(species) if species_name == s]
            if indices:
                x_vals = [sepal_length[i] for i in indices]
                y_vals = [sepal_width[i] for i in indices]
                with dcg.ThemeList(C) as theme:
                    dcg.ThemeStyleImPlot(
                        C,
                        marker=dcg.PlotMarker.CIRCLE,
                        marker_size=8
                    )
                    dcg.ThemeColorImPlot(C, marker_fill=color, marker_outline=color)
                dcg.PlotScatter(C,
                                label=s, 
                                X=x_vals,
                                Y=y_vals, 
                                theme=theme)
        
        # Add labels
        plot.X1.label = "Sepal Length (cm)"
        plot.Y1.label = "Sepal Width (cm)"

@demosection(dcg.DrawInPlot, dcg.DrawRegularPolygon, dcg.DrawInvisibleButton, dcg.Tooltip)
@documented
@democode
def _scatter_advanced(C: dcg.Context):
    """
    ### Advanced Scatter Plotting with DrawInPlot

    PlotScatter is not enough for your needs? Consider using DrawInPlot.

    When standard scatter plots aren't flexible enough,
    DearCyGui's DrawInPlot API offers limitless possibilities for custom visualizations.
    This approach lets you directly draw in plot coordinates, opening up new dimensions
    of data representation.
    
    #### When to use DrawInPlot for scatter plots:
    - Representing more than two dimensions (using size, color, shape)
    - Creating interactive data points with tooltips, click or drag behavior
    - Customizing individual markers beyond standard options
    - Implementing novel visual encodings not available in standard plots

    #### Implementation considerations:
    - Drawing each marker individually offers maximum flexibility but has higher overhead.
        The principal overhead is in creating the plot as more Python code is needed.
    - For both `PlotScatter` and `DrawInPlot` rendering performance may not be
        real time for very large datasets (>50K points). `dcg.DrawingClip` can be used
        to improve performance by limiting the area of the plot that is drawn.
    - When instantiating UI items (such as tooltips) in a `with DrawInPlot` block,
        be careful of the target parent, as UI items can have as parent plot series
        (for the legend popup).
    """
    ui_container = C.fetch_parent_queue_back()
    
    with dcg.Plot(C, label="Advanced Scatter Plot Using DrawInPlot", height=300, width=-1) as plot:
        # Generate data with additional dimensions
        np.random.seed(123)
        n_points = 80
        x = np.random.normal(size=n_points)
        y = np.random.normal(size=n_points)
        
        # Third dimension represented by distance from origin
        distance = np.sqrt(x**2 + y**2)
        
        # Fourth dimension (just for demo purposes)
        angle = np.arctan2(y, x)
        
        # Map distance to size (larger points farther from center)
        sizes = 1 + 6 * (distance / distance.max())
        
        # Map angle to color using a colormap
        colors = []
        for a in angle:
            # Convert angle to hue (0-360 degrees)
            hue = (np.degrees(a) + 180) / 360.0
            # Create RGB color (simple HSV to RGB conversion)
            r = int(255 * (0.5 + 0.5 * np.cos(2 * np.pi * (hue + 0.0/3))))
            g = int(255 * (0.5 + 0.5 * np.cos(2 * np.pi * (hue + 1.0/3))))
            b = int(255 * (0.5 + 0.5 * np.cos(2 * np.pi * (hue + 2.0/3))))
            colors.append((r, g, b))
        
        # For advanced needs, such as custom color per marker,
        # it becomes easier to draw directly each marker
        with dcg.DrawInPlot(C, no_legend=False, label="Markers"):
            for i in range(n_points):
                dcg.DrawRegularPolygon(C,
                             center=(x[i], y[i]),
                             direction=0.5*np.pi,
                             num_points=5,
                             radius=-sizes[i], # minus for screen space
                             fill=colors[i], color=0)
                # Advanced: interactive data
                star_as_button = \
                    dcg.DrawInvisibleButton(C,
                        min_side=3.*sizes[i],
                        p1=(x[i], y[i]),
                        p2=(x[i], y[i]))
                with dcg.Tooltip(C, target=star_as_button, parent=ui_container):
                    dcg.Text(C, value=f"Point {i}: ({x[i]:.2f}, {y[i]:.2f})")
        
        # Add labels
        plot.X1.label = "X Value"
        plot.Y1.label = "Y Value"

pop_group()  # End Scatter Plots
push_group("Line Plots")

# Line plots - demonstrates basic line plots with different styles
@demosection(dcg.Plot, dcg.PlotLine)
@documented
def _line_plots(C: dcg.Context):
    """
    ### Line Plots

    Line plots are used to visualize data points connected by lines.
    They are particularly useful for showing trends over time or continuous data.

    This section demonstrates:
    - Basic line plots
    - Multiple lines on one plot
    - Line styling (color, width, shade, segments)
    - Customizing line styles
    - Adding legends and annotations
    - Handling large datasets efficiently
    - Using line plots for time series data
    """
    pass


@demosection(dcg.Plot, dcg.PlotLine)
@documented
@democode
def _line_basic(C: dcg.Context):
    """
    ### Basic Line Plot
    
    Line plots connect data points with straight lines,
    creating a visual representation of how values change.
    They're ideal for showing trends, patterns, and
    relationships in sequential data.
    
    #### Creating a basic line plot:
    - Use `dcg.Plot` to create a plot container
    - Use `dcg.PlotLine` to add a line series
    - Provide X and Y data arrays of equal length.
        Arrays of types int32, float32 or float64 will not
        generate an internal copy of the data. This is
        particularly useful for dynamic data.
    - Optionally, customize the line with colors, strength and labels
    
    Try changing the sin function to other mathematical functions (cos, tan, log)
    to see how the line changes!
    """
    with dcg.Plot(C, label="Basic Line Plot", height=300, width=-1) as plot:
        # Generate data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        
        # Create a basic line plot
        dcg.PlotLine(C, label="Sin(x)", X=x, Y=y)
        
        # Add labels
        plot.X1.label = "X Axis"
        plot.Y1.label = "Y Axis"


@demosection(dcg.PlotLine, dcg.ThemeList, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
@democode
def _line_styling(C: dcg.Context):
    """
    ### Line Styling

    Line plots can be customized in various ways to enhance their visual appeal and clarity.

    #### Color customization:
    Use `ThemeColorImPlot`'s `Line` attribute to set the default color of lines.

    #### Line weight:
    Use `ThemeStyleImPlot`'s `LineWeight` attribute to set the thickness of lines.

    """
    with dcg.Plot(C, label="Line Styling", height=300, width=-1) as plot:
        # Generate data
        x = np.linspace(0, 10, 50)
        y1 = np.sin(x)
        y2 = np.cos(x)
        
        # Standard line with default styling
        dcg.PlotLine(C, label="Default Line", X=x, Y=y1)
        
        # Line with custom color, width and no markers
        with dcg.ThemeList(C) as theme1:
            dcg.ThemeColorImPlot(C, line=(255, 0, 0))  # Red line
            dcg.ThemeStyleImPlot(C, line_weight=3.0)     # Thicker line
        dcg.PlotLine(C, label="Custom Line", X=x, Y=y2, theme=theme1)
        
        # Add labels
        plot.X1.label = "X Value"
        plot.Y1.label = "Y Value"


@demosection(dcg.Plot, dcg.PlotLine, dcg.PlotShadedLine, dcg.ThemeList, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
@democode
def _line_shaded(C: dcg.Context):
    """
    ### Shaded Line Areas

    Shaded areas in line plots can convey additional information about the data.

    Two series items can be produced to produce shared areas:
    - `PlotShadedLine` for shaded areas between two lines
    - `PlotLine` with `shaded=True` for shading below a line

    In both cases, the `ThemeColorImPlot` and `ThemeStyleImPlot` attributes
    'Fill' and 'FillAlpha' can be used to customize the color and
    transparency of the shaded area.
    """
    with dcg.Plot(C, label="Shaded Areas", height=300, width=-1) as plot:
        # Generate data
        x = np.linspace(0, 10, 100)
        y1 = np.sin(x)
        y2 = np.sin(x) + 0.3  # Upper bound
        y3 = np.sin(x) - 0.3  # Lower bound
        
        # Standard line
        dcg.PlotLine(C, label="Sin(x)", X=x, Y=y1)
        
        # Line with area filled to axis
        with dcg.ThemeList(C) as theme1:
            dcg.ThemeColorImPlot(C, 
                               line=(0, 0, 255),         # Blue line
                               fill=(0, 0, 255, 64))     # Transparent blue fill
            #dcg.ThemeStyleImPlot(C, FillAlpha=0.2) # Alternative way to set transparency
        dcg.PlotLine(C, label="Filled to Axis", X=x, Y=np.cos(x), theme=theme1, shaded=True)
        
        # Create a confidence interval effect with shaded area between two curves
        with dcg.ThemeList(C) as theme2:
            dcg.ThemeColorImPlot(C, 
                               line=(255, 0, 0),         # Red line for bounds
                               fill=(255, 0, 0, 40))     # Very transparent red fill
        dcg.PlotShadedLine(C, label="Confidence Interval", X=x, Y1=y2, Y2=y3, theme=theme2)
        
        # Add labels
        plot.X1.label = "X Value"
        plot.Y1.label = "Y Value"


@demosection(dcg.Plot, dcg.PlotLine, dcg.PlotStairs, dcg.ThemeList, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
@democode
def _line_segments_steps(C: dcg.Context):
    """
    ### Line Segments and Step Lines

    In order to draw dashed lines and stair steps, three different
    options are available:
    - `PlotLine` with `segments=True` to draw only line pieces between consecutive points.
        It works by drawing only a line every two points.
    - `PlotStairs` will create horizontal steps between points.
        In addition `PlotStairs` with `shaded=True` will fill the area below the steps.
    - For complex line layouts, you can revert to using `DrawInPlot` directly.

    """
    with dcg.Plot(C, label="Line Segments & Steps", height=300, width=-1) as plot:
        # Generate data
        x = np.linspace(0, 10, 20)  # Fewer points to see steps clearly
        y = np.sin(x)
        
        # Standard continuous line for comparison
        dcg.PlotLine(C, label="Standard Line", X=x, Y=y)
        
        # Line with segments (disconnected segments)
        with dcg.ThemeList(C) as theme1:
            dcg.ThemeColorImPlot(C, line=(255, 165, 0))  # Orange line
            dcg.ThemeStyleImPlot(C, line_weight=2.0)
        segmented_line = dcg.PlotLine(C, label="Segmented Line", 
                                    X=x, Y=y + 0.5, 
                                    theme=theme1, 
                                    segments=True)
        
        # Step line (discrete transitions)
        with dcg.ThemeList(C) as theme2:
            dcg.ThemeColorImPlot(C, line=(128, 0, 128))  # Purple line
            dcg.ThemeStyleImPlot(C, line_weight=1.5)
        dcg.PlotStairs(C, label="Step Plot", X=x, Y=y - 0.5, theme=theme2)
        
        # Add shaded step line
        with dcg.ThemeList(C) as theme3:
            dcg.ThemeColorImPlot(C, 
                               line=(0, 128, 128),       # Teal line
                               fill=(0, 128, 128, 50))   # Transparent teal fill
        # PlotStairs accepts a pre_step parameter. Try it !
        dcg.PlotStairs(C, label="Shaded Steps", X=x, Y=y - 1.0, theme=theme3, shaded=True)
        
        # Add labels
        plot.X1.label = "X Value"
        plot.Y1.label = "Y Value"


@demosection(dcg.Plot, dcg.PlotLine, dcg.AxesResizeHandler)
@documented
@democode
def _line_large_data(C: dcg.Context):
    """
    ### Handling Large Datasets

    A common request is to be able to draw lines composed of millions of points.

    This is not possible for DearCyGui to draw real-time that many points using
    PlotLine. What can be done however is to draw a lower resolution of your
    dataset at basic zoom level, and switch for a local higher resolution when needed.
    """
    stats = dcg.Text(C, value="")
    with dcg.Plot(C, label="Large Dataset (10M points). Try to zoom", height=300, width=-1) as plot:
        # Generate a large dataset (10,000,000 points) using Brownian motion
        n_points = 10_000_000
        data_xmin = 0
        data_xmax = 10
        x = np.linspace(data_xmin, data_xmax, n_points)
        # Initialize y with zeros
        y = np.zeros(n_points)
        # Generate Brownian motion (random walk)
        np.random.seed(42)  # For reproducibility
        step_size = 0.001
        steps = np.random.normal(0, step_size, n_points)
        y = np.cumsum(steps)  # Cumulative sum to create the random walk

        # generate various subsampled versions
        # Note: better techniques exist depending on your data type
        # Here using a pyramid with a scale of 4 every level
        downsample_factor = 4
        pyramid_x = []
        pyramid_y = []
        while len(x) > 2000:
            pyramid_x.append(x)
            pyramid_y.append(y)
            x = x[::downsample_factor]
            y = y[::downsample_factor]
            # Ensure no copy display for each level
            x = np.ascontiguousarray(x)
            y = np.ascontiguousarray(y)

        # Plot subsampled data initially
        with dcg.ThemeList(C) as theme:
            dcg.ThemeColorImPlot(C, line=(0, 0, 255))
            dcg.ThemeStyleImPlot(C, line_weight=2.0)

        plot_line = dcg.PlotLine(C,label=f"A lot of data", 
            X=pyramid_x[-1], Y=pyramid_y[-1], theme=theme)

        def zoom_callback(sender, target, data):
            # This function is called when the plot is zoomed or panned.
            ((x_min, x_max, x_scale), (y_min, y_max, y_scale)) = data
            # scale contains the delta of plot units in a pixel.
            # add a margin of 50 pixels (for quick panning)
            x_min -= 50 * x_scale
            x_max += 50 * x_scale
            # Pick a pyramid level:
            proportion_shown = \
                (x_max - x_min) / (data_xmax - data_xmin)
            level = 0
            for level in range(len(pyramid_x)):
                estimated_points_on_screen = \
                    proportion_shown * \
                    pyramid_x[level].shape[0]
                if estimated_points_on_screen < 10000:
                    break
            level = min(level, len(pyramid_x) - 1)
            # Get the subsampled data
            x = pyramid_x[level]
            y = pyramid_y[level]
            # retrieve range to show
            i_left = np.searchsorted(x, x_min)
            i_right = np.searchsorted(x, x_max, side="right")
            # Add a margin of 1 point
            i_left = max(0, i_left - 1)
            i_right = min(len(x), i_right + 1)
            # Update the plot line with the new data
            plot_line.X = x[i_left:i_right]
            plot_line.Y = y[i_left:i_right]
            # Update the label with the number of points
            stats.value = f"Showing {len(plot_line.X)} points using subsampling {4**level}"
            C.viewport.wake()

        # Register the zoom callback
        plot.handlers += [
            dcg.AxesResizeHandler(C,
                                  axes=(dcg.Axis.X1, dcg.Axis.Y1),
                                  callback=zoom_callback)
        ]

        # retrict Y zoom
        plot.Y1.min = pyramid_y[0].min()
        plot.Y1.max = pyramid_y[0].max()
        plot.Y1.lock_max = True
        plot.Y1.lock_min = True

        plot.X1.label = "X Value"
        plot.Y1.label = "Y Value"

        dcg.Text(C, value="Try zooming and panning to test interactive performance with large datasets.")
        dcg.Text(C, value="Double-click in the plot area to fit data to view.")


@demosection(dcg.Plot, dcg.PlotLine, dcg.AxisScale)
@documented
@democode
def _line_time_series(C: dcg.Context):
    """
    ### Time Series Data
    
    Time series data is one of the most common data types in visualization.
    DearCyGui provides specialized tools for handling time-based data effectively,
    with automatic date formatting and appropriate scaling.
    
    #### Understanding time series in DearCyGui:
    - Time is represented as **UNIX timestamps** (seconds since January 1, 1970)
    - The axes can be configured with a specialized time scale, using `dcg.AxisScale.TIME`
    - Data can be plotted directly using timestamps, and DearCyGui will handle the formatting
    - The display of dates and times can be customized using plot attributes `use_local_time`,
       `use_ISO8601`, and `use_24hour_clock`
    """
    with dcg.Plot(C, label="Time Series Plot", height=300, width=-1) as plot:
        # Configure plot for time series
        plot.X1.scale = dcg.AxisScale.TIME
        plot.X1.label = "Date"
        plot.Y1.label = "Value"
        
        # Generate time series data (one year of daily data)
        # Starting from January 1, 2023
        base_timestamp = 1672531200  # January 1, 2023 in UNIX timestamp
        days = 365
        timestamps = np.array([base_timestamp + 86400 * i for i in range(days)])
        
        # Create some simulated stock price data
        np.random.seed(42)  # For reproducibility
        values = [100.0]  # Starting value
        for i in range(1, days):
            # Random walk with slight upward bias
            new_value = values[-1] * (1 + np.random.normal(0.0005, 0.015))
            values.append(new_value)
        values = np.array(values)
        
        # Add some seasonal pattern
        season = 5 * np.sin(np.linspace(0, 2 * np.pi, days))
        values += season
        
        # Plot the time series
        dcg.PlotLine(C, label="Stock Price", X=timestamps, Y=values)
        
        # Add a moving average
        window_size = 30  # 30-day moving average
        moving_avg = np.convolve(values, np.ones(window_size)/window_size, mode='valid')
        # Align the moving average with the right timestamps
        ma_timestamps = timestamps[window_size-1:]
        
        # Plot the moving average
        with dcg.ThemeList(C) as theme:
            dcg.ThemeColorImPlot(C, line=(255, 0, 0))  # Red line
            dcg.ThemeStyleImPlot(C, line_weight=2.0)
        dcg.PlotLine(C, label=f"{window_size}-Day Moving Avg", 
                   X=ma_timestamps, Y=moving_avg, 
                   theme=theme)


pop_group()  # End Line Plots
push_group("Bar Charts")

@demosection(dcg.Plot, dcg.PlotBars)
@documented
@democode
def _bar_charts(C: dcg.Context):
    """
    ### Bar Charts
    
    Bar charts are ideal for comparing quantities across different categories.
    Each bar's height (or length for horizontal bars) represents the value of a specific category.
    
    This section demonstrates:
    - Simple vertical bar charts
    - Customizing bar appearance
    - Grouped bars for multi-category comparisons
    - Stacked bars for part-to-whole relationships
    - Horizontal bar orientation
    """
    # Basic bar chart example
    with dcg.Plot(C, label="Basic Bar Chart", height=300, width=-1) as plot:
        # Data for different categories
        categories = ["Category A", "Category B", "Category C", "Category D", "Category E"]
        values = [45, 67, 32, 58, 73]
        
        # X positions for the bars (can be any numerical values)
        x_positions = np.arange(len(categories))
        
        # Create a basic bar chart
        dcg.PlotBars(C, label="Values", X=x_positions, Y=values, weight=0.7)
        
        # Configure axis
        plot.X1.no_gridlines = True  # Disable gridlines on X axis
        plot.X1.no_tick_marks = True  # Disable tick marks on X axis
        plot.X1.labels = categories  # Set category names as labels
        plot.X1.labels_coord = x_positions  # Position labels at x positions
        
        # Add labels
        plot.X1.label = "Categories"
        plot.Y1.label = "Values"

@demosection(dcg.Plot, dcg.PlotBars, dcg.ThemeList, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
@democode
def _bar_styling(C: dcg.Context):
    """
    ### Bar Styling
    
    Bar charts can be styled in various ways to enhance their visual appeal and clarity.
    
    #### Styling options:
    - **Bar weight**: Controls the width of the bars
    - **Colors**: Can be customized with `ThemeColorImPlot`
    - **Borders**: Can be added for better definition
    - **Spacing**: Can be adjusted to control the gap between bars
    
    This example shows how to customize the appearance of bars.
    """
    with dcg.Plot(C, label="Styled Bar Chart", height=300, width=-1) as plot:
        # Sample data
        categories = ["Q1", "Q2", "Q3", "Q4"]
        values = [250, 420, 380, 310]
        
        # X positions
        x_positions = np.arange(len(categories))
        
        # Create a styled bar chart
        with dcg.ThemeList(C) as theme:
            dcg.ThemeColorImPlot(C, 
                               line=(100, 100, 100),  # Dark gray outline
                               fill=(65, 105, 225))   # Royal blue fill
            dcg.ThemeStyleImPlot(C, line_weight=3.0)   # Outline thickness
            
        dcg.PlotBars(C, 
                   label="Quarterly Sales", 
                   X=x_positions, 
                   Y=values, 
                   weight=0.6,  # Width of the bars
                   theme=theme)
        
        # Configure axis
        plot.X1.no_gridlines = True
        plot.X1.labels = categories
        plot.X1.labels_coord = x_positions
        
        # Add labels
        plot.X1.label = "Quarter"
        plot.Y1.label = "Sales ($K)"

@demosection(dcg.Plot, dcg.PlotBars, dcg.PlotBarGroups, dcg.ThemeList, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
@democode
def _grouped_bars(C: dcg.Context):
    """
    ### Grouped Bar Charts
    
    Grouped (or clustered) bar charts allow for comparing multiple data series across categories.
    Each group represents a category, and within each group are bars for different data series.
    
    #### Implementation options:
    - Use multiple `PlotBars` calls with adjusted x-positions
    - Use `PlotBarGroups` for a simpler API with multi-dimensional data
    
    This example demonstrates both approaches.
    """
    # First method: Using multiple PlotBars with manual positioning
    with dcg.Plot(C, label="Grouped Bars (Manual Method)", height=300, width=-1) as plot:
        # Sample data
        categories = ["Food", "Transport", "Entertainment", "Utilities"]
        x_pos = np.arange(len(categories))
        
        # Three data series
        values1 = [350, 200, 150, 180]  # 2021
        values2 = [320, 220, 190, 170]  # 2022
        values3 = [380, 240, 200, 190]  # 2023
        
        # Bar width and spacing
        bar_width = 0.25
        
        # Create three sets of bars, shifted on x-axis
        dcg.PlotBars(C, label="2021", X=x_pos - bar_width, Y=values1, weight=bar_width)
        
        with dcg.ThemeList(C) as theme2:
            dcg.ThemeColorImPlot(C, fill=(255, 165, 0))  # Orange
        dcg.PlotBars(C, label="2022", X=x_pos, Y=values2, weight=bar_width, theme=theme2)
        
        with dcg.ThemeList(C) as theme3:
            dcg.ThemeColorImPlot(C, fill=(50, 205, 50))  # Green
        dcg.PlotBars(C, label="2023", X=x_pos + bar_width, Y=values3, weight=bar_width, theme=theme3)
        
        # Configure axis
        plot.X1.no_gridlines = True
        plot.X1.labels = categories
        plot.X1.labels_coord = x_pos
        
        # Add labels
        plot.X1.label = "Category"
        plot.Y1.label = "Expense ($)"
    
    # Second method: Using PlotBarGroups for simpler implementation
    with dcg.Plot(C, label="Grouped Bars (Using PlotBarGroups)", height=300, width=-1) as plot:
        # Sample data in the format expected by PlotBarGroups
        # Data needs to be shaped as [n_series, n_categories]
        data = np.array([
            [83, 67, 23, 89, 83],  # Series 1 values for each category
            [80, 62, 56, 99, 55],  # Series 2 values for each category
            [80, 69, 52, 92, 72],  # Series 3 values for each category
        ])
        
        # Category labels
        categories = ["Cat A", "Cat B", "Cat C", "Cat D", "Cat E"]
        x_pos = np.arange(len(categories))
        
        # Series labels
        series_labels = ["Series 1", "Series 2", "Series 3"]
        
        # Create grouped bars
        dcg.PlotBarGroups(C,
                        values=data,
                        labels=series_labels,
                        group_size=0.7)  # Controls overall group width
        
        # Configure axis
        plot.X1.no_gridlines = True
        plot.X1.labels = categories
        plot.X1.labels_coord = x_pos
        plot.X1.no_initial_fit = True
        plot.X1.min = -0.5
        plot.X1.max = len(categories) - 0.5
        
        # Add labels
        plot.X1.label = "Categories"
        plot.Y1.label = "Values"
        
        dcg.Text(C, value="Note: PlotBarGroups requires less code and handles spacing automatically")

@demosection(dcg.Plot, dcg.PlotBarGroups)
@documented
@democode
def _stacked_bars(C: dcg.Context):
    """
    ### Stacked Bar Charts
    
    Stacked bar charts show the composition of each category, with segments representing 
    parts that make up the whole. They're excellent for visualizing part-to-whole relationships
    across different categories.
    
    This example shows how to create stacked bars using `PlotBarGroups` with `stacked=True`.
    """
    with dcg.Plot(C, label="Stacked Bar Chart", height=300, width=-1) as plot:
        # Sample data - each row is a component, each column is a category
        data = np.array([
            [12, 15, 8, 10, 7],    # Component 1 values for each category
            [8, 10, 12, 8, 6],     # Component 2 values for each category
            [5, 8, 10, 9, 12],     # Component 3 values for each category
        ])
        
        # Category labels
        categories = ["Project A", "Project B", "Project C", "Project D", "Project E"]
        x_pos = np.arange(len(categories))
        
        # Component labels
        component_labels = ["Development", "Testing", "Deployment"]
        
        # Create stacked bars
        dcg.PlotBarGroups(C,
                        values=data,
                        labels=component_labels,
                        group_size=0.7,
                        stacked=True)  # This is what makes it stacked!
        
        # Configure axis
        plot.X1.no_gridlines = True
        plot.X1.labels = categories
        plot.X1.labels_coord = x_pos
        plot.X1.no_initial_fit = True
        plot.X1.min = -0.5
        plot.X1.max = len(categories) - 0.5
        
        # Add labels
        plot.X1.label = "Projects"
        plot.Y1.label = "Hours"

@demosection(dcg.Plot, dcg.PlotBars, dcg.PlotBarGroups)
@documented
@democode
def _horizontal_bars(C: dcg.Context):
    """
    ### Horizontal Bar Charts
    
    Horizontal bar charts are especially useful when:
    - You have many categories to display
    - Category names are long
    - You want to emphasize the comparison between values rather than their absolute values
    
    Both `PlotBars` and `PlotBarGroups` support horizontal orientation.
    """
    with dcg.Plot(C, label="Horizontal Bar Chart", height=400, width=-1) as plot:
        # Sample data with longer category names
        categories = [
            "North America", 
            "Europe", 
            "Asia-Pacific", 
            "Latin America", 
            "Middle East & Africa"
        ]
        values = [42.5, 38.7, 45.2, 26.8, 22.1]
        
        # Y positions for horizontal bars (note: these become Y coordinates)
        positions = np.arange(len(categories))
        
        # Create horizontal bars by setting horizontal=True
        dcg.PlotBars(C, label="Market Share (%)", 
                   X=values, Y=positions,  # Note how X and Y are swapped in meaning
                   horizontal=True, weight=0.6)
        
        # Configure axes for horizontal orientation
        plot.Y1.no_gridlines = True
        plot.Y1.labels = categories
        plot.Y1.labels_coord = positions
        
        # Add labels (note X and Y are swapped in meaning)
        plot.X1.label = "Market Share (%)"
        # No Y label needed with category names
        
    # Horizontal grouped bars
    with dcg.Plot(C, label="Horizontal Grouped Bars", height=400, width=-1) as plot:
        # Sample data for multiple years
        data = np.array([
            [45, 60, 38, 72, 15],  # 2021
            [50, 55, 42, 68, 20],  # 2022
            [55, 50, 45, 65, 25],  # 2023
        ])
        
        # Categories
        categories = ["Product A", "Product B", "Product C", "Product D", "Product E"]
        y_pos = np.arange(len(categories))
        
        # Series labels
        series_labels = ["2021", "2022", "2023"]
        
        # Create horizontal grouped bars
        bar_groups = dcg.PlotBarGroups(C,
                                     values=data,
                                     labels=series_labels,
                                     group_size=0.7,
                                     horizontal=True)  # This makes it horizontal
        
        # Configure axes
        plot.Y1.no_gridlines = True
        plot.Y1.labels = categories
        plot.Y1.labels_coord = y_pos
        plot.Y1.no_initial_fit = True
        plot.Y1.min = -0.5
        plot.Y1.max = len(categories) - 0.5
        
        # Add labels
        plot.X1.label = "Sales Volume"
        # No Y label needed with category names

pop_group()  # End Bar Plots
push_group("Pie Charts")

@demosection(dcg.Plot, dcg.PlotPieChart)
@documented
@democode
def _pie_charts(C: dcg.Context):
    """
    ### Pie Charts
    
    Pie charts display data as proportional slices of a circle, making them ideal for showing
    the composition of a whole or the relative sizes of different parts.
    
    This section demonstrates:
    - Basic pie charts
    - Customizing pie chart appearance
    - Donut charts (pie charts with a hole)
    - Exploded pie segments
    """
    # Basic pie chart
    with dcg.Plot(C, label="Basic Pie Chart", height=350, width=350, no_mouse_pos=True) as plot:
        # Sample data
        values = [35, 25, 20, 15, 5]
        labels = ["Product A", "Product B", "Product C", "Product D", "Product E"]
        
        # Configure plot for pie chart (hide axes elements)
        plot.X1.no_gridlines = True
        plot.X1.no_tick_marks = True
        plot.X1.no_tick_labels = True
        plot.X1.no_initial_fit = True
        plot.X1.min = 0
        plot.X1.max = 1
        plot.Y1.no_gridlines = True
        plot.Y1.no_tick_marks = True
        plot.Y1.no_tick_labels = True
        plot.Y1.no_initial_fit = True
        plot.Y1.min = 0
        plot.Y1.max = 1
        
        # Create pie chart at center with normalized radius
        dcg.PlotPieChart(C, 
                       x=0.5,        # Center X
                       y=0.5,        # Center Y
                       radius=0.4,   # Radius (normalized to plot)
                       values=values,
                       labels=labels,
                       normalize=True,  # Automatically normalize values to percentages
                       label_format="%.1f%%")  # Display as percentages
        
        dcg.Text(C, value="Note: Pie charts are best for showing 5-7 categories at most")

@demosection(dcg.Plot, dcg.DrawInPlot, dcg.HorizontalLayout, dcg.DrawArc,
             dcg.DrawTriangle, dcg.DrawPolygon, dcg.DrawText)
@documented
@democode
def _advanced_pie_charts(C: dcg.Context):
    """
    ### Advanced Pie Charts
    
    Pie charts can be further customized with:
    - Exploded segments to highlight specific parts
    - Donut charts (pie charts with a center hole)
    - Custom colors for each segment
    - Different positioning and sizing
    
    These variations can enhance readability and highlight important data.
    """
    # Create a layout with two pie charts side by side
    with dcg.HorizontalLayout(C):
        # Left side: Exploded pie chart
        with dcg.Plot(C, label="Exploded Pie Chart", height=350, width="0.5*fillx", no_mouse_pos=True, equal_aspects=True) as plot2:
            # Sample data
            values = [40, 30, 20, 10]
            labels = ["Q1", "Q2", "Q3", "Q4"]
            
            # Explosion (offset) for each segment
            # The second segment (index 1) is "exploded"
            explosion = [0.0, 0.15, 0.0, 0.0]
            
            # Configure plot
            plot2.X1.no_gridlines = True
            plot2.X1.no_tick_marks = True
            plot2.X1.no_tick_labels = True
            plot2.X1.no_initial_fit = True
            plot2.X1.min = 0
            plot2.X1.max = 1
            plot2.Y1.no_gridlines = True
            plot2.Y1.no_tick_marks = True
            plot2.Y1.no_tick_labels = True
            plot2.Y1.no_initial_fit = True
            plot2.Y1.min = 0
            plot2.Y1.max = 1
            
            # Create exploded pie chart
            with dcg.DrawInPlot(C):
                # For exploded segments, we need to use DrawInPlot
                # and calculate segment positions manually
                
                # Define custom colors for segments
                colors = [
                    (65, 105, 225),   # Royal blue
                    (220, 20, 60),    # Crimson
                    (50, 205, 50),    # Lime green
                    (255, 165, 0)     # Orange
                ]
                
                # Calculate total for percentage
                total = sum(values)
                
                # Starting angle (in radians)
                angle_start = 0
                
                center_x, center_y = 0.5, 0.5
                radius = 0.4
                
                for i in range(len(values)):
                    # Calculate angle for this segment
                    angle_end = angle_start + 2 * np.pi * values[i] / total
                    
                    # Calculate center of segment for explosion
                    mid_angle = (angle_start + angle_end) / 2
                    explosion_x = center_x + explosion[i] * np.cos(mid_angle)
                    explosion_y = center_y + explosion[i] * np.sin(mid_angle)

                    # Draw the slice
                    dcg.DrawArc(C, center=(explosion_x, explosion_y),
                                radius=(radius, radius),
                                start_angle=angle_start,
                                end_angle=angle_end,
                                thickness=-1,
                                color=0,
                                fill=colors[i])
                    dcg.DrawTriangle(C,
                                    p1=(explosion_x, explosion_y),
                                    p2=(explosion_x + radius * np.cos(angle_start),
                                        explosion_y + radius * np.sin(angle_start)),
                                    p3=(explosion_x + radius * np.cos(angle_end),
                                        explosion_y + radius * np.sin(angle_end)),
                                    thickness=-1,
                                    color=colors[i],
                                    fill=colors[i])
                    
                    # Draw label
                    label_x = explosion_x + 0.7 * radius * np.cos(mid_angle)
                    label_y = explosion_y + 0.7 * radius * np.sin(mid_angle)
                    percentage = 100 * values[i] / total
                    
                    dcg.DrawText(C,
                               text=f"{labels[i]}: {percentage:.1f}%",
                               pos=(label_x, label_y),
                               color=(255, 255, 255))
                    
                    # Update starting angle for next segment
                    angle_start = angle_end

        # Right side: Donut chart
        with dcg.Plot(C, label="Donut Chart", height=350, width=-1, no_mouse_pos=True, equal_aspects=True) as plot1:
            # Sample data
            values = np.array([30, 25, 20, 15, 10])
            labels = ["A", "B", "C", "D", "E"]
            
            # Configure plot
            plot1.X1.no_gridlines = True
            plot1.X1.no_tick_marks = True
            plot1.X1.no_tick_labels = True
            plot1.X1.no_initial_fit = True
            plot1.X1.min = 0
            plot1.X1.max = 1
            plot1.Y1.no_gridlines = True
            plot1.Y1.no_tick_marks = True
            plot1.Y1.no_tick_labels = True
            plot1.Y1.no_initial_fit = True
            plot1.Y1.min = 0
            plot1.Y1.max = 1
            
            # Create donut chart using DrawInPlot and DrawPolygon
            with dcg.DrawInPlot(C):
                # Define custom colors for segments
                colors = [
                    (65, 105, 225),   # Royal blue
                    (220, 20, 60),    # Crimson
                    (50, 205, 50),    # Lime green
                    (255, 165, 0),    # Orange
                    (148, 0, 211)     # Dark violet
                ]
                
                # Calculate total for percentage
                total = values.sum()
                
                # Center and radius settings
                center_x, center_y = 0.5, 0.5
                outer_radius = 0.4
                inner_radius = 0.2  # This creates the "donut hole"
                
                # Starting angle (in radians)
                angle_start = 0
                
                for i in range(len(values)):
                    # Calculate angle for this segment
                    angle_end = angle_start + 2 * np.pi * values[i] / total
                    
                    # Generate points for slice (outer and inner arcs)
                    num_segments = max(20, int(50 * (angle_end - angle_start) / (2 * np.pi)))
                    angles = np.linspace(angle_start, angle_end, num_segments)
                    
                    # Create polygon vertices
                    vertices = []
                    
                    # Add outer arc points (going clockwise)
                    for angle in angles:
                        x = center_x + outer_radius * np.cos(angle)
                        y = center_y + outer_radius * np.sin(angle)
                        vertices.append((x, y))
                    
                    # Add inner arc points (going counter-clockwise)
                    for angle in reversed(angles):
                        x = center_x + inner_radius * np.cos(angle)
                        y = center_y + inner_radius * np.sin(angle)
                        vertices.append((x, y))
                    
                    # Draw the slice as a polygon
                    dcg.DrawPolygon(C,
                                  points=vertices,
                                  fill=colors[i % len(colors)],
                                  color=0)
                    
                    # Add label outside the donut
                    mid_angle = (angle_start + angle_end) / 2
                    label_radius = outer_radius + 0.05
                    label_x = center_x + label_radius * np.cos(mid_angle)
                    label_y = center_y + label_radius * np.sin(mid_angle)
                    
                    percentage = 100 * values[i] / total
                    label_text = f"{labels[i]}: {percentage:.1f}%"
                        
                    dcg.DrawText(C,
                               text=label_text,
                               pos=(label_x, label_y))
                    
                    # Update starting angle for next segment
                    angle_start = angle_end
                
                # Optional: Add a title in the center
                dcg.DrawText(C,
                           text="Annual\nRevenue",
                           pos=(center_x, center_y),
                           color=(250, 250, 250),
                           size=-20.0)

pop_group()  # End Pie Plots

push_group("Statistical Plots")

@demosection(dcg.Plot, dcg.PlotHistogram, dcg.PlotErrorBars, dcg.PlotStems, dcg.PlotHistogram2D, dcg.PlotHeatmap)
@documented
def _statistical_plots(C: dcg.Context):
    """
    ### Statistical Plots

    Statistical plots help visualize data distributions and uncertainty.
    
    This section demonstrates:
    - Error bars for showing data uncertainty
    - Histograms for frequency distributions
    - 2D histograms for bivariate distributions
    - Stem plots for discrete sequence data
    
    These visualization types are particularly useful for scientific and data analysis
    applications when you need to represent statistical properties of your data.
    """
    pass

@demosection(dcg.PlotBars, dcg.PlotErrorBars, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
@democode
def _error_bars(C: dcg.Context):
    """
    ### Error Bars
    
    Error bars indicate uncertainty in data points, showing a range of possible values.
    They are essential for scientific visualization and statistical analysis.
    
    #### Key features:
    - Add error bars to both bar charts and line plots
    - Specify asymmetric errors with separate positive/negative values
    - Customize appearance with themes
    
    This example shows error bars applied to both bar and line series.
    """
    with dcg.Plot(C, label="Error Bar Example", height=300, width=-1) as plot:
        # Sample data for bars with error
        bar_x = np.array([1, 2, 3, 4, 5])
        bar_y = np.array([2.5, 3.8, 4.2, 3.5, 5.1])
        # Error values (can be different for positive/negative direction)
        err_neg = np.array([0.3, 0.4, 0.2, 0.5, 0.3])
        err_pos = np.array([0.5, 0.3, 0.4, 0.6, 0.4])
        
        # Sample data for line with error
        line_x = np.array([1, 2, 3, 4, 5])
        line_y = np.array([6.5, 6.8, 7.2, 6.5, 7.1])
        line_err = np.array([0.3, 0.5, 0.4, 0.3, 0.5])  # Same error in both directions
        
        # Bar chart with error bars
        dcg.PlotBars(C, label="Data with Error", X=bar_x, Y=bar_y, weight=0.4)
        dcg.PlotErrorBars(C, X=bar_x, Y=bar_y, negatives=err_neg, positives=err_pos)
        
        # Line plot with symmetric error bars
        with dcg.ThemeList(C) as theme:
            dcg.ThemeColorImPlot(C, line=(220, 20, 60))  # Crimson line
            dcg.ThemeStyleImPlot(C, line_weight=2.0)
        dcg.PlotLine(C, label="Trend with Error", X=line_x, Y=line_y, theme=theme)
        
        # For symmetric errors, you can provide the same array to both negatives and positives
        dcg.PlotErrorBars(C, X=line_x, Y=line_y, negatives=line_err, positives=line_err)
        
        # Configure axes
        plot.X1.label = "Measurement"
        plot.Y1.label = "Value"
        
        dcg.Text(C, value="Error bars can be attached to any data series to show uncertainty")

@demosection(dcg.Plot, dcg.PlotHistogram, dcg.PlotHistogram2D, dcg.PlotHeatmap, dcg.Checkbox, dcg.Slider)
@documented
@democode
def _histogram(C: dcg.Context):
    """
    ### Histograms
    
    Histograms display the distribution of a dataset by grouping values
    into bins and showing the frequency of values in each bin.
    
    #### Key features:
    - Automatically determine optimal bin sizes
    - Control number of bins manually
    - Calculate density for probability distributions
    - Show cumulative distributions
    
    This example demonstrates a basic histogram with controls for density and cumulative options.
    """
    # Generate sample data
    np.random.seed(42)
    data = np.concatenate([
        np.random.normal(3, 1, 1000),   # Normal distribution centered at 3
        np.random.normal(7, 2, 500)     # Normal distribution centered at 7
    ])
    
    # Interactive controls
    with dcg.HorizontalLayout(C):
        density_cb = dcg.Checkbox(C, label="Density", value=False)
        cumulative_cb = dcg.Checkbox(C, label="Cumulative", value=False)
        bins_slider = dcg.Slider(C, label="Bins", width=200, 
                               min_value=5, max_value=100, value=20)
    
    with dcg.Plot(C, label="Histogram Plot", height=300, width=-1) as plot:
        # Create histogram series
        hist_series = dcg.PlotHistogram(C, 
                                      label="Distribution", 
                                      X=data,
                                      bins=int(bins_slider.value),
                                      density=density_cb.value,
                                      cumulative=cumulative_cb.value)
        
        # Configure axes
        plot.X1.label = "Value"
        plot.Y1.label = "Frequency" if not density_cb.value else "Density"
        plot.Y1.auto_fit = True
        
        # Set callback functions to update histogram when controls change
        def update_histogram(sender, target, data):
            hist_series.bins = int(bins_slider.value)
            hist_series.density = density_cb.value
            hist_series.cumulative = cumulative_cb.value
            plot.Y1.label = "Density" if density_cb.value else "Frequency"
            if cumulative_cb.value:
                plot.Y1.label += " (Cumulative)"
            C.viewport.wake()
        
        density_cb.callback = update_histogram
        cumulative_cb.callback = update_histogram
        bins_slider.callback = update_histogram
        
        dcg.Text(C, value="Histograms are useful for visualizing distributions and identifying patterns in data")

@demosection(dcg.Plot, dcg.PlotHistogram, dcg.PlotHistogram2D, dcg.PlotHeatmap)
@documented
@democode
def _histogram_2d(C: dcg.Context):
    """
    ### 2D Histograms
    
    2D histograms (also called heatmaps) show the joint distribution of two variables.
    They divide the plane into bins and count how many data points fall into each bin.
    
    #### Key features:
    - Visualize relationships between two variables
    - Identify clusters and patterns in bivariate data
    - Control bin resolution in both dimensions
    - Apply custom color scales
    
    This example demonstrates a 2D histogram of normally distributed data.
    """
    # Generate sample bivariate normal distribution
    np.random.seed(123)
    n_points = 5000
    
    # Create a bimodal distribution
    x1 = np.random.normal(-2, 1, n_points//2)
    y1 = np.random.normal(-2, 1, n_points//2)
    
    x2 = np.random.normal(2, 1, n_points//2)
    y2 = np.random.normal(2, 1, n_points//2)
    
    x = np.concatenate([x1, x2])
    y = np.concatenate([y1, y2])
    
    # Controls for bin count
    bin_slider = dcg.Slider(C, label="Bins", width=200, 
                          min_value=10, max_value=100, value=40)
    
    with dcg.Plot(C, label="2D Histogram", height=400, width=-1) as plot:
        # Create 2D histogram
        hist_2d = dcg.PlotHistogram2D(C, 
                                     label="Joint Distribution", 
                                     X=x, Y=y,
                                     x_bins=int(bin_slider.value),
                                     y_bins=int(bin_slider.value))
        
        # Configure axes
        plot.X1.label = "X Value"
        plot.Y1.label = "Y Value"
        
        # Set callback to update bin count
        def update_bins(sender, target, data):
            hist_2d.x_bins = data
            hist_2d.y_bins = data
            C.viewport.wake()
        
        bin_slider.callbacks = update_bins
        
        dcg.Text(C, value="2D histograms reveal patterns in bivariate data that might be missed in separate 1D histograms")

@demosection(dcg.Plot, dcg.PlotStems, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
@democode
def _stem_plots(C: dcg.Context):
    """
    ### Stem Plots
    
    Stem plots connect discrete data points to a baseline with vertical stems,
    emphasizing the individual values in a sequence.
    
    #### Key features:
    - Visualize discrete sequences
    - Emphasize the magnitude of individual data points
    - Customize stem and marker appearance
    - Great for impulse responses, discrete-time signals, and sequence data
    
    This example shows stem plots with different customizations.
    """
    with dcg.Plot(C, label="Stem Plot Example", height=300, width=-1) as plot:
        # Generate sample data
        x = np.linspace(0, 2*np.pi, 20)
        y_sin = 0.5 + 0.5 * np.sin(x)  # Sine wave
        y_cos = 0.5 + 0.75 * np.cos(x)  # Cosine wave
        
        # Basic stem plot
        dcg.PlotStems(C, label="sin(x)", X=x, Y=y_sin)
        
        # Customize stem appearance
        with dcg.ThemeList(C) as theme:
            dcg.ThemeColorImPlot(C, line=(0, 120, 0))  # Dark green
            dcg.ThemeStyleImPlot(C, 
                               marker=dcg.PlotMarker.DIAMOND,
                               marker_size=6,
                               line_weight=2.0)
        dcg.PlotStems(C, label="cos(x)", X=x, Y=y_cos, theme=theme)
        
        # Configure axes
        plot.X1.label = "X Axis"
        plot.Y1.label = "Y Axis"

pop_group()  # End Statistical Plots

push_group("Specialized Plots")

@demosection(dcg.Plot, dcg.PlotHeatmap, dcg.PlotDigital, dcg.utils.PlotCandleStick)
@documented
def _specialized_plots(C: dcg.Context):
    """
    ### Specialized Plots
    
    Beyond standard charts, DearCyGui offers specialized plot types
    for specific visualization needs.
    
    This section demonstrates:
    - Heatmaps for matrix data visualization
    - Digital plots for boolean/signal data
    - Infinite lines for reference marks
    - Financial charts for stock data
    
    These specialized visualization types address specific use cases
    that arise in various fields like engineering, finance, and data science.
    """
    pass

@demosection(dcg.Plot, dcg.PlotHeatmap, dcg.Checkbox)
@documented
@democode
def _heatmaps(C: dcg.Context):
    """
    ### Heatmaps
    
    Heatmaps visualize matrix data using color intensity to represent values.
    They're ideal for correlation matrices, geographical data, and any 2D grid of values.
    
    #### Key features:
    - Map numerical values to colors
    - Customize color scales
    - Control value range mapping
    - Display patterns in 2D data
    
    This example shows a basic heatmap with custom data.
    """
    # Create sample matrix data
    values = np.array([
        [0.8, 2.4, 2.5, 3.9, 0.0, 4.0, 0.0],
        [2.4, 0.0, 4.0, 1.0, 2.7, 0.0, 0.0],
        [1.1, 2.4, 0.8, 4.3, 1.9, 4.4, 0.0],
        [0.6, 0.0, 0.3, 0.0, 3.1, 0.0, 0.0],
        [0.7, 1.7, 0.6, 2.6, 2.2, 6.2, 0.0],
        [1.3, 1.2, 0.0, 0.0, 0.0, 3.2, 5.1],
        [0.1, 2.0, 0.0, 1.4, 0.0, 1.9, 6.3]
    ])
    
    # Create checkbox for column-major orientation
    col_major_cb = dcg.Checkbox(C, label="Column-major", value=False)
    
    with dcg.Plot(C, label="Heatmap Example", height=400, width=-1) as plot:
        # Configure plot for heatmap
        plot.X1.label = "X"
        plot.X1.no_gridlines = True
        plot.X1.no_tick_marks = True
        plot.X1.lock_min = True
        plot.X1.lock_max = True
        
        plot.Y1.label = "Y"
        plot.Y1.no_gridlines = True
        plot.Y1.no_tick_marks = True
        plot.Y1.lock_min = True
        plot.Y1.lock_max = True
        
        # Create heatmap with value scale
        heatmap = dcg.PlotHeatmap(C, 
                                 label="Matrix Data",
                                 values=values, 
                                 scale_min=0, 
                                 scale_max=values.max(),
                                 col_major=col_major_cb.value)
        
        # Callback to toggle column-major layout
        def toggle_col_major(sender, target, data):
            heatmap.col_major = data
            C.viewport.wake()
            
        col_major_cb.callback = toggle_col_major
        
        dcg.Text(C, value="Heatmaps are useful for visualizing patterns in matrix data")
        dcg.Text(C, value="Applications include: correlation matrices, geographical data, image processing")

@demosection(dcg.Plot, dcg.PlotInfLines, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
@democode
def _infinite_lines(C: dcg.Context):
    """
    ### Infinite Lines
    
    Infinite lines extend across the entire plot area, useful for references,
    thresholds, or marking specific positions.
    
    #### Key features:
    - Create vertical or horizontal reference lines
    - Mark important thresholds or boundaries
    - Customize line appearance with styles and colors
    
    This example demonstrates using infinite lines as references.
    """
    with dcg.Plot(C, label="Infinite Lines Example", height=300, width=-1) as plot:
        # Sample data for context
        x = np.linspace(0, 10, 100)
        y = np.sin(x) * np.exp(-0.2 * x)
        
        # Plot main data series
        dcg.PlotLine(C, label="Signal", X=x, Y=y)
        
        # Add vertical infinite lines at specific x positions
        vert_positions = [2, 4, 6, 8]
        with dcg.ThemeList(C) as v_theme:
            dcg.ThemeColorImPlot(C, line=(255, 0, 0, 100))  # Transparent red
            dcg.ThemeStyleImPlot(C, line_weight=1.0)
        dcg.PlotInfLines(C, 
                       label="Vertical Refs", 
                       X=vert_positions, 
                       theme=v_theme)
        
        # Add horizontal infinite lines at specific y positions
        horz_positions = [0, 0.5, -0.5]
        with dcg.ThemeList(C) as h_theme:
            dcg.ThemeColorImPlot(C, line=(0, 0, 255, 100))  # Transparent blue
            dcg.ThemeStyleImPlot(C, line_weight=1.0)
        dcg.PlotInfLines(C, 
                       label="Horizontal Refs", 
                       X=horz_positions, 
                       horizontal=True, 
                       theme=h_theme)
        
        # Configure axes
        plot.X1.label = "X Axis"
        plot.Y1.label = "Y Axis"
        
        dcg.Text(C, value="Infinite lines are useful for marking reference values, thresholds, or important positions")

@demosection(dcg.Plot, dcg.PlotDigital, dcg.PlotLine, dcg.RenderHandler)
@documented
@democode
def _digital_plots(C: dcg.Context):
    """
    ### Digital Plots
    
    Digital plots visualize binary or discrete signals that switch between states,
    making them ideal for digital logic, square waves, or binary signals.
    
    #### Key features:
    - Display signals with discrete states (typically 0 and 1)
    - Automatically create vertical transitions between states
    - Overlay with analog signals for comparison
    - Digital plot Y-axis is fixed and not affected by zooming/panning
    
    This example shows digital signals alongside analog signals.
    """
    with dcg.Plot(C, label="Digital Plot Example", height=300, width=-1) as plot:
        # Initial settings
        t_start = -10
        t_end = 0
        
        plot.X1.label = "Time"
        plot.X1.min = t_start
        plot.X1.max = t_end
        plot.X1.lock_min = True
        plot.X1.lock_max = True
        
        plot.Y1.label = "Signal"
        plot.Y1.min = -1.5
        plot.Y1.max = 1.5
        
        # Create digital series
        digital_0 = dcg.PlotDigital(C, label="Digital Signal 1")
        digital_1 = dcg.PlotDigital(C, label="Digital Signal 2")
        
        # Create analog series for comparison
        analog_0 = dcg.PlotLine(C, label="Analog Signal 1")
        analog_1 = dcg.PlotLine(C, label="Analog Signal 2")
        
        # Generate initial data points
        t_points = np.linspace(t_start, t_end, 200)
        digital_0.X = t_points
        digital_0.Y = (np.sin(t_points) > 0.3).astype(float)
        
        digital_1.X = t_points
        digital_1.Y = (np.sin(t_points) < -0.3).astype(float)
        
        analog_0.X = t_points
        analog_0.Y = np.sin(t_points)
        
        analog_1.X = t_points
        analog_1.Y = np.cos(t_points)
        
        # Live update function
        def update_plot():
            # Get current time data
            t = plot.user_data
            if t is None:
                t = 0
            
            # Advance time
            t += C.viewport.metrics.delta_whole_frame
            
            # Update visible range
            plot.X1.min = t - 10
            plot.X1.max = t
            
            # Add new data points
            new_t = t
            new_digital_0 = 1.0 if np.sin(new_t) > 0.3 else 0.0
            new_digital_1 = 1.0 if np.sin(new_t) < -0.3 else 0.0
            
            # Append data
            digital_0.X = np.append(digital_0.X, new_t)
            digital_0.Y = np.append(digital_0.Y, new_digital_0)
            
            digital_1.X = np.append(digital_1.X, new_t)
            digital_1.Y = np.append(digital_1.Y, new_digital_1)
            
            analog_0.X = np.append(analog_0.X, new_t)
            analog_0.Y = np.append(analog_0.Y, np.sin(new_t))
            
            analog_1.X = np.append(analog_1.X, new_t)
            analog_1.Y = np.append(analog_1.Y, np.cos(new_t))
            
            # Trim old data (optional, to prevent arrays from growing too large)
            if len(digital_0.X) > 1000:
                digital_0.X = digital_0.X[-1000:]
                digital_0.Y = digital_0.Y[-1000:]
                digital_1.X = digital_1.X[-1000:]
                digital_1.Y = digital_1.Y[-1000:]
                analog_0.X = analog_0.X[-1000:]
                analog_0.Y = analog_0.Y[-1000:]
                analog_1.X = analog_1.X[-1000:]
                analog_1.Y = analog_1.Y[-1000:]
            
            # Update stored time
            plot.user_data = t
            C.viewport.wake()
        
        # Register render handler to update plot
        plot.handlers = [dcg.RenderHandler(C, callback=update_plot)]
        
        dcg.Text(C, value="Digital plots are useful for visualizing binary signals, logic states, or thresholds")
        dcg.Text(C, value="Note: Digital plots don't respond to Y-axis zooming, allowing overlaid analog plots")

@demosection(dcg.Plot, dcg.utils.PlotCandleStick)
@documented
@democode
def _financial_charts(C: dcg.Context):
    """
    ### Financial Charts
    
    Financial charts are specialized visualizations for market data,
    with candlestick charts being the most common for showing price movements.
    
    #### Key features:
    - Display open, high, low, and close prices
    - Color-code price movements (typically green for up, red for down)
    - Integrate with time axis for chronological display
    - Customizable candlestick appearance
    
    This example demonstrates a basic candlestick chart for stock prices.
    """
    # Sample stock price data (1 month of daily prices)
    # Format: dates are UNIX timestamps, prices are in dollars
    dates = np.array([  # Timestamps for dates
        1609459200, 1609545600, 1609632000, 1609718400, 1609804800,
        1609891200, 1609977600, 1610064000, 1610150400, 1610236800,
        1610323200, 1610409600, 1610496000, 1610582400, 1610668800,
        1610755200, 1610841600, 1610928000, 1611014400, 1611100800,
        1611187200, 1611273600, 1611360000, 1611446400, 1611532800,
        1611619200, 1611705600, 1611792000, 1611878400, 1611964800
    ])
    
    # Generate somewhat realistic stock data
    np.random.seed(42)
    base_price = 150.0
    volatility = 0.02
    
    # Start with random changes
    changes = np.random.normal(0.001, volatility, len(dates))
    # Add a slight upward trend
    changes += 0.002
    
    # Generate OHLC data from changes
    closes = np.zeros(len(dates))
    closes[0] = base_price
    for i in range(1, len(dates)):
        closes[i] = closes[i-1] * (1 + changes[i])
    
    # Generate open, high, low based on close
    opens = np.zeros(len(dates))
    highs = np.zeros(len(dates))
    lows = np.zeros(len(dates))
    
    for i in range(len(dates)):
        if i == 0:
            opens[i] = base_price * (1 - volatility/2)
        else:
            opens[i] = closes[i-1] * (1 + np.random.normal(0, volatility/2))
        
        # High is the highest of open/close plus some random amount
        highs[i] = max(opens[i], closes[i]) * (1 + abs(np.random.normal(0, volatility)))
        
        # Low is the lowest of open/close minus some random amount
        lows[i] = min(opens[i], closes[i]) * (1 - abs(np.random.normal(0, volatility)))
    
    with dcg.Plot(C, label="Candlestick Chart", height=400, width=-1) as plot:
        # Configure plot for time series
        plot.X1.label = "Date"
        plot.X1.scale = dcg.AxisScale.TIME
        plot.Y1.label = "Price ($)"
        
        # Use DearCyGui's utility function for candlestick charts
        dcg.utils.PlotCandleStick(C,
                                dates=dates,
                                opens=opens,
                                closes=closes,
                                lows=lows,
                                highs=highs,
                                label="Stock Price",
                                time_formatter=lambda x: datetime.datetime.fromtimestamp(x).strftime("%b %d"))
        
        dcg.Text(C, value="Candlestick charts show open, high, low, and close prices for financial instruments")
        dcg.Text(C, value="Green candles indicate price increases, while red candles indicate decreases")

pop_group()  # End Specialized Plots

pop_group()  # End Basic Plots




push_group("Axes")

@demosection(dcg.Plot, dcg.PlotAxisConfig, dcg.AxisScale, dcg.AxisTag)
@documented
def _axes_overview(C: dcg.Context):
    """
    ## Working with Axes in DearCyGui

    Axes are fundamental components of plots, providing the coordinate system for data visualization.
    DearCyGui offers extensive customization options for axes, allowing precise control over their
    appearance and behavior.

    ### Available Axis Properties

    #### Basic Configuration
    - `label`: Axis title text
    - `min`/`max`: Define the visible range of the axis
    - `enabled`: Whether the axis is visible and active 
    - `scale`: Axis scale type (linear, logarithmic, time, symmetric log)
    - `invert`: Reverse the direction of the axis
    - `opposite`: Place the axis on the opposite side of the plot

    #### Visual Styling
    - `no_gridlines`: Hide gridlines
    - `foreground_grid`: Show gridlines in front of data
    - `no_tick_marks`: Hide tick marks
    - `no_tick_labels`: Hide tick labels 
    - `no_initial_fit`: Prevent automatic fitting to data
    - `no_highlight`: Disable highlighting when hovered
    - `no_label`: Hide the axis label

    #### Fit and Zoom Behavior
    - `auto_fit`: Continuously fit axis to visible data
    - `lock_min`/`lock_max`: Prevent min/max values from changing during zooming/panning
    - `zoom_min`/`zoom_max`: Set limits for how far users can zoom in/out
    - `constraint_min`/`constraint_max`: Constrain the axis range
    - `pan_stretch`: Allow stretching when panning in locked state
    - `restrict_fit_to_range`: Only fit to data within the visible region

    **Note**: If `no_initial_fit` is not set, by default the axis will fit to the
        displayed data the first time it is drawn.
        This also works with `DrawInPlot` element. You can
        manually call the `fit()` method to adjust the axis to the current data at
        next refresh.
        This is useful when you want to control the axis limits programmatically.
        e.g.: `plot.X1.fit()`

    #### Advanced Features
    - `labels`: Custom tick labels (text)
    - `labels_coord`: Positions for custom labels
    - `keep_default_ticks`: Keep default ticks when using custom labels
    - `tick_format`: Format string for axis values

    ### Supported Axis Types
    
    DearCyGui plots support up to three X axes and three Y axes:
    - `X1`, `Y1`: Primary axes (enabled by default)
    - `X2`, `Y2`: Secondary axes
    - `X3`, `Y3`: Tertiary axes

    To use secondary or tertiary axes, you must explicitly enable them:
    ```python
    plot.X2.enabled = True
    plot.Y2.enabled = True
    ```

    Finally if you want to constrain the X and Y axes to have the
    same step size, you can set the plot's `equal_aspects` property to `True`.

    The following sections demonstrate these features with practical examples.
    """
    pass

@demosection(dcg.Plot, dcg.PlotAxisConfig, dcg.AxisScale, dcg.AxisTag, dcg.AxesResizeHandler, dcg.PlotLine, dcg.TreeNode)
@documented
@democode
def _basic_axes_customization(C: dcg.Context):
    """
    ### Basic Axes Customization
    
    This example demonstrates the fundamental customization options for axes:
    
    - Adding labels to axes
    - Setting axis limits (min/max values)
    - Controlling tick marks and gridlines
    - Formatting tick labels
    
    These basic options allow you to create well-labeled, readable plots
    with appropriate scales for your data.
    """
    with dcg.Plot(C, label="Basic Axes Customization", height=300,
                  width="0.5*fillx", no_newline=True) as plot:
        # Generate some sample data
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        
        # Plot the data
        dcg.PlotLine(C, label="sin(x)", X=x, Y=y)
        
        # Configure X axis
        plot.X1.label = "X Axis Label"  # Set axis label
        plot.X1.min = 0                # Set minimum value
        plot.X1.max = 10               # Set maximum value
        
        # Configure Y axis
        plot.Y1.label = "Y Axis Label"  # Set axis label
        plot.Y1.min = -1.2             # Set minimum value
        plot.Y1.max = 1.2              # Set maximum value
        
    # Create controls for axis customization
    with dcg.ChildWindow(C, width=-1, auto_resize_y=True):
        with dcg.TreeNode(C, label="X Axis Controls", value=True):
            x_min_slider = dcg.Slider(C, label="X Min", min_value=0, max_value=5, value=0)
            x_max_slider = dcg.Slider(C, label="X Max", min_value=5, max_value=10, value=10)
            x_gridlines = dcg.Checkbox(C, label="Show Gridlines", value=True)
            x_ticks = dcg.Checkbox(C, label="Show Tick Marks", value=True)
            x_labels = dcg.Checkbox(C, label="Show Tick Labels", value=True)
            
        with dcg.TreeNode(C, label="Y Axis Controls", value=True):
            y_min_slider = dcg.Slider(C, label="Y Min", min_value=-2, max_value=0, value=-1.2)
            y_max_slider = dcg.Slider(C, label="Y Max", min_value=0, max_value=2, value=1.2)
            y_gridlines = dcg.Checkbox(C, label="Show Gridlines", value=True)
            y_ticks = dcg.Checkbox(C, label="Show Tick Marks", value=True)
            y_labels = dcg.Checkbox(C, label="Show Tick Labels", value=True)
            
        # Connect controls to axis properties
        x_min_slider.callback = lambda s, t, d: plot.X1.configure(min=d)
        x_max_slider.callback = lambda s, t, d: plot.X1.configure(max=d)
        x_gridlines.callback = lambda s, t, d: plot.X1.configure(no_gridlines=not d)
        x_ticks.callback = lambda s, t, d: plot.X1.configure(no_tick_marks=not d)
        x_labels.callback = lambda s, t, d: plot.X1.configure(no_tick_labels=not d)
            
        y_min_slider.callback = lambda s, t, d: plot.Y1.configure(min=d)
        y_max_slider.callback = lambda s, t, d: plot.Y1.configure(max=d)
        y_gridlines.callback = lambda s, t, d: plot.Y1.configure(no_gridlines=not d)
        y_ticks.callback = lambda s, t, d: plot.Y1.configure(no_tick_marks=not d)
        y_labels.callback = lambda s, t, d: plot.Y1.configure(no_tick_labels=not d)

    def on_plot_interaction(sender, target, data):
        ((x_min, x_max, x_scale), (y_min, y_max, y_scale)) = data
        # Update slider values limits based on interaction
        x_min_slider.value = x_min
        x_max_slider.value = x_max
        y_min_slider.value = y_min
        y_max_slider.value = y_max
        C.viewport.wake()
    plot.handlers = [dcg.AxesResizeHandler(C, callback=on_plot_interaction)]

@demosection(dcg.Plot, dcg.PlotAxisConfig, dcg.AxisScale, dcg.AxisTag, dcg.PlotLine)
@documented
@democode
def _axis_scales(C: dcg.Context):
    """
    ### Axis Scales
    
    DearCyGui supports different types of axis scales to accommodate various data types:
    
    - **Linear scale**: Standard linear scaling (default)
    - **Logarithmic scale**: Useful for data that spans multiple orders of magnitude
    - **Symmetric logarithmic scale**: Handles both positive and negative values with logarithmic scaling
    - **Time scale**: Specialized for time series data (covered in a separate example)
    
    This example demonstrates how to use different scales and when they're appropriate.
    """
    # Create radio button for scale selection
    scale_options = dcg.RadioButton(C, items=["Linear", "Log10", "Symmetric Log"], horizontal=True)

    with dcg.Plot(C, label="Axis Scales", height=400, width=-1) as plot:
        # Generate sample data that works well with different scales
        x_linear = np.linspace(0, 10, 100)
        y_linear = x_linear * np.sin(x_linear)
        
        x_log = np.logspace(-1, 3, 100)  # 0.1 to 1000
        y_log = np.sqrt(x_log)
        
        x_symlog = np.linspace(-100, 100, 200)
        y_symlog = np.sign(x_symlog) * np.log10(1 + np.abs(x_symlog))
        
        # Plot the appropriate dataset based on the current scale
        plot_data = dcg.PlotLine(C, label="Data", X=x_linear, Y=y_linear)
        
        # Set X axis limits and label
        plot.X1.label = "X (Linear Scale)"
        
        # Set Y axis limits and label
        plot.Y1.label = "Y"
        
        # Function to update the plot based on the selected scale
        def update_scale(sender, target, selected_scale):
            if selected_scale == "Linear":
                # Linear scale
                plot.X1.scale = dcg.AxisScale.LINEAR
                plot.X1.label = "X (Linear Scale)"
                plot_data.configure(X=x_linear, Y=y_linear)
                plot.X1.min = 0
                plot.X1.max = 10
                plot.Y1.min = -10
                plot.Y1.max = 10
            
            elif selected_scale == "Log10":
                # Logarithmic scale
                plot.X1.scale = dcg.AxisScale.LOG10
                plot.X1.label = "X (Log10 Scale)"
                plot_data.configure(X=x_log, Y=y_log)
                plot.X1.min = 0.1
                plot.X1.max = 1000
                plot.Y1.min = 0
                plot.Y1.max = 35
            
            elif selected_scale == "Symmetric Log":
                # Symmetric logarithmic scale
                plot.X1.scale = dcg.AxisScale.SYMLOG
                plot.X1.label = "X (Symmetric Log Scale)"
                plot_data.configure(X=x_symlog, Y=y_symlog)
                plot.X1.min = -100
                plot.X1.max = 100
                plot.Y1.min = -3
                plot.Y1.max = 3
            C.viewport.wake()
                
        # Connect the callback
        scale_options.callback = update_scale
        
        # Add explanatory text
        dcg.Text(C, value="Linear scale: Best for most datasets where values change proportionally")
        dcg.Text(C, value="Log10 scale: Ideal for data spanning multiple orders of magnitude")
        dcg.Text(C, value="Symmetric Log: Useful for data with both positive and negative values that need log scaling")

@demosection(dcg.Plot, dcg.PlotAxisConfig, dcg.AxisScale, dcg.AxisTag, dcg.PlotLine, dcg.PlotAnnotation)
@documented
@democode
def _time_axis_formatting(C: dcg.Context):
    """
    ### Time Axis Configuration
    
    Time series data is common in visualization, and DearCyGui provides specialized 
    support for time-based axes with automatic date formatting.
    
    Key aspects of time axis configuration:
    
    - Time is represented as UNIX timestamps (seconds since January 1, 1970)
    - Set `scale = dcg.AxisScale.TIME` to enable time axis formatting
    - Control date/time display with `use_local_time`, `use_ISO8601`, and `use_24hour_clock`
    - Provide custom formatters with the `time_formatter` parameter
    
    This example demonstrates various time axis formatting options.
    """
    # Generate time series data
    now = int(time.time())  # Current time in seconds since epoch
    days_back = 365  # Show one year of data
    
    # Create timestamps at daily intervals going back from now
    timestamps = np.array([now - 86400 * i for i in range(days_back, 0, -1)])
    
    # Create some synthetic data
    values = np.cumsum(np.random.normal(0, 1, len(timestamps)))
    values = values + 100  # Offset to make values positive
    
    # Create controls for time formatting
    with dcg.HorizontalLayout(C):
        use_local = dcg.Checkbox(C, label="Use Local Time", value=True)
        use_iso = dcg.Checkbox(C, label="Use ISO8601", value=False)
        use_24h = dcg.Checkbox(C, label="Use 24-hour Clock", value=False)
    
    time_range = dcg.Combo(C, items=["Full Year", "Last 30 Days", "Last 7 Days"], 
                            label="Time Range", value="Full Year")
    
    with dcg.Plot(C, label="Time Axis Formatting", height=350, width=-1,
                  use_local_time=True) as plot:
        # Configure plot for time series
        plot.X1.label = "Date"
        plot.X1.scale = dcg.AxisScale.TIME
        plot.Y1.label = "Value"
        
        # Add the time series data
        dcg.PlotLine(C, label="Time Series Data", X=timestamps, Y=values)
        
        # Function to update time range
        def update_time_range(sender, target, range_option):
            if range_option == "Full Year":
                plot.X1.min = timestamps[0]
                plot.X1.max = timestamps[-1]
            elif range_option == "Last 30 Days":
                plot.X1.min = now - 86400 * 30
                plot.X1.max = now
            elif range_option == "Last 7 Days":
                plot.X1.min = now - 86400 * 7
                plot.X1.max = now
            C.viewport.wake()
        
        # Connect controls to plot properties
        use_local.callback = lambda s, t, d: plot.configure(use_local_time=d)
        use_iso.callback = lambda s, t, d: plot.configure(use_ISO8601=d)
        use_24h.callback = lambda s, t, d: plot.configure(use_24hour_clock=d)
        time_range.callback = update_time_range
        
        # Add annotations to mark specific dates
        month_ago = now - 86400 * 30
        week_ago = now - 86400 * 7
        
        dcg.PlotAnnotation(C, text="1 Month Ago", x=month_ago, y=values[30], 
                          clamp=True, bg_color=(255, 200, 0, 100))
        dcg.PlotAnnotation(C, text="1 Week Ago", x=week_ago, y=values[7], 
                          clamp=True, bg_color=(0, 200, 255, 100))
        
    # Add explanation text
    dcg.Text(C, value="Note: Time axes use UNIX timestamps (seconds since January 1, 1970 UTC)")
    dcg.Text(C, value="Try different time ranges and formatting options to see how they affect the display")

@demosection(dcg.Plot, dcg.PlotAxisConfig, dcg.TreeNode, dcg.Checkbox)
@documented
@democode
def _multiple_axes(C: dcg.Context):
    """
    ### Using Multiple Axes
    
    DearCyGui supports up to three X and Y axes for a single plot, enabling you to:
    
    - Display data in different scales or units
    - Compare datasets with widely varying ranges
    - Create complex visualizations with multiple data series
    
    This example shows how to enable and configure multiple axes, and how to
    assign plot elements to specific axes.
    """
    # Create sample data with different scales
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)                     # Range: -1 to 1
    y2 = 100 * np.cos(x) + 100         # Range: 0 to 200
    y3 = np.exp(x / 3) / 100           # Range: exponential growth
    
    with dcg.Plot(C, label="Multiple Axes Example", height=350, width=-1) as plot:
        # Configure primary axes (X1, Y1)
        plot.X1.label = "X Axis"
        plot.Y1.label = "sin(x) [-1 to 1]"
        
        # Configure and enable secondary Y axis (Y2)
        plot.Y2.enabled = True
        plot.Y2.label = "cos(x) [0 to 200]"
        plot.Y2.opposite = True  # Place on right side
        
        # Configure and enable tertiary Y axis (Y3)
        plot.Y3.enabled = True
        plot.Y3.label = "exp(x/3)"
        plot.Y3.opposite = False  # Place on left side
        
        # Add data series, assigning each to the appropriate axis
        # Note: X1 is the default X axis for all series
        dcg.PlotLine(C, label="sin(x) on Y1", X=x, Y=y1)
        
        # For Y2 and Y3, we need to specify the axis
        dcg.PlotLine(C,
                     label="cos(x) on Y2",
                     X=x,
                     Y=y2,
                     axes=(dcg.Axis.X1, dcg.Axis.Y2),
                     theme=dcg.ThemeColorImPlot(C, line=(255, 0, 0)))

        dcg.PlotLine(C,
                     label="exp(x) on Y3",
                     X=x,
                     Y=y3,
                     axes=(dcg.Axis.X1, dcg.Axis.Y3),
                     theme=dcg.ThemeColorImPlot(C, line=(0, 200, 0)))
        
    # Create controls to toggle axis visibility
    with dcg.TreeNode(C, label="Axis Controls", value=True):
        y1_visible = dcg.Checkbox(C, label="Show Y1 (sin)", value=True)
        y2_visible = dcg.Checkbox(C, label="Show Y2 (cos)", value=True)
        y3_visible = dcg.Checkbox(C, label="Show Y3 (exp)", value=True)
    
    # Connect controls to axis properties
    y1_visible.callback = lambda s, t, d: plot.Y1.configure(enabled=d)
    y2_visible.callback = lambda s, t, d: plot.Y2.configure(enabled=d)
    y3_visible.callback = lambda s, t, d: plot.Y3.configure(enabled=d)
    
    # Add explanation
    dcg.Text(C, value="This example demonstrates using multiple Y axes to display data with different scales.")
    dcg.Text(C, value="Each series is associated with a specific axis, allowing for clear comparison.")
    dcg.Text(C, value="Toggle the checkboxes to show/hide individual axes.")

@demosection(dcg.Plot, dcg.PlotAxisConfig, dcg.PlotInfLines, dcg.TreeNode, dcg.Checkbox)
@documented
@democode
def _axis_orientation(C: dcg.Context):
    """
    ### Axis Orientation Options
    
    DearCyGui provides multiple ways to control axis orientation:
    
    - **opposite**: Places the axis on the opposite side of the plot
      (right instead of left for Y, top instead of bottom for X)
    - **invert**: Reverses the direction of the axis (high to low instead of low to high)
    
    These options allow you to create various plot styles and adapt to different
    data visualization conventions.
    """
    # Create sample data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    with dcg.Plot(C, label="Axis Orientation", height=350, width="0.5*fillx", no_newline=True) as plot:
        # Add data
        dcg.PlotLine(C, label="sin(x)", X=x, Y=y)
        
        # Configure default axes
        plot.X1.label = "X Axis"
        plot.Y1.label = "Y Axis"

    # Add controls for axis orientation
    with dcg.ChildWindow(C, width=-1, auto_resize_y=True):
        with dcg.TreeNode(C, label="X Axis Orientation", value=True):
            x_opposite = dcg.Checkbox(C, label="X at Top (Opposite)", value=False)
            x_invert = dcg.Checkbox(C, label="Invert X Direction", value=False)
        
        with dcg.TreeNode(C, label="Y Axis Orientation", value=True):
            y_opposite = dcg.Checkbox(C, label="Y at Right (Opposite)", value=False)
            y_invert = dcg.Checkbox(C, label="Invert Y Direction", value=False)
    
    # Connect controls to axis properties
    x_opposite.callback = lambda s, t, d: plot.X1.configure(opposite=d)
    x_invert.callback = lambda s, t, d: plot.X1.configure(invert=d)
    
    y_opposite.callback = lambda s, t, d: plot.Y1.configure(opposite=d)
    y_invert.callback = lambda s, t, d: plot.Y1.configure(invert=d)
    
    # Add reference lines to make the orientation changes more obvious
    theme = dcg.ThemeColorImPlot(C, line=(150, 150, 150, 100))
    dcg.PlotInfLines(C, X=[5], label="X Center", horizontal=False, theme=theme)
    dcg.PlotInfLines(C, X=[0], label="Y Center", horizontal=True, theme=theme)
    
    # Add explanations
    dcg.Text(C, value="Flip axes to accommodate different plotting conventions or to match specific data needs.")
    dcg.Text(C, value="The 'opposite' option moves axes to the opposite side of the plot.")
    dcg.Text(C, value="The 'invert' option reverses the direction of increasing values.")
    dcg.Text(C, value="Try combinations of these options to see their effects!")

@demosection(dcg.Plot, dcg.PlotAxisConfig, dcg.PlotLine, dcg.ChildWindow, dcg.TreeNode, dcg.Checkbox)
@documented
@democode
def _axis_constraints_locking(C: dcg.Context):
    """
    ### Axis Constraints and Locking
    
    DearCyGui provides several ways to control how axes can be manipulated:
    
    - **lock_min/lock_max**: Prevent users from changing minimum or maximum bounds
    - **constraint_min/constraint_max**: Enforce limits on axis range values
    - **zoom_min/zoom_max**: Control minimum and maximum zoom extents
    - **pan_stretch**: Allow stretching locked axes during panning
    
    These features help maintain appropriate bounds for your data and
    control the user's navigation experience.
    """
    # Create sample data
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    with dcg.Plot(C, label="Axis Constraints and Locking", height=350, width="0.5*fillx", no_newline=True) as plot:
        # Plot data
        dcg.PlotLine(C, label="sin(x)", X=x, Y=y)
        
        # Initial axis configuration
        plot.X1.label = "X Axis"
        plot.X1.min = 0
        plot.X1.max = 10
        
        plot.Y1.label = "Y Axis"
        plot.Y1.min = -1
        plot.Y1.max = 1

    with dcg.ChildWindow(C, width=-1, auto_resize_y=True):
        # Controls for X axis constraints
        with dcg.TreeNode(C, label="X Axis Controls", value=True):
            x_lock_min = dcg.Checkbox(C, label="Lock X Min", value=False)
            x_lock_max = dcg.Checkbox(C, label="Lock X Max", value=False)
            x_constraint_min = dcg.Slider(C, label="X Constraint Min", min_value=-5, max_value=5, value=0)
            x_constraint_max = dcg.Slider(C, label="X Constraint Max", min_value=5, max_value=15, value=10)
            x_pan_stretch = dcg.Checkbox(C, label="X Pan Stretch", value=False)
        
        # Controls for Y axis constraints
        with dcg.TreeNode(C, label="Y Axis Controls", value=True):
            y_lock_min = dcg.Checkbox(C, label="Lock Y Min", value=False)
            y_lock_max = dcg.Checkbox(C, label="Lock Y Max", value=False)
            y_constraint_min = dcg.Slider(C, label="Y Constraint Min", min_value=-2, max_value=0, value=-1)
            y_constraint_max = dcg.Slider(C, label="Y Constraint Max", min_value=0, max_value=2, value=1)
            y_pan_stretch = dcg.Checkbox(C, label="Y Pan Stretch", value=False)
    
    # Connect controls to axis properties
    x_lock_min.callback = lambda s, t, d: plot.X1.configure(lock_min=d)
    x_lock_max.callback = lambda s, t, d: plot.X1.configure(lock_max=d)
    x_constraint_min.callback = lambda s, t, d: plot.X1.configure(constraint_min=d)
    x_constraint_max.callback = lambda s, t, d: plot.X1.configure(constraint_max=d)
    x_pan_stretch.callback = lambda s, t, d: plot.X1.configure(pan_stretch=d)
    
    y_lock_min.callback = lambda s, t, d: plot.Y1.configure(lock_min=d)
    y_lock_max.callback = lambda s, t, d: plot.Y1.configure(lock_max=d)
    y_constraint_min.callback = lambda s, t, d: plot.Y1.configure(constraint_min=d)
    y_constraint_max.callback = lambda s, t, d: plot.Y1.configure(constraint_max=d)
    y_pan_stretch.callback = lambda s, t, d: plot.Y1.configure(pan_stretch=d)
    
    # Add instructions and explanations
    dcg.Text(C, value="Try panning and zooming the plot with different constraint settings.")
    dcg.Text(C, value="Lock Min/Max: Prevents that bound from changing during zoom/pan operations")
    dcg.Text(C, value="Constraint Min/Max: Sets a limit beyond which the axis cannot be set")
    dcg.Text(C, value="Pan Stretch: When locked, allows the axis to stretch when panning")

@demosection(dcg.Plot, dcg.PlotAxisConfig, dcg.PlotLine, dcg.PlotBars, dcg.Checkbox, dcg.Combo)
@documented
@democode
def _axis_custom_ticks_labels(C: dcg.Context):
    """
    ### Custom Axis Ticks and Labels
    
    DearCyGui allows you to customize the tick marks and labels on axes:
    
    - Define custom label text for specific positions
    - Control label formatting with format strings
    - Option to keep default ticks alongside custom labels
    
    These features are useful for categorical data, custom scales, or
    when you need precise control over how values are displayed.
    """
    # Create sample data
    categories = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    x_positions = np.arange(len(categories))
    y_values = [5, 8, 12, 18, 23, 27, 28, 26, 22, 16, 10, 6]  # Temperature data
    
    with dcg.Plot(C, label="Custom Axis Labels", height=350, width=-1) as plot:
        # Plot the data
        dcg.PlotBars(C, label="Average Temperature", X=x_positions, Y=y_values, weight=0.7)
        
        # Configure X axis with custom labels
        plot.X1.label = "Month"
        plot.X1.labels = categories
        plot.X1.labels_coord = x_positions
        plot.X1.no_gridlines = True
        
        # Configure Y axis
        plot.Y1.label = "Temp (°C)"
        plot.Y1.tick_format = "%.0f °C"  # Custom format for Y values
    
    # Controls for custom label options
    keep_default_ticks = dcg.Checkbox(C, label="Keep Default Ticks", value=False)
    show_quarters = dcg.Checkbox(C, label="Show Quarter Labels", value=False)
    
    # Function to update custom labels
    def update_labels():
        if show_quarters.value:
            # Add quarter labels at positions between months
            quarters = ["Q1", "Q2", "Q3", "Q4"]
            quarter_positions = [1.5, 4.5, 7.5, 10.5]  # Between months
            
            # Combine month and quarter labels
            all_labels = categories + quarters
            all_positions = np.concatenate([x_positions, quarter_positions])
            
            plot.X1.labels = all_labels
            plot.X1.labels_coord = all_positions
        else:
            # Just show month labels
            plot.X1.labels = categories
            plot.X1.labels_coord = x_positions
        
        plot.X1.keep_default_ticks = keep_default_ticks.value
        C.viewport.wake()
    
    # Connect controls
    keep_default_ticks.callback = lambda s, t, d: update_labels()
    show_quarters.callback = lambda s, t, d: update_labels()
    
    # Create a second example for numeric formatting
    with dcg.Plot(C, label="Custom Value Formatting", height=350, width=-1) as format_plot:
        # Plot some data
        x = np.linspace(0, 10, 100)
        y = np.exp(x)
        
        dcg.PlotLine(C, label="Exponential Growth", X=x, Y=y)
        
        # Configure Y axis
        format_plot.Y1.label = "Value"
    
    # Format selection for Y axis values
    format_options = dcg.Combo(C, items=["Default",
                                         r"Scientific: %.1e",
                                         r"Thousands: %.1fK",
                                         r"Fixed: %.2f",
                                         r"Percentage: %.1f%%"], 
                                label="Y Axis Format")
    
    # Connect format selection
    def update_format(sender, target, selected_format):
        if selected_format == "Default":
            format_plot.Y1.tick_format = ""
        elif selected_format == r"Scientific: %.1e":
            format_plot.Y1.tick_format = "%.1e"
        elif selected_format == r"Thousands: %.1fK":
            format_plot.Y1.tick_format = "%.1fK"
        elif selected_format == r"Fixed: %.2f":
            format_plot.Y1.tick_format = "%.2f"
        elif selected_format == r"Percentage: %.1f%%":
            format_plot.Y1.tick_format = "%.1f%%"
        C.viewport.wake()
    
    format_options.callback = update_format
    
    # Add explanations
    dcg.Text(C, value="Custom labels let you display categorical data or special marker positions.")
    dcg.Text(C, value="Format strings control how numeric values appear on axes.")

@demosection(dcg.Plot, dcg.PlotAxisConfig, dcg.AxisTag, dcg.PlotAnnotation, dcg.TreeNode)
@documented
@democode
def _axis_tags_annotations(C: dcg.Context):
    """
    ### Axis Tags and Annotations
    
    Axis tags are markers attached to specific positions on an axis, useful for:
    
    - Highlighting important values or thresholds
    - Marking reference points in your data
    - Adding interactive elements to axes
    
    Tags remain attached to their axis position even when zooming or panning.
    Annotations provide text labels at specific points within the plot area.
    """
    # Create sample data for demonstration
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    with dcg.Plot(C, label="Axis Tags and Annotations", height=400, width=-1) as plot:
        # Plot our base data
        dcg.PlotLine(C, label="Sin(x)", X=x, Y=y)
        
        # Configure axes
        plot.X1.label = "X Axis"
        plot.Y1.label = "Y Axis"
        
        # Enable secondary axes to demonstrate tags on multiple axes
        plot.X2.enabled = True
        plot.X2.opposite = True  # Place at top
        plot.Y2.enabled = True
        plot.Y2.opposite = True  # Place at right
        
        # Add tags to X1 axis (bottom)
        with plot.X1:
            # Mark π and 2π points with custom colors
            dcg.AxisTag(C, coord=np.pi, text="pi", bg_color=(255, 0, 0, 255))
            dcg.AxisTag(C, coord=2*np.pi, text="2pi", bg_color=(255, 0, 0, 255))
            # Mark the midpoint of the data
            dcg.AxisTag(C, coord=5, text="Mid", bg_color=(0, 0, 255, 255))
        
        # Add tags to Y1 axis (left)
        with plot.Y1:
            # Mark sin wave peaks
            dcg.AxisTag(C, coord=1, text="Peak", bg_color=(0, 255, 0, 255))
            dcg.AxisTag(C, coord=-1, text="Valley", bg_color=(0, 255, 0, 255))
        
        # Add tags to secondary axes
        with plot.X2:
            dcg.AxisTag(C, coord=7.5, text="Critical Point", bg_color=(255, 165, 0, 255))
        
        with plot.Y2:
            dcg.AxisTag(C, coord=0, text="Zero", bg_color=(128, 0, 128, 255))
        
        # Add plot annotations to highlight specific points
        # Annotations appear within the plot area
        dcg.PlotAnnotation(C, 
                          text="Local Maximum", 
                          x=np.pi/2,  # x coordinate 
                          y=np.sin(np.pi/2),  # y coordinate
                          offset=(10, -10),  # pixel offset from point
                          bg_color=(200, 200, 0, 200))
        
        dcg.PlotAnnotation(C, 
                          text="Local Minimum", 
                          x=3*np.pi/2, 
                          y=np.sin(3*np.pi/2),
                          offset=(-10, 10),
                          clamp=True,  # Keep visible when zooming
                          bg_color=(0, 200, 200, 200))
    
    # Interactive controls for demonstration
    with dcg.TreeNode(C, label="Tag Controls", value=True):
        dcg.Text(C, value="Try zooming and panning to see how tags stay attached to their positions.")
        dcg.Text(C, value="Tags are fixed to axis positions regardless of view.")
        dcg.Text(C, value="Annotations can be clamped to remain visible when outside the current view.")




pop_group()  # End Axes

push_group("Subplots")

@demosection(dcg.Subplots, dcg.Plot)
@documented
def _subplots_intro(C: dcg.Context):
    """
    ### Subplots

    Subplots allow you to display multiple plots in a grid arrangement, creating dashboards and multi-panel visualizations.
    
    Each subplot maintains its own independent plot structure while offering options to share certain elements like axes 
    ranges, legends, and styling across the grid.

    This section demonstrates:
    - Creating basic subplot grids
    - Customizing subplot layout with sizing ratios
    - Sharing axes, legends, and other properties between subplots
    - Advanced subplot configurations for data dashboards
    
    Subplots are particularly useful for:
    - Comparing multiple datasets side by side
    - Creating multi-panel data visualizations
    - Building monitoring dashboards
    - Displaying related but distinct visualizations together
    """
    pass

@demosection(dcg.Subplots, dcg.Plot)
@documented
@democode
def _basic_subplots(C: dcg.Context):
    """
    ### Basic Subplot Grid

    The `dcg.Subplots` container creates a grid of plots arranged in rows and columns.
    
    Each cell in the grid contains a `dcg.Plot` object, which can be configured independently.
    Plots are added in row-major order by default (can be changed to column-major).
    
    #### Key parameters:
    - `rows`: Number of subplot rows
    - `cols`: Number of subplot columns
    - `label`: Title for the entire subplot grid
    - `width`, `height`: Control overall dimensions
    
    This example creates a 2x2 grid of plots with different data series.
    """
    # Generate some data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) * np.cos(x)
    y4 = x / 10
    
    # Create a 2x2 grid of subplots
    with dcg.Subplots(C, rows=2, cols=2, label="Basic Subplot Grid", height=400, width=-1) as subplots:
        # Top-left plot (added first)
        with dcg.Plot(C, label="Sine Wave") as plot1:
            dcg.PlotLine(C, label="sin(x)", X=x, Y=y1)
            
        # Top-right plot (added second)
        with dcg.Plot(C, label="Cosine Wave") as plot2:
            dcg.PlotLine(C, label="cos(x)", X=x, Y=y2)
            
        # Bottom-left plot (added third)
        with dcg.Plot(C, label="Sin x Cos") as plot3:
            dcg.PlotLine(C, label="sin(x)xcos(x)", X=x, Y=y3)
            
        # Bottom-right plot (added fourth)
        with dcg.Plot(C, label="Linear") as plot4:
            dcg.PlotLine(C, label="x/10", X=x, Y=y4)

@demosection(dcg.Subplots, dcg.Plot)
@documented
@democode
def _subplot_layout(C: dcg.Context):
    """
    ### Customizing Subplot Layout

    Subplot grid layouts can be customized in several ways:
    
    #### Size ratios:
    - `row_ratios`: List of relative heights for each row
    - `col_ratios`: List of relative widths for each column
    
    #### Row vs column-major order:
    - `col_major`: If True, plots are added column-by-column rather than row-by-row
    
    #### Appearance options:
    - `no_title`: Hide subplot titles
    - `no_resize`: Disable subplot resize splitters
    - `no_align`: Disable subplot edge alignment
    
    This example creates a 3x2 grid with custom size ratios and shows the difference between 
    row-major and column-major order.
    """
    # Create data
    t = np.linspace(0, 10, 100)
    
    # Create row-major subplots
    dcg.Text(C, value="Row-major order (default):")
    with dcg.Subplots(C, 
                      rows=3,
                      cols=2, 
                      label="Custom Layout (Row-Major)",
                      row_ratios=[2, 1, 1],  # First row twice as tall
                      col_ratios=[2, 1],     # First column twice as wide
                      height=400, 
                      width=-1) as subplots1:
        # Plots are added row by row (0,0 -> 0,1 -> 1,0 -> 1,1 -> 2,0 -> 2,1)
        for i in range(6):
            with dcg.Plot(C, label=f"Plot {i+1}") as plot:
                # Generate different data for each plot
                data = np.sin(t + i/2) * (i+1)/6
                dcg.PlotLine(C, label=f"Series {i+1}", X=t, Y=data)
    
    # Create column-major subplots
    dcg.Text(C, value="Column-major order:")
    with dcg.Subplots(C, 
                      rows=3, 
                      cols=2, 
                      label="Custom Layout (Column-Major)",
                      row_ratios=[2, 1, 1],
                      col_ratios=[2, 1],
                      col_major=True,       # Switch to column-major
                      height=400, 
                      width=-1) as subplots2:
        # Plots are added column by column (0,0 -> 1,0 -> 2,0 -> 0,1 -> 1,1 -> 2,1)
        for i in range(6):
            with dcg.Plot(C, label=f"Plot {i+1}") as plot:
                data = np.sin(t + i/2) * (i+1)/6
                dcg.PlotLine(C, label=f"Series {i+1}", X=t, Y=data)


@demosection(dcg.Subplots, dcg.Plot, dcg.PlotAxisConfig)
@documented
@democode
def _sharing_axes_legends(C: dcg.Context):
    """
    ### Sharing Axes and Legends

    One of the most powerful features of subplots is the ability to share axes properties and legends
    across multiple plots in the grid.
    
    #### Sharing options:
    - `share_legends`: Share legend items across all subplots
    
    > **Note:** Unfortunately as of now the the built-in axes sharing features
    > do not work yet with the way we implement axes.
    > You can implement sharing manually by assigning the same axis config to target plots
    > (e.g., `plot2.X1 = plot1.X1`).
    
    This example demonstrates legend sharing and manual axis linking.
    """
    # Create data
    x = np.linspace(0, 10, 100)
    
    # Create subplot grid with shared legend
    with dcg.Subplots(C, 
                     rows=2, 
                     cols=2, 
                     label="Shared Legend Example", 
                     share_legends=True,  # Share legends across all plots
                     height=400, 
                     width=-1) as subplots:
        
        # Create four plots with the same series names
        plots = []
        for i in range(4):
            with dcg.Plot(C, label=f"Plot {i+1}") as plot:
                plots.append(plot)  # Store plot references for manual axis linking
                # Each plot has the same named series but with different data
                dcg.PlotLine(C, label="Series A", X=x, Y=np.sin(x + i))
                dcg.PlotLine(C, label="Series B", X=x, Y=np.cos(x + i))
        
        # Manually link X-axis between first row plots
        plots[1].X1 = plots[0].X1  # Link Plot 2 X-axis to Plot 1 X-axis
        
        # Manually link Y-axis between first column plots
        plots[2].Y1 = plots[0].Y1  # Link Plot 3 Y-axis to Plot 1 Y-axis
    
    # Explain the linking behavior
    dcg.Text(C, value="In this example:")
    dcg.Text(C, value="All plots share a common legend", marker="bullet")
    dcg.Text(C, value="Plot 1 and 2 share the same X-axis (top row)", marker="bullet")
    dcg.Text(C, value="Plot 1 and 3 share the same Y-axis (left column)", marker="bullet")
    dcg.Text(C, value="Try zooming or panning one of these linked plots to see the effect", marker="bullet")

@demosection(dcg.Subplots, dcg.Plot, dcg.PlotAxisConfig, dcg.PlotInfLines, dcg.PlotHistogram,
             dcg.PlotScatter, dcg.PlotBars)
@documented
@democode
def _practical_dashboard(C: dcg.Context):
    """
    ### Practical Dashboard Example

    Subplots are ideal for creating data dashboards that present multiple visualizations
    of related data in a cohesive layout. This example demonstrates a simple dashboard
    that could be used for monitoring or analysis purposes.
    
    This dashboard includes:
    - A main time series plot
    - A histogram of value distribution
    - A scatter plot showing correlation
    - A bar chart of categorical data
    
    The layout uses custom size ratios to emphasize the main plot while providing
    context with the supporting visualizations.
    """
    # Generate some sample data
    np.random.seed(42)
    
    # Time series data (120 data points)
    dates = np.linspace(1609459200, 1640995200, 120)  # 2021 year in Unix time
    values = 100 + np.cumsum(np.random.normal(0, 3, 120))  # Random walk
    
    # Derived data
    categories = ["A", "B", "C", "D", "E"]
    cat_values = np.array([42, 28, 35, 49, 21])
    correlate_x = values[:-1]
    correlate_y = values[1:]
    
    # Create a dashboard with subplots
    with dcg.Subplots(C,
                     rows=2,
                     cols=2,
                     label="Data Dashboard",
                     row_ratios=[2, 1],  # Main plot is twice as tall
                     col_ratios=[2, 1],  # Main plot is twice as wide
                     height=600,
                     width=-1) as dashboard:
        
        # 1. Main time series plot (top-left, larger)
        with dcg.Plot(C, label="Time Series") as main_plot:
            main_plot.X1.scale = dcg.AxisScale.TIME  # Use time scale for X-axis
            main_plot.X1.label = "Date"
            main_plot.Y1.label = "Value"
            
            # Add time series data
            with dcg.ThemeList(C) as theme:
                dcg.ThemeColorImPlot(C, line=(0, 120, 200), fill=(0, 120, 200, 50))
                dcg.ThemeStyleImPlot(C, line_weight=2)
            dcg.PlotLine(C, label="Metric Value", X=dates, Y=values, theme=theme, shaded=True)
            
            # Add horizontal reference line at mean value
            mean_value = np.mean(values)
            dcg.PlotInfLines(C, label="Mean", X=[mean_value], horizontal=True)
        
        # 2. Histogram (top-right)
        with dcg.Plot(C, label="Distribution") as hist_plot:
            hist_plot.Y1.label = "Frequency"
            hist_plot.X1.label = "Value"
            
            # Add histogram of values
            dcg.PlotHistogram(C, label="Distribution", X=values, bins=15)
        
        # 3. Lag plot (bottom-left)
        with dcg.Plot(C, label="Lag Correlation") as scatter_plot:
            scatter_plot.X1.label = "Value(t)"
            scatter_plot.Y1.label = "Value(t+1)"
            
            # Add scatter of value vs. next value
            scatter_theme = dcg.ThemeStyleImPlot(C, marker=dcg.PlotMarker.CIRCLE, marker_size=3)
            dcg.PlotScatter(C, label="Lag 1", X=correlate_x, Y=correlate_y, theme=scatter_theme)
        
        # 4. Bar chart (bottom-right)
        with dcg.Plot(C, label="Categories") as bar_plot:
            bar_plot.X1.no_gridlines = True
            bar_plot.X1.labels = categories
            bar_plot.X1.labels_coord = np.arange(len(categories))
            bar_plot.Y1.label = "Count"
            
            # Add bar chart
            bar_theme =  dcg.ThemeColorImPlot(C, fill=(200, 80, 100))
            dcg.PlotBars(C, label="Categories", X=np.arange(len(categories)), Y=cat_values, weight=0.7, theme=bar_theme)

pop_group()  # End Subplots

push_group("Legends")

@demosection(dcg.Plot, dcg.PlotLegendConfig)
@documented
def _legend_overview(C: dcg.Context):
    """
    ## Plot Legends

    Legends help viewers identify and interpret the different data series in your plots. DearCyGui provides comprehensive
    options for legend customization, positioning, and interaction.
    
    ### Key Features
    
    - **Flexible positioning**: Place legends inside or outside the plot area, in any corner or along any edge
    - **Layout options**: Horizontal or vertical arrangement of legend entries
    - **Styling**: Customize colors, fonts, backgrounds, and borders
    - **Interactivity**: Highlight plot elements when hovering over legend entries
    - **Context menus**: Right-click access to additional plot options

    Plot legends in DearCyGui can be extensively customized through the `legend_config` property
    of Plot objects. This provides detailed control over the legend's appearance and behavior.
    
    #### Positioning and Layout
    - `location`: Position of the legend within the plot (e.g., LegendLocation.NORTHWEST)
    - `outside`: When True, renders the legend outside the plot area
    - `horizontal`: When True, displays legend entries horizontally rather than vertically
    
    #### Behavior Options
    - `no_buttons`: Disables legend icons from functioning as hide/show buttons
    - `no_highlight_item`: Disables highlighting plot items when their legend entry is hovered
    - `no_highlight_axis`: Disables highlighting axes when their legend entry is hovered
    - `no_menus`: Disables right-clicking to open context menus
    - `sorted`: When True, displays legend entries in alphabetical order
    
    The following examples will demonstrate these features and show you how to create effective legends for your plots.
    """
    pass

@demosection(dcg.Plot, dcg.PlotLegendConfig, dcg.PlotLine, dcg.Checkbox)
@documented
@democode
def _legend_basic(C: dcg.Context):
    """
    ### Basic Legend Usage
    
    By default, DearCyGui automatically creates a legend entry for each plot series that has a label.
    The legend appears in the top-left (northwest) corner of the plot.
    
    #### Key points:
    - Each series with a non-empty label gets a legend entry
    - The legend icon/marker matches the series style
    - Legends can be hidden with the `no_legend` plot property
    - Default legend position is northwest (top-left)
    
    This example shows basic legend creation with multiple series.
    """
    with dcg.Plot(C, label="Basic Legend Example", height=350, width=-1) as plot:
        # Generate some sample data
        x = np.linspace(0, 10, 100)
        
        # Create multiple series with labels
        dcg.PlotLine(C, label="sin(x)", X=x, Y=np.sin(x))
        dcg.PlotLine(C, label="cos(x)", X=x, Y=np.cos(x), 
                     theme=dcg.ThemeColorImPlot(C, line=(255, 0, 0)))
        dcg.PlotLine(C, label="sin(x/2)", X=x, Y=np.sin(x/2), 
                     theme=dcg.ThemeColorImPlot(C, line=(0, 255, 0)))
        
        # Series without a label won't appear in the legend
        dcg.PlotLine(C, label="", X=x, Y=x/10 - 1, 
                     theme=dcg.ThemeColorImPlot(C, line=(150, 150, 150)))
        
        # Configure plot
        plot.X1.label = "X Axis"
        plot.Y1.label = "Y Axis"
    
    # Create a control to show/hide the legend
    show_legend = dcg.Checkbox(C, label="Show Legend", value=True)
    
    # Connect checkbox to plot property
    show_legend.callback = lambda s, t, d: plot.configure(no_legend=not d)
    
    dcg.Text(C, value="Try toggling the legend visibility with the checkbox above.")
    dcg.Text(C, value="Note that the gray line doesn't appear in the legend because it has an empty label.")

@demosection(dcg.Plot, dcg.PlotLegendConfig, dcg.LegendLocation, dcg.PlotScatter, dcg.PlotLine)
@documented
@democode
def _legend_position(C: dcg.Context):
    """
    ### Legend Positioning
    
    DearCyGui gives you precise control over where legends appear in your plots.
    
    #### Position options:
    - **location**: Corner or edge position (using `dcg.LegendLocation` enum)
    - **outside**: Place the legend outside the plot area
    - **horizontal**: Display legend entries horizontally rather than vertically
    
    #### Location options:
    - `CENTER`, `NORTH`, `SOUTH`, `EAST`, `WEST`
    - `NORTHWEST`, `NORTHEAST`, `SOUTHWEST`, `SOUTHEAST`
    
    This example lets you interactively try different legend positions.
    """
    # Create controls for legend positioning
    with dcg.HorizontalLayout(C):
        location_combo = dcg.Combo(C, 
                                   label="Legend Location", 
                                   items=["Northwest", "North", "Northeast",
                                          "West", "Center", "East",
                                          "Southwest", "South", "Southeast"],
                                   value="Northwest")
        
        outside_cb = dcg.Checkbox(C, label="Outside Plot", value=False)
        horizontal_cb = dcg.Checkbox(C, label="Horizontal Layout", value=False)
    
    with dcg.Plot(C, label="Legend Positioning", height=350, width=-1) as plot:
        # Generate sample data
        x = np.linspace(0, 10, 100)
        
        # Add multiple series
        dcg.PlotLine(C, label="Series A", X=x, Y=np.sin(x))
        
        with dcg.ThemeList(C) as theme_b:
            dcg.ThemeColorImPlot(C, line=(255, 0, 0))
            dcg.ThemeStyleImPlot(C, line_weight=2.0)
        dcg.PlotLine(C, label="Series B", X=x, Y=np.cos(x), theme=theme_b)
        
        with dcg.ThemeList(C) as theme_c:
            dcg.ThemeColorImPlot(C, line=(0, 180, 0))
            dcg.ThemeStyleImPlot(C, line_weight=2.0)
        dcg.PlotLine(C, label="Series C", X=x, Y=np.sin(x) * np.cos(x), theme=theme_c)
        
        # Add a scatter series to demonstrate different marker in legend
        with dcg.ThemeList(C) as theme_d:
            dcg.ThemeColorImPlot(C, marker_fill=(100, 100, 255))
            dcg.ThemeStyleImPlot(C, marker=dcg.PlotMarker.CIRCLE, marker_size=4)
        dcg.PlotScatter(C, label="Series D", X=x[::5], Y=np.sin(x[::5] + 1), theme=theme_d)
        
        # Configure plot
        plot.X1.label = "X Axis"
        plot.Y1.label = "Y Axis"
        
        # Initialize legend config
        plot.legend_config.location = dcg.LegendLocation.NORTHWEST
        plot.legend_config.outside = False
        plot.legend_config.horizontal = False
        
        # Function to update legend positioning
        def update_legend_pos(sender=None, target=None, data=None):
            # Map user-friendly names to enum values
            location_map = {
                "Northwest": dcg.LegendLocation.NORTHWEST,
                "North": dcg.LegendLocation.NORTH,
                "Northeast": dcg.LegendLocation.NORTHEAST,
                "West": dcg.LegendLocation.WEST,
                "Center": dcg.LegendLocation.CENTER,
                "East": dcg.LegendLocation.EAST,
                "Southwest": dcg.LegendLocation.SOUTHWEST,
                "South": dcg.LegendLocation.SOUTH,
                "Southeast": dcg.LegendLocation.SOUTHEAST
            }
            
            # Update legend properties
            plot.legend_config.location = location_map[location_combo.value]
            plot.legend_config.outside = outside_cb.value
            plot.legend_config.horizontal = horizontal_cb.value
            C.viewport.wake()
        
        # Connect controls to update function
        location_combo.callback = update_legend_pos
        outside_cb.callback = update_legend_pos
        horizontal_cb.callback = update_legend_pos
    
    dcg.Text(C, value="Try different combinations of location, outside, and horizontal settings.")
    dcg.Text(C, value="Outside legends can be useful to maximize the data display area.")

@demosection(dcg.Plot, dcg.PlotLegendConfig, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
@democode
def _legend_styling(C: dcg.Context):
    """
    ### Legend Styling and Appearance
    
    You can customize the visual appearance of legends to match your application's style.
    
    #### Styling options:
    - Background and border colors
    - Text color and font
    - Padding and spacing
    - Legend entry sorting
    
    This example demonstrates how to style legends using themes.
    """
    with dcg.Plot(C, label="Legend Styling", height=350, width=-1) as plot:
        # Generate sample data
        x = np.linspace(0, 6, 100)
        
        # Create multiple series
        dcg.PlotLine(C, label="Sine", X=x, Y=np.sin(x))
        dcg.PlotLine(C, label="Cosine", X=x, Y=np.cos(x), 
                     theme=dcg.ThemeColorImPlot(C, line=(220, 20, 60)))  # Crimson
        dcg.PlotScatter(C, label="Points", X=x[::10], Y=np.sin(x[::10] + 0.5),
                        theme=dcg.ThemeStyleImPlot(C, marker=dcg.PlotMarker.DIAMOND, marker_size=6))
        
        # Configure plot
        plot.X1.label = "X Axis"
        plot.Y1.label = "Y Axis"
        
        # Position the legend
        plot.legend_config.location = dcg.LegendLocation.NORTHEAST
        
        # Apply custom styling to the legend using a theme
        with dcg.ThemeList(C) as legend_theme:
            # Style the legend background and border
            dcg.ThemeColorImPlot(C, 
                                 legend_bg=(25, 25, 25, 220),     # Dark background
                                 legend_border=(200, 200, 200),   # Light gray border
                                 legend_text=(220, 220, 220))     # Off-white text
        
        # Apply the theme to the plot (themes cascade to children)
        plot.theme = legend_theme
        
        # Optionally sort legend items alphabetically
        plot.legend_config.sorted = True
    
    # Controls for additional legend settings
    with dcg.HorizontalLayout(C):
        sort_cb = dcg.Checkbox(C, label="Sort Alphabetically", value=True)
        no_buttons_cb = dcg.Checkbox(C, label="Disable Legend Buttons", value=False)
        no_highlight_cb = dcg.Checkbox(C, label="Disable Highlight on Hover", value=False)
    
    # Connect controls
    sort_cb.callback = lambda s, t, d: plot.legend_config.configure(sorted=d)
    no_buttons_cb.callback = lambda s, t, d: plot.legend_config.configure(no_buttons=d)
    no_highlight_cb.callback = lambda s, t, d: plot.legend_config.configure(no_highlight_item=d)
    
    dcg.Text(C, value="Legend entries can be clicked to show/hide the corresponding plot item.")
    dcg.Text(C, value="Hover over a legend entry to highlight the corresponding data in the plot.")

@demosection(dcg.Plot, dcg.PlotLegendConfig, dcg.PlotLine, dcg.PlotScatter, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
@democode
def _legend_popup_menus(C: dcg.Context):
    """
    ### Legend Popup Menus
    
    An important interactive feature of legends in DearCyGui is the ability to add context menus
    to legend items. When a user right-clicks on a legend entry, a popup menu can appear with
    custom controls and options.
    
    This is implemented by adding UI elements as children of plot series objects:
    
    - Any UI elements added as children of a plot series appear in its context menu
    - This allows for dynamic control of plot properties directly from the legend
    - Common uses include adjusting visual properties, filtering data, or showing additional information
    
    This example demonstrates how to add interactive controls to legend entries.
    """
    # Create data for the demonstration
    x = np.linspace(0, 10, 100)
    
    with dcg.Plot(C, label="Interactive Legend Menus", height=400, width=-1) as plot:
        plot.X1.label = "X Axis"
        plot.Y1.label = "Y Axis"
        
        # Series 1 with interactive frequency control
        with dcg.PlotLine(C, label="Sine Wave (Right-click me!)", 
                        X=x, Y=np.sin(x)) as sine_series:
            # Adding children to a plot series makes them appear in its legend context menu
            frequency_slider = dcg.Slider(C, label="Frequency", 
                                        value=1.0, min_value=0.1, max_value=5.0)
            amplitude_slider = dcg.Slider(C, label="Amplitude",
                                        value=1.0, min_value=0.1, max_value=2.0)
            dcg.Text(C, value="Adjust parameters above")
            dcg.Separator(C)  # Visual separator in the menu
        
        # Series 2 with color controls
        with dcg.PlotLine(C, label="Cosine Wave (Right-click me!)",
                        X=x, Y=np.cos(x),
                        theme=dcg.ThemeColorImPlot(C, line=(255, 0, 0))) as cosine_series:
            # Color selection options in the context menu
            dcg.Text(C, value="Change Line Color:")
            color_red = dcg.Button(C, label="Red", small=True)
            color_green = dcg.Button(C, label="Green", small=True)
            color_blue = dcg.Button(C, label="Blue", small=True)
            dcg.Separator(C)
        
        # Series 3 with visibility toggles for other series
        with dcg.PlotScatter(C, label="Points (Right-click me!)",
                          X=x[::5], Y=(np.sin(x[::5]) + np.cos(x[::5])),
                          theme=dcg.ThemeStyleImPlot(C, marker=dcg.PlotMarker.CIRCLE, marker_size=5)) as scatter_series:
            dcg.Text(C, value="Toggle Series Visibility:")
            sine_toggle = dcg.Checkbox(C, label="Show Sine Wave", value=True)
            cosine_toggle = dcg.Checkbox(C, label="Show Cosine Wave", value=True)
            dcg.Separator(C)

        # Create callback functions for the interactive controls
        def update_sine_wave(sender=None, target=None, data=None):
            sine_series.configure(Y=amplitude_slider.value * np.sin(frequency_slider.value * x))
            C.viewport.wake()
        
        frequency_slider.callback = update_sine_wave
        amplitude_slider.callback = update_sine_wave
        
        # Color control callbacks
        color_red.callback = lambda s, t, d: cosine_series.configure(theme=dcg.ThemeColorImPlot(C, line=(255, 0, 0)))
        color_green.callback = lambda s, t, d: cosine_series.configure(theme=dcg.ThemeColorImPlot(C, line=(0, 255, 0)))
        color_blue.callback = lambda s, t, d: cosine_series.configure(theme=dcg.ThemeColorImPlot(C, line=(0, 0, 255)))
        
        # Visibility toggle callbacks
        sine_toggle.callback = lambda s, t, d: sine_series.configure(show=d)
        cosine_toggle.callback = lambda s, t, d: cosine_series.configure(show=d)
    
    dcg.Text(C, value="Right-click on any legend entry to access its interactive menu")
    dcg.Text(C, value="Try adjusting the sine wave parameters or changing the cosine wave color")
    dcg.Text(C, value="The 'Points' legend item allows you to toggle visibility of other series")


pop_group()  # End Legends

push_group("Plot Styling")

@demosection(dcg.Plot, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
def _plot_styling_overview(C: dcg.Context):
    """
    ## Plot Styling

    DearCyGui provides extensive styling options to customize the appearance of your plots.
    These styling capabilities allow you to create visually appealing visualizations that
    match your application's aesthetic or highlight specific aspects of your data.

    ### Two Main Styling Components

    1. **ThemeColorImPlot**: Controls colors of various plot elements
       - Line colors, fill colors, marker colors
       - Background and border colors
       - Text, axis, and grid colors

    2. **ThemeStyleImPlot**: Controls non-color styling parameters
       - Line weights and styles
       - Marker types and sizes
       - Spacing, padding, and dimensions

    ### Applying Styles

    Styles can be applied at different levels:

    - **Individual plot element**: Affects only a single line, scatter plot, etc.
        To achieve this, set assign the target theme to the plot element
    - **Plot-wide**: Affects all elements within a plot
        To achieve this, set the theme to the plot
    - **Multiple plots**: Using a shared theme for visual consistency
        To achieve this, set the same theme to multiple plots

    The following examples demonstrate various styling techniques to enhance
    your plots and make them more effective and visually appealing.
    """
    pass

@demosection(dcg.Plot, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
def _color_customization(C: dcg.Context):
    """
    ### Color Customization with ThemeColorImPlot

    The `ThemeColorImPlot` object controls the colors of various plot elements.
    Colors can be specified in three formats:
    
    1. Unsigned integer (encodes rgba little-endian)
    2. RGB or RGBA tuple with values as integers (0-255)
    3. RGB or RGBA tuple with values as floats (0.0-1.0)

    #### Common Color Properties

    - **line**: Default color for plot lines
    - **fill**: Color for filled areas
    - **frame_bg**: Plot frame background color
    - **plot_bg**: Plot area background color
    - **plot_border**: Plot area border color
    - **axis_text**: Color for axis labels and values
    - **axis_grid**: Color for grid lines
    - **crosshairs**: Crosshairs color

    #### Legend Color Properties

    - **legend_bg**: Background color of the legend
    - **legend_border**: Border color of the legend
    - **legend_text**: Text color in the legend
    - **title_text**: Title text color
    - **inlay_text**: Color of text appearing inside plots

    #### Axis Color Properties

    - **axis_tick**: Color of axis tick marks
    - **axis_bg**: Background color of axis hover region
    - **axis_bg_hovered**: Background color when hovered
    - **axis_bg_active**: Background color when clicked

    In addition there are a few plot element specific colors:
    - **error_bar**: Color for error bars
    - **marker_outline**: Color for marker outlines
    - **marker_fill**: Color for marker fills

    By default the colors are automatically deduced from the
    current ImGui theme and a default colormap. In addition
    if you set some properties, the plot backend ImPlot will try
    to deduce the rest of the colors from the ones you set.
    """


@demosection(dcg.Plot, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot)
@documented
def _style_parameters(C: dcg.Context):
    """
    ### Style Parameters with ThemeStyleImPlot

    `ThemeStyleImPlot` controls non-color styling parameters such as line weights,
    marker types, spacing, and other visual attributes.
    
    #### Common Parameters
    
    - **line_weight**: Thickness of plot lines in pixels
    - **fill_alpha**: Alpha multiplier for all plot item fills (transparency)
    
    #### Special Plot Type Parameters

    - **marker**: Type of marker (e.g., circle, square, diamond)
    - **marker_size**: Size of markers in pixels
    - **marker_weight**: Outline thickness for markers in pixels
    - **error_bar_size**: Width of error bar whiskers in pixels
    - **error_bar_weight**: Thickness of error bar lines in pixels
    - **digital_bit_height**: Height of digital plot bits (at value 1) in pixels
    - **digital_bit_gap**: Spacing between digital plot channels in pixels
    
    #### Plot Area Parameters
    
    - **plot_border_size**: Thickness of the border around the plot area
    - **plot_default_size**: Default size when no specific size is provided
    - **plot_min_size**: Minimum size the plot can shrink to
    - **plot_padding**: Padding between the frame and plot area
    
    #### Axis Parameters
    
    - **major_tick_len**: Length of major tick marks for X and Y axes
    - **minor_tick_len**: Length of minor tick marks for X and Y axes
    - **major_tick_size**: Line thickness of major tick marks
    - **minor_tick_size**: Line thickness of minor tick marks
    - **major_grid_size**: Line thickness of major grid lines
    - **minor_grid_size**: Line thickness of minor grid lines
    - **minor_alpha**: Alpha multiplier for minor grid lines
    - **fit_padding**: Additional padding as percentage when fitting data
        See associated properties `auto_fit`, `no_initial_fit` and
        `restrict_fit_to_range`.
    
    #### Spacing Parameters
    
    - **label_padding**: Spacing between axes labels, tick labels, and plot edge
    - **legend_padding**: Padding between the legend and plot edges
    - **legend_inner_padding**: Padding within the legend box
    - **legend_spacing**: Space between legend entries
    - **mouse_pos_padding**: Padding between plot edge and mouse position text
    - **annotation_padding**: Padding around annotation text
    
    Unlike ThemeColorImPlot, which accepts different color formats, ThemeStyleImPlot 
    parameters are always either float or tuple of float, depending on the parameter,
    with the exception of Marker with must be a dcg.PlotMarker instance (see the scatter plots section).
    
    These style parameters can be used to create a consistent look across your application
    or to emphasize specific aspects of your data visualization.
    """

@demosection(dcg.Plot, dcg.ThemeColorImPlot, dcg.ThemeStyleImPlot, dcg.PlotAnnotation, dcg.AxisTag, dcg.utils.StyleEditor)
@documented
@democode
def _style_demo(C: dcg.Context):
    """
    Use the StyleEditor to try various settings
    """
    dcg.Button(C, label="Open Style Editor", callback=lambda s, t, d: dcg.utils.StyleEditor(C))

    with dcg.Plot(C, label="Style Editor Demo", height=400, width=-1) as plot:
        # Generate sample data
        x = np.linspace(0, 10, 100)
        
        # Create multiple series
        dcg.PlotLine(C, label="Sine", X=x, Y=np.sin(x))
        dcg.PlotScatter(C, label="Cosine", X=x, Y=np.cos(x))
        dcg.PlotErrorBars(C, label="Error Bars", X=x, Y=np.sin(x),
                          negatives=np.random.uniform(0.1, 0.5, size=x.shape),
                          positives=np.random.uniform(0.1, 0.5, size=x.shape))
        dcg.PlotDigital(C, label="Digital", X=x, Y=np.random.randint(0, 2, size=x.shape))

    # create a dummy legend context entry for each element
    for element in plot.children:
        with element:
            dcg.Text(C, value=f"Dummy entry for {element.label}")

    with plot:
        dcg.PlotAnnotation(C, label="Annotation", x=x[50], y=np.sin(x[50]),
                           offset=(10, 10), text="This is an annotation",
                           bg_color=(255, 255, 0, 100))
        with plot.X1:
            dcg.AxisTag(C, coord=x[50], text="I", bg_color=(255, 0, 255, 100))

pop_group()  # End Plot Styling

@demosection(dcg.Plot)
@documented
def _plot_configuration_options(C: dcg.Context):
    """
    ### Plot Configuration Options
    
    DearCyGui plots have numerous configuration options that control their behavior and appearance.
    Below are key options specific to plot functionality:
    
    #### Navigation Controls
    - `pan_button`: Button that when held enables navigation inside the plot (default: left mouse button)
    - `pan_mod`: Modifier keys (shift/ctrl/alt/super) required with pan_button (default: none)
    - `fit_button`: Button that must be double-clicked to fit axes to data (default: left mouse button)
    - `zoom_mod`: Modifier keys required for mouse wheel zoom (default: none)
    - `zoom_rate`: Zoom rate for scroll wheel (e.g., 0.1 = 10% plot range per scroll; negative to invert)
    
    #### Visual Options
    - `crosshairs`: Replace the default mouse cursor with crosshairs when hovering over plot
    - `equal_aspects`: Constrain X/Y axes to have the same units/pixels ratio
    - `no_frame`: Disable drawing of the ImGui frame around the plot
    - `no_inputs`: Disable all user interactions with the plot
    - `no_legend`: Hide the plot legend
    - `no_title`: Hide the plot title
    - `no_menus`: Disable context menus
    - `no_mouse_pos`: Disable display of mouse position text
    
    #### Time Formatting
    - `use_24hour_clock`: Use 24-hour format for time display (default: False)
    - `use_ISO8601`: Format dates according to ISO 8601 standard (default: False)
    - `use_local_time`: Format axis labels for system timezone with time axes (default: False)
    - `mouse_location`: Position where mouse coordinates are displayed (default: LegendLocation.southeast)
    """
    pass

if __name__ == "__main__":
    launch_demo(title="Plots Demo")