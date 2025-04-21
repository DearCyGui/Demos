import dearcygui as dcg
from demo_utils import documented, democode,\
    push_group, pop_group, launch_demo, demosection


# decorators:
# - documented: the description (markdown) is displayed
# - democode: the code is displayed and can edited (and run again)
# - demosection: the section is displayed in the table of contents,
#    the section name is extracted from the function name.

push_group("Introduction")

@demosection
@documented
def _intro(C: dcg.Context):
    """
    ## Introduction to Tables

    Tables in DearCyGui provide a powerful way to display and organize data. 
    They support a wide range of features including:

    - Row and column organization
    - Sorting and filtering
    - Custom styling and formatting
    - Interactive elements
    - Dynamic content

    This guide will walk you through all aspects of using tables effectively.
    """
    pass


pop_group()  # End Introduction

push_group("Creating Tables")

@demosection(dcg.Table)
@documented
def _table_creation(C: dcg.Context):
    """
    ## Creating tables

    Tables are a objects composed of a parent `dcg.Table`,
    to which child elements are added.

    Various parameters enable to tune the table appearance and behavior.

    In this section we will focus on creating tables and adding content.

    To attach children to a table, do not use the `parent` or `children`
    attributes, but use instead:
    - `table[row, col]` to access a specific cell
    - `table.row(row)` / `table.col(col)` to access a specific row/column
    - `table.next_row` / `table.next_col` to append a new row/column
    - `table.append_row` / `table.append_col` is an alternative to append a new row/column
    """
    pass


@demosection(dcg.Table, dcg.TableFlag, dcg.Button, dcg.TableElement)
@documented
@democode
def _indexing(C: dcg.Context):
    """
    ### Using table indexing

    The simplest way to fill a table is to directly
    write in the cells using the `table[row, col] = value` notation.

    While an object can be assigned to a cell, this syntax
    also accepts a string directly.

    Note the size of the Table is automatically deduced, and
    holes are allowed.
    """
    table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS)
    table[0, 0] = "Cell 1,1"
    table[0, 1] = dcg.Button(C, label="Cell 1,2")
    table[0, 2] = "Cell 1,3"
    table[1, 0] = "Cell 2,1"
    table[1, 2] = "Cell 2,3"


@demosection(dcg.Table, dcg.TableFlag, dcg.Text, dcg.TableElement)
@documented
@democode
def _accessing(C: dcg.Context):
    """
    ### Accessing rows and columns

    The `row` and `col` methods of a table allow to access
    a specific row or column.

    This can be useful to replace a range of elements,
    but can also be used to append elements.
    """
    table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS)
    for j in range(3):
        with table.col(j):
            for i in range(4):
                dcg.Text(C, value=f"Row{i} Column{j}")
    # replacing a specific col
    with table.col(1):
        for i in range(4):
            dcg.Text(C, value=f"Replaced Row{i} Column1")

@demosection(dcg.Table, dcg.TableFlag, dcg.Button, dcg.Text)
@documented
@democode
def _appending_1(C: dcg.Context):
    """
    ### Appending rows/columns

    The `next_row` and `next_col` attributes of a table
    allow to append a new row or column.

    Objects declared without an explicit parent inside
    these context managers will be automatically attached
    to the table.
    """
    table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS)
    with table.next_row:
        dcg.Text(C, value="Cell 1,1")
        dcg.Text(C, value="Cell 1,2")
    with table.next_row:
        dcg.Button(C, label="Cell 2,1")
        dcg.Text(C, value="Cell 2,2")
    with table.next_col:
        dcg.Text(C, value="Cell 1,3")
        dcg.Text(C, value="Cell 2,3")

@demosection(dcg.Table, dcg.TableFlag, dcg.Button)
@documented
@democode
def _appending_2(C: dcg.Context):
    """
    ### Appending rows/columns, variant

    The `append_row` and `append_col` methods of a table
    allow to append a new row or column by passing
    an iterable of elements (for instance a list).

    It is similar to the `next_row` and `next_col`, but
    do not require the `with` statement. In addition,
    it is possible to pass strings directly.
    """
    table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS)
    table.append_row(["Cell 1,1", "Cell 1,2"])
    table.append_row([dcg.Button(C, label="Cell 2,1"), "Cell 2,2"])
    table.append_col(["Cell 1,3", "Cell 2,3"])

@demosection(dcg.Table, dcg.TableFlag, dcg.Text)
@documented
@democode
def _table_size(C: dcg.Context):
    """
    ### Table size

    When adding elements the size of the table
    is automatically deduced. It is contained
    in the attributes `table.num_rows` and `table.num_cols`.

    Holes are allowed in the table, and the table
    will automatically resize to the maximum row and column
    index used.

    In order to force a specific size, it is possible to
    override the default size by setting the attributes
    `table.num_rows_visible` and `table.num_cols_visible`.
    """

    table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS | dcg.TableFlag.SIZING_STRETCH_SAME)
    table[0, 0] = "Cell 1,1"
    table[0, 2] = "Cell 1,3"
    table[1, 0] = "Cell 2,1"
    table[1, 2] = "Cell 2,3"

    table.num_cols_visible = 6

    dcg.Text(C, value=f"Number of actual rows: {table.num_rows}")
    dcg.Text(C, value=f"Number of actual columns: {table.num_cols}")


@demosection(dcg.Table, dcg.TableFlag, dcg.TableElement, dcg.Button, dcg.VerticalLayout, dcg.HorizontalLayout, dcg.ChildWindow)
@documented
@democode
def _cell_content(C: dcg.Context):
    """
    ### What can be put in a cell?

    A cell can contain any object.

    For the table cell indexing and `append_*` methods,
    are accepted:
    - dcg items (Text, Button, ...)
    - strings
    - any value that can be converted to a string (int, float, ...), except dict
    - a dict which keys can be one of "content", "tooltip" (see tooltip section),
        "ordering_value" (see sorting section) or "bg_color" (see theme section).

    In order to contain several dcg items in a cell, they must be grouped.
    """
    table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS | dcg.TableFlag.SIZING_STRETCH_SAME)
    table[0, 0] = "Cell 1,1"
    table[0, 1] = dcg.Button(C, label="Cell 1,2")
    table[0, 2] = {"content": "Cell 1,3", "tooltip": "This is a tooltip"}
    table[1, 0] = 42
    multi_item = dcg.VerticalLayout(C)
    table[1, 1] = multi_item
    with multi_item:
        dcg.Text(C, value="I contain")
        dcg.Text(C, value="two items")
    multi_item2 = dcg.ChildWindow(C, auto_resize_x=True, auto_resize_y=True, border=False)
    table[1, 2] = multi_item2
    with multi_item2:
        dcg.Text(C, value="I contain")
        dcg.Text(C, value="two items too")
    long_string = "This is a very long string that will be wrapped in the cell"
    " because as you know everyone loves long strings !!!"
    # fixed wrapping width
    multi_item3 = dcg.HorizontalLayout(C, width=100, alignment_mode=dcg.Alignment.JUSTIFIED)
    table[2, 1] = multi_item3
    with multi_item3:
        for word in long_string.split():
            dcg.Text(C, value=word)
    # adaptive wrapping width
    multi_item4 = dcg.HorizontalLayout(C, alignment_mode=dcg.Alignment.JUSTIFIED)
    table[2, 2] = multi_item4
    with multi_item4:
        for word in long_string.split():
            dcg.Text(C, value=word)

@demosection(dcg.Table)
@documented
def _other_methods(C: dcg.Context):
    """
    ### Other methods available to create tables

    - `table.col(i)` and `table.row(i)` represent a table column or row
       and can be indexed directly to read/write elements
    - `table.set_col(i, [...])` and `table.set_row(i, [...])` replace the
       content of a column or row
    - `table.insert_col(i, [...])` and `table.insert_row(i, [...])` insert
       a column or row at index i, shifting the other elements
    - `table.clear()` removes all the elements of the table
    - `table.remove_col(i)` and `table.remove_row(i)` remove a column or row
    - `del table[i, j]` removes the element at row i and column j
    - `table.swap((i1, j1), (i2, j2))` swaps the elements at (i1, j1) and (i2, j2)
    - `table.swap_cols(i1, i2)` and `table.swap_rows(i1, i2)` swaps the columns or rows
         at index i1 and i2
    """


pop_group()  # End Creating Tables

push_group("Formatting")


@demosection(dcg.Table, dcg.TableColConfig, dcg.TableRowConfig)
@documented
def _formatting_intro(C: dcg.Context):
    """
    ## Formatting Tables

    Tables in DearCyGui can be extensively customized to control their appearance and behavior.
    This section covers:

    - **Sizing**: controlling how columns and rows are sized
    - **Layout**: padding, scrolling, and outer dimensions
    - **Behavior**: making tables interactive through resizing, reordering, etc.

    Table formatting is primarily controlled through:
    - The `flags` parameter when creating the table
    - The `col_config` and `row_config` properties for column/row-specific settings
    - Properties of the table itself (`num_rows_frozen`, etc.)
    """
    pass

@demosection(dcg.Table, dcg.TableFlag)
@documented
def _table_flags(C: dcg.Context):
    """
    ## Table Flags

    In the following sections we will demonstrate how to use
    various TableFlag options to control the appearance and behavior.

    Here is the detailed explanation of each flag.
    This documentation corresponds to what you would get if you typed
    `help(dcg.TableFlag)` in a Python shell.

    The TableFlag flags can be appended using the `|` operator, and can
    be passed to the `flags` parameter when creating the table.

    ### Features:
    - **NONE (0)**: No flags
    - **RESIZABLE**: Enable resizing columns
    - **REORDERABLE**: Enable reordering columns 
    - **HIDEABLE**: Enable hiding/disabling columns
    - **SORTABLE**: Enable sorting
    - **NO_SAVED_SETTINGS**: Disable persisting columns order, width and sort settings
    - **CONTEXT_MENU_IN_BODY**: Right-click on columns body/contents will display table context menu
    
    ### Decorations:
    - **ROW_BG**: Set each RowBg color with alternating colors
    - **BORDERS_INNER_H**: Draw horizontal borders between rows
    - **BORDERS_OUTER_H**: Draw horizontal borders at the top and bottom
    - **BORDERS_INNER_V**: Draw vertical borders between columns
    - **BORDERS_OUTER_V**: Draw vertical borders on the left and right sides
    - **BORDERS_H**: Draw all horizontal borders (inner + outer)
    - **BORDERS_V**: Draw all vertical borders (inner + outer)
    - **BORDERS_INNER**: Draw all inner borders
    - **BORDERS_OUTER**: Draw all outer borders
    - **BORDERS**: Draw all borders (inner + outer)
    - **NO_BORDERS_IN_BODY**: Disable vertical borders in columns Body
    - **NO_BORDERS_IN_BODY_UNTIL_RESIZE**: Disable vertical borders in columns Body until hovered for resize
    
    ### Sizing Policy:
    - **SIZING_FIXED_FIT**: Columns default to _WidthFixed or _WidthAuto, matching contents width
    - **SIZING_FIXED_SAME**: Columns default to _WidthFixed or _WidthAuto, matching the maximum contents width of all columns
    - **SIZING_STRETCH_PROP**: Columns default to _WidthStretch with default weights proportional to each columns contents widths
    - **SIZING_STRETCH_SAME**: Columns default to _WidthStretch with default weights all equal
    
    ### Sizing Extra Options:
    - **NO_HOST_EXTEND_X**: Make outer width auto-fit to columns
    - **NO_HOST_EXTEND_Y**: Make outer height stop exactly at outer_size.y
    - **NO_KEEP_COLUMNS_VISIBLE**: Disable keeping column always minimally visible when ScrollX is off
    - **PRECISE_WIDTHS**: Disable distributing remainder width to stretched columns 
    
    ### Clipping:
    - **NO_CLIP**: Disable clipping rectangle for every individual column
    
    ### Padding:
    - **PAD_OUTER_X**: Enable outermost padding
    - **NO_PAD_OUTER_X**: Disable outermost padding
    - **NO_PAD_INNER_X**: Disable inner padding between columns
    
    ### Scrolling:
    - **SCROLL_X**: Enable horizontal scrolling
    - **SCROLL_Y**: Enable vertical scrolling
    
    ### Sorting:
    - **SORT_MULTI**: Hold shift when clicking headers to sort on multiple columns
    - **SORT_TRISTATE**: Allow no sorting, disable default sorting
    
    ### Miscellaneous:
    - **HIGHLIGHT_HOVERED_COLUMN**: Highlight column header when hovered
    """


@demosection(dcg.Table, dcg.TableFlag, dcg.TableColConfig)
@documented
def _col_flags(C: dcg.Context):
    """
    ## Column Configuration Options

    Table columns offer extensive configuration options that control their behavior and appearance.
    Each column's properties can be accessed and modified through `table.col_config[index]`.

    ### Main Properties:

    - **label**: Text displayed in the column header
    - **width**: Fixed width of the column in pixels (0 = auto-width)
    - **stretch**: Controls column sizing behavior
      - `True`: Column stretches with specified weight
      - `False`: Column uses fixed width
      - `None`: Uses table's default policy
    - **stretch_weight**: Relative weight for stretching (higher values = more space)
    - **enabled**: Whether the column is visible (can be changed by user interaction)
    - **show**: Directly control visibility (not affected by user interaction)

    ### Sorting Options:

    - **default_sort**: Makes this the default sorting column
    - **no_sort**: Disable sorting for this column
    - **prefer_sort_ascending/descending**: Set initial sort direction
    - **no_sort_ascending/descending**: Disable specific sort directions

    ### Visual/Behavior Controls:

    - **no_hide**: Prevent column from being hidden
    - **no_resize**: Prevent column from being resized
    - **no_reorder**: Prevent column from being reordered
    - **no_clip**: Disable content clipping in this column
    - **no_header_width**: Don't show width indicator when hovering header
    - **no_header_label**: Hide the column's header label

    ### State Detection:

    - **hovered**: Is the column currently being hovered?
    - **clicked/double_clicked**: Detect mouse interactions
    - **visible**: Is the column currently visible on screen?

    You can add event handlers to columns to respond to user interactions like:
    - **ToggledOpenHandler/ToggledCloseHandler**: When column is shown/hidden
    - **ContentResizeHandler**: When column is resized
    - **HoveredHandler/LostHoverHandler**: When mouse enters/leaves column
    """

@demosection(dcg.Table, dcg.TableFlag, dcg.TableRowConfig)
@documented
def _row_flags(C: dcg.Context):
    """
    ## Row Configuration Options

    Table rows have simpler configuration options compared to columns.
    Each row's properties can be accessed and modified through `table.row_config[index]`.

    ### Available Properties:

    - **bg_color**: Background color for the entire row
      - Set to `(r, g, b)` or `(r, g, b, a)` to apply a color
      - Set to `0` to use the default theme color
      - Applied on top of theme colors using blending
    
    - **min_height**: Minimum height for the row in pixels
      - Ensures row doesn't shrink below this height regardless of content

    - **show**: Control row visibility
      - Set to `False` to hide the row (useful for filtering)
      - Unlike columns, rows don't have an `enabled` property

    Rows do not support handlers.
    """

@demosection(dcg.Table, dcg.TableFlag, dcg.TableColConfig)
@documented
@democode
def _headers(C: dcg.Context):
    """
    ### Table Headers
    
    Headers provide column labels and interactive functionality for your tables.
    
    To enable headers:
    - Set `header=True` when creating the table
    - Set column labels using `table.col_config[i].label`
    
    Headers also enable various interactive features like:
    - Sorting (with the `SORTABLE` flag)
    - Column reordering (with the `REORDERABLE` flag)
    - Column hiding (with the `HIDEABLE` flag)
    - Column resizing (with the `RESIZABLE` flag)
    
    Header visibility can be toggled at any time by setting `table.header` property.
    """
    # Create a table with headers
    table = dcg.Table(C, header=True, flags=dcg.TableFlag.BORDERS)
    
    # Set column labels
    table.col_config[0].label = "ID"
    table.col_config[1].label = "Name"
    table.col_config[2].label = "Value"
    
    # Add some data
    data = [
        (1, "Alpha", 42),
        (2, "Beta", 73),
        (3, "Gamma", 15),
        (4, "Delta", 29),
        (5, "Epsilon", 56)
    ]
    
    for row in data:
        with table.next_row:
            for value in row:
                dcg.Text(C, value=str(value))
    
    # Controls for toggling header and features
    dcg.Text(C, value="Header controls:")
    
    def toggle_header(sender, table=table):
        table.header = sender.value
        
    def toggle_flag(sender, table=table):
        flag = sender.user_data
        if sender.value:
            table.flags |= flag
        else:
            table.flags &= ~flag
    
    with dcg.HorizontalLayout(C):
        dcg.Checkbox(C, label="Show Headers", value=True, callback=toggle_header)
    
    dcg.Text(C, value="Interactive features:")
    
    with dcg.HorizontalLayout(C):
        with dcg.VerticalLayout(C):
            dcg.Checkbox(C, label="Sortable", 
                         callback=toggle_flag,
                         user_data=dcg.TableFlag.SORTABLE)
                         
            dcg.Checkbox(C, label="Multi-Sort (hold Shift)", 
                         callback=toggle_flag,
                         user_data=dcg.TableFlag.SORT_MULTI)
        
        with dcg.VerticalLayout(C):
            dcg.Checkbox(C, label="Reorderable", 
                         callback=toggle_flag,
                         user_data=dcg.TableFlag.REORDERABLE)
                         
            dcg.Checkbox(C, label="Hideable", 
                         callback=toggle_flag,
                         user_data=dcg.TableFlag.HIDEABLE)
    
    # Advanced header customization example
    dcg.Separator(C)
    dcg.Text(C, value="Advanced header customization example:")
    
    table2 = dcg.Table(C, 
                      header=True, 
                      flags=dcg.TableFlag.BORDERS | 
                            dcg.TableFlag.HIDEABLE |
                            dcg.TableFlag.REORDERABLE |
                            dcg.TableFlag.SORTABLE |
                            dcg.TableFlag.HIGHLIGHT_HOVERED_COLUMN)
    
    # Configure column headers with additional settings
    table2.col_config[0].label = "ID"
    table2.col_config[1].label = "Name"
    table2.col_config[1].width = 150  # Fixed width for this column
    table2.col_config[2].label = "Value"
    table2.col_config[2].default_sort = True  # This column is sorted by default
    table2.col_config[2].prefer_sort_descending = True  # Sort descending by default
    
    # Add the same data
    for row in data:
        with table2.next_row:
            for value in row:
                dcg.Text(C, value=str(value))
    
    dcg.Text(C, value="This table has the following features enabled:")
    dcg.Text(C, value="- Highlight hovered column")
    dcg.Text(C, value="- Default sorting on 'Value' column (descending)")
    dcg.Text(C, value="- Fixed width for the 'Name' column")
    dcg.Text(C, value="- Hideable columns (right-click on header)")
    dcg.Text(C, value="- Column reordering (drag headers)")

@demosection(dcg.Table, dcg.TableFlag, dcg.Spacer)
@documented
@democode
def _sizing_policies(C: dcg.Context):
    """
    ### Sizing Policies

    DearCyGui provides four sizing policies that control how columns are sized:
    
    - `SIZING_FIXED_FIT`: Each column's width matches its contents
    - `SIZING_FIXED_SAME`: All columns have the same width, matching the maximum content width
    - `SIZING_STRETCH_PROP`: Columns stretch proportionally to their content width
    - `SIZING_STRETCH_SAME`: All columns stretch equally
    
    These policies affect the default behavior when a specific column width is not set.
    """
    dcg.Text(C, value="Compare the four different sizing policies:")
    
    # Helper function to create a table with a specific sizing policy
    def create_table(policy_flag, policy_name):
        dcg.Text(C, value=f"Policy {policy_name}:")
        table = dcg.Table(C, header=True, flags=dcg.TableFlag.BORDERS | policy_flag)
        
        # Add column headers with descriptive names
        table.col_config[0].label = "Short"
        table.col_config[1].label = "Medium Width"
        table.col_config[2].label = "Very Long Column Header"
        
        # Add data with varying content lengths
        for i in range(3):
            with table.next_row:
                table[i, 0] = "X"
                table[i, 1] = "Medium text"
                table[i, 2] = "This is a much longer piece of text for comparison"
        return table
    
    # Create tables with each sizing policy
    create_table(dcg.TableFlag.SIZING_FIXED_FIT, "SIZING_FIXED_FIT")
    dcg.Spacer(C, height=20)
    
    create_table(dcg.TableFlag.SIZING_FIXED_SAME, "SIZING_FIXED_SAME")
    dcg.Spacer(C, height=20)
    
    create_table(dcg.TableFlag.SIZING_STRETCH_PROP, "SIZING_STRETCH_PROP")
    dcg.Spacer(C, height=20)
    
    create_table(dcg.TableFlag.SIZING_STRETCH_SAME, "SIZING_STRETCH_SAME")

@demosection(dcg.Table, dcg.TableFlag, dcg.TableColConfig, dcg.Checkbox)
@documented
@democode
def _column_resizing(C: dcg.Context):
    """
    ### Column Resizing

    Tables can have resizable columns using the `RESIZABLE` flag.
    
    Additionally, individual columns can be:
    - **Fixed width**: Set a specific width using `col_config[i].width`
    - **Stretched**: Set `col_config[i].stretch = True` to fill available space
    - **Given stretch weight**: Control proportional stretching using `col_config[i].stretch_weight`
    
    By default, the sizing policy determines whether columns are fixed or stretched.
    """
    # Create a resizable table
    table = dcg.Table(C, header=True, 
                      flags=dcg.TableFlag.BORDERS | 
                            dcg.TableFlag.RESIZABLE)
    
    # Configure columns
    table.col_config[0].label = "Fixed (100px)"
    table.col_config[1].label = "Stretch (1x)"
    table.col_config[2].label = "Stretch (2x)"
    
    # Set column properties
    table.col_config[0].width = 100
    table.col_config[0].stretch = False
    
    table.col_config[1].stretch = True
    table.col_config[1].stretch_weight = 1.0
    
    table.col_config[2].stretch = True
    table.col_config[2].stretch_weight = 2.0
    
    # Add rows
    for i in range(4):
        with table.next_row:
            dcg.Text(C, value="Fixed width")
            dcg.Text(C, value="Stretches with weight 1")
            dcg.Text(C, value="Stretches with weight 2")
    
    # Information text
    dcg.Text(C, value="Try resizing the columns by dragging the borders")
    
    # Control for enabling/disabling resizing
    def toggle_resizable(sender, table=table):
        if sender.value:
            table.flags |= dcg.TableFlag.RESIZABLE
        else:
            table.flags &= ~dcg.TableFlag.RESIZABLE

    
    dcg.Checkbox(C, label="Resizable Columns", value=True, callback=toggle_resizable)

@demosection(dcg.Table, dcg.TableFlag, dcg.TableColConfig)
@documented
@democode
def _row_height(C: dcg.Context):
    """
    ### Row Height Control
    
    While column widths can be controlled in various ways, row heights are typically
    determined automatically based on content.
    
    However, you can set a minimum height for rows using `row_config[i].min_height`.
    """
    # Create table with borders
    table = dcg.Table(C, header=True, flags=dcg.TableFlag.BORDERS)
    
    # Set column headers
    table.col_config[0].label = "Row Type"
    table.col_config[1].label = "Content"
    
    # Create rows with different min_height values
    heights = [0, 30, 60, 90]
    
    for i, height in enumerate(heights):
        # Set minimum height for this row
        table.row_config[i].min_height = height
        
        with table.next_row:
            if height == 0:
                dcg.Text(C, value="Default height")
            else:
                dcg.Text(C, value=f"min_height = {height}px")
            dcg.Text(C, value="Row content")
    
    dcg.Text(C, value="Notice how rows respect their minimum height regardless of content")

@demosection(dcg.Table, dcg.TableFlag, dcg.TableColConfig, dcg.Separator, dcg.Slider)
@documented
@democode
def _outer_size_scrolling(C: dcg.Context):
    """
    ### Table Size and Scrolling
    
    By default, tables expand to fit their content. You can control this behavior with:
    
    - `height` and `width` parameters to set fixed dimensions
    - `NO_HOST_EXTEND_X` and `NO_HOST_EXTEND_Y` flags to control auto-expansion
    - `SCROLL_X` and `SCROLL_Y` flags to enable scrolling when content exceeds visible area
    
    Scrollable tables can also have frozen rows/columns that remain visible while scrolling.
    """
    # Create a table with fixed size and scrolling
    table = dcg.Table(C, 
                     header=True,
                     height=150,  # Fixed height
                     flags=dcg.TableFlag.BORDERS | 
                           dcg.TableFlag.SCROLL_Y |  # Enable vertical scrolling
                           dcg.TableFlag.NO_HOST_EXTEND_Y)  # Don't expand beyond set height
    
    # Set column headers
    table.col_config[0].label = "Index"
    table.col_config[1].label = "Content"
    
    # Add many rows to demonstrate scrolling
    for i in range(20):
        with table.next_row:
            dcg.Text(C, value=f"Row {i}")
            dcg.Text(C, value="This table has fixed height with scrolling enabled")
    
    # Controls for frozen rows
    dcg.Text(C, value="Number of frozen rows:")
    
    def set_frozen_rows(sender, table=table):
        table.num_rows_frozen = int(sender.value)
    
    dcg.Slider(C, label="", 
                 min_value=0, 
                 max_value=5,
                 format="int",
                 value=0,
                 callback=set_frozen_rows)
    
    dcg.Text(C, value="Frozen rows remain visible at the top while scrolling")
    
    # Horizontal scrolling example
    dcg.Separator(C)
    dcg.Text(C, value="Table with horizontal scrolling:")
    
    table2 = dcg.Table(C,
                      header=True,
                      width=300,  # Fixed width
                      flags=dcg.TableFlag.BORDERS |
                            dcg.TableFlag.SCROLL_X |  # Enable horizontal scrolling
                            dcg.TableFlag.NO_HOST_EXTEND_X)  # Don't expand beyond set width
    
    # Add columns with wide content
    for i in range(6):
        table2.col_config[i].label = f"Column {i}"
    
    # Add rows
    for i in range(3):
        with table2.next_row:
            for j in range(6):
                dcg.Text(C, value=f"Cell with more text than fits {i},{j}")

@demosection(dcg.Table, dcg.TableFlag, dcg.TableColConfig, dcg.Separator)
@documented
@democode
def _advanced_column_options(C: dcg.Context):
    """
    ### Advanced Column Options
    
    Columns have several options beyond basic width and sorting.
    This demo shows how to use various column flags
    
    Advanced features include:
    
    - **Column visibility control**: Hide/show specific columns
    - **Column restrictions**: Prevent specific operations on columns
    """
    # Create a table with all interactive features enabled
    table = dcg.Table(C, 
                     header=True,
                     flags=dcg.TableFlag.BORDERS | 
                           dcg.TableFlag.HIDEABLE | 
                           dcg.TableFlag.REORDERABLE | 
                           dcg.TableFlag.RESIZABLE | 
                           dcg.TableFlag.SORTABLE |
                           dcg.TableFlag.HIGHLIGHT_HOVERED_COLUMN)
    
    # Set column headers with different configuration options
    table.col_config[0].label = "ID"
    table.col_config[0].no_hide = True  # Can't be hidden
    
    table.col_config[1].label = "Name"
    table.col_config[1].no_reorder = True  # Can't be reordered
    
    table.col_config[2].label = "Value"
    table.col_config[2].no_sort = True  # Can't be sorted
    
    table.col_config[3].label = "Options"
    table.col_config[3].no_resize = True  # Can't be resized
    
    # Add data
    data = [
        (1, "Alpha", 42, "Edit"),
        (2, "Beta", 73, "Edit"),
        (3, "Gamma", 15, "Edit"),
        (4, "Delta", 29, "Edit"),
        (5, "Epsilon", 56, "Edit")
    ]

    for i, row in enumerate(data):
        with table.next_row:
            for j, value in enumerate(row):
                dcg.Text(C, value=str(value))
    
    
    # Column configuration options description
    dcg.Separator(C)
    dcg.Text(C, value="Column configuration restrictions:")
    dcg.Text(C, bullet=True, value="ID column: Cannot be hidden")
    dcg.Text(C, bullet=True, value="Name column: Cannot be reordered")
    dcg.Text(C, bullet=True, value="Value column: Cannot be sorted")
    dcg.Text(C, bullet=True, value="Options column: Cannot be resized")
    
    dcg.Text(C, value="Try right-clicking on column headers to see available options")

@demosection(dcg.Table, dcg.TableFlag, dcg.TableColConfig, dcg.Checkbox, dcg.HorizontalLayout)
@documented
@democode
def _padding_options(C: dcg.Context):
    """
    ### Table Padding Options
    
    Tables offer various padding options to control the spacing around content:
    
    - `PAD_OUTER_X`: Controls padding outside table edges (enabled by default)
    - `NO_PAD_OUTER_X`: Removes padding outside table edges
    - `NO_PAD_INNER_X`: Removes padding between columns
    
    These options help you control how compact or spacious your table appears.
    """
    dcg.Text(C, value="Default table padding:")
    
    # Create table with configurable padding
    table = dcg.Table(C, 
                      header=True,
                      flags=dcg.TableFlag.BORDERS)
    
    # Set headers and add rows
    for i in range(3):
        table.col_config[i].label = f"Column {i}"
        
    for i in range(3):
        with table.next_row:
            for j in range(3):
                dcg.Button(C, label=f"Cell {i},{j}", width=-1)
    
    # Padding control options
    def toggle_padding_flag(sender, table=table):
        flag = sender.user_data
        if sender.value:
            table.flags |= flag
        else:
            table.flags &= ~flag
    
    dcg.Text(C, value="Padding controls:")
    with dcg.HorizontalLayout(C):
        dcg.Checkbox(C, 
                    label="PAD_OUTER_X", 
                    value=True, 
                    callback=toggle_padding_flag,
                    user_data=dcg.TableFlag.PAD_OUTER_X)
        
        dcg.Checkbox(C, 
                    label="NO_PAD_OUTER_X", 
                    value=False, 
                    callback=toggle_padding_flag,
                    user_data=dcg.TableFlag.NO_PAD_OUTER_X)
        
        dcg.Checkbox(C, 
                    label="NO_PAD_INNER_X", 
                    value=False, 
                    callback=toggle_padding_flag,
                    user_data=dcg.TableFlag.NO_PAD_INNER_X)


pop_group()  # End Formatting

push_group("Interactions")


@demosection(dcg.Table)
@documented
def _interactions_intro(C: dcg.Context):
    """
    ## Table Interactions

    Interactive tables allow users to engage with data in meaningful ways. 
    DearCyGui tables support several interaction mechanisms:
    
    - **Tooltips**: Display additional information when hovering over cells
    - **Filtering**: Show only rows matching specific criteria
    - **Sorting**: Organize data by column values in ascending or descending order
    - **Selection**: Allow users to select specific rows or cells
    
    These interactions transform static data displays into dynamic interfaces
    that respond to user input and provide richer information access.
    """
    pass

@demosection(dcg.Table, dcg.Tooltip, dcg.TableFlag)
@documented
@democode
def _tooltips(C: dcg.Context):
    """
    ### Table Tooltips
    
    Tooltips provide additional context when hovering over table cells. This is useful for:
    
    - Displaying more detailed information than fits in a cell
    - Providing explanations or metadata about cell contents
    - Showing the complete text when a cell contains truncated content
    
    DearCyGui offers two ways to add tooltips to table cells:
    
    1. **Using the** `dcg.Tooltip` **widget**: Create a tooltip as a child of a cell item
    2. **Using dictionary syntax**: Include a "tooltip" key when setting cell content
    
    The dictionary approach is more concise, while the `dcg.Tooltip` widget
    gives more control over tooltip behavior (like hover delay).
    """
    # Example 1: Using dcg.Tooltip widget
    dcg.Text(C, value="Method 1: Using dcg.Tooltip widget")
    table1 = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS)
    
    with table1.next_row:
        for j in range(3):
            dcg.Text(C, value=f"Column {j}")
            with dcg.Tooltip(C):
                dcg.Text(C, value=f"Detailed information for column {j}")
                dcg.Text(C, value="(Hover over cells to see tooltips)")
    
    dcg.Spacer(C, height=20)
    
    # Example 2: Using dictionary syntax
    dcg.Text(C, value="Method 2: Using dictionary syntax")
    table2 = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS)
    
    for j in range(3):
        # Using dict syntax to set content and tooltip
        table2[0, j] = {
            "content": f"Column {j}", 
            "tooltip": f"Detailed information for column {j}\n(Using dictionary syntax)"
        }
    
    # Example with multi-line tooltip and more complex content
    dcg.Spacer(C, height=20)
    dcg.Text(C, value="Example with truncated text and helpful tooltip")
    table3 = dcg.Table(C, header=True, flags=dcg.TableFlag.BORDERS)
    
    # Set column headers
    table3.col_config[0].label = "Product"
    table3.col_config[1].label = "Description"
    
    # Data with long descriptions that will be truncated in the table
    products = [
        ("Laptop", "High-performance laptop with 16GB RAM, 512GB SSD, and dedicated graphics card"),
        ("Monitor", "27-inch 4K HDR display with 144Hz refresh rate and adjustable stand"),
        ("Keyboard", "Mechanical keyboard with RGB lighting, programmable keys and wrist rest")
    ]
    
    # Add rows with truncated descriptions and full tooltips
    for product, description in products:
        with table3.next_row:
            dcg.Text(C, value=product)
            # Truncate the description in the cell but show full text in tooltip
            truncated = description[:20] + "..." if len(description) > 20 else description
            dcg.Text(C, value=truncated)
            with dcg.Tooltip(C):
                dcg.Text(C, value=description)
    
    # Note on tooltip behavior
    dcg.Text(C, value="Note: Hover over cells with truncated text to see the full description")

@demosection(dcg.Table, dcg.TableFlag, dcg.InputText, dcg.EditedHandler)
@documented
@democode
def _filtering(C: dcg.Context):
    """
    ### Table Filtering
    
    Filtering allows users to dynamically show only rows that match specific criteria.
    This is particularly useful for large datasets where users need to focus on
    specific subsets of data.
    
    Key filtering concepts:
    
    - The `row_config[i].show` property controls visibility of individual rows
    - Filtering is typically connected to an input control (like a text field)
    - Custom filter logic can be implemented based on any criteria
    - Filtering doesn't remove rows from the table, it just hides them
    
    Common filtering use cases:
    
    - Text search across any column
    - Numeric range filtering (e.g., "show values between X and Y")
    - Category filtering (e.g., "show only items in category Z")
    - Combination filtering with multiple criteria
    
    This example demonstrates text-based filtering across all columns.
    """
    # Create a filter input
    filter_value = dcg.InputText(C, label="Filter", hint="Type to filter table")
    
    # Create a table with filterable content
    table = dcg.Table(C, 
                     header=True,
                     flags=dcg.TableFlag.BORDERS | 
                           dcg.TableFlag.SCROLL_Y |
                           dcg.TableFlag.ROW_BG,
                     height=250)
    
    # Set column headers
    table.col_config[0].label = "ID"
    table.col_config[1].label = "Name"
    table.col_config[2].label = "Category"
    table.col_config[3].label = "Value"
    
    # Add rows with sample data
    data = [
        (1, "Alpha", "Fruit", 42),
        (2, "Beta", "Vegetable", 73),
        (3, "Gamma", "Fruit", 15),
        (4, "Delta", "Grain", 29),
        (5, "Epsilon", "Vegetable", 56),
        (6, "Zeta", "Dairy", 88),
        (7, "Eta", "Fruit", 33),
        (8, "Theta", "Grain", 91),
        (9, "Iota", "Dairy", 27),
        (10, "Kappa", "Vegetable", 63)
    ]
    
    for item in data:
        with table.next_row:
            for value in item:
                dcg.Text(C, value=str(value))
    
    # Filter function to show/hide rows based on input
    def apply_filter(sender, target, table=table):
        filter_text = target.value.lower()
        
        # Count how many rows are displayed
        visible_count = 0
        
        for i in range(table.num_rows):
            # Check if any cell in this row contains the filter text
            row_matches = any(
                filter_text in str(table[i, j].content.value).lower() 
                for j in range(table.num_cols)
            )
            
            # Show row if it matches or if filter is empty
            row_visible = row_matches or not filter_text
            table.row_config[i].show = row_visible
            
            if row_visible:
                visible_count += 1
        
        # Update filter status message
        filter_status.value = f"Showing {visible_count} of {table.num_rows} rows"
    
    # Status text to show how many rows are filtered
    filter_status = dcg.Text(C, value=f"Showing {table.num_rows} of {table.num_rows} rows")
    
    # Connect filter function to input
    filter_value.handlers += [dcg.EditedHandler(C, callback=apply_filter)]


@demosection(dcg.Table, dcg.TableFlag, dcg.TableColConfig, dcg.Checkbox)
@documented
@democode
def _sorting(C: dcg.Context):
    """
    ### Table Sorting
    
    Sorting allows users to organize table data by column values, making it easier
    to find and analyze information. DearCyGui provides powerful sorting capabilities
    through the `SORTABLE` flag and related options.
    
    Key sorting features:
    
    - **Basic sorting**: Click on column headers to sort by that column
    - **Multi-column sorting**: Hold Shift while clicking to sort by multiple columns
    - **Tri-state sorting**: Toggle between ascending, descending, and unsorted
    - **Custom sorting**: Control how items are sorted with `ordering_value`
    
    Sorting controls:
    
    - Enable sorting with the `SORTABLE` flag
    - Control multi-column sorting with the `SORT_MULTI` flag
    - Enable three-state sorting with the `SORT_TRISTATE` flag
    - Set column-specific sort behavior with `col_config` properties:
      - `default_sort`: Makes a column the default sort column
      - `prefer_sort_ascending/descending`: Sets initial sort direction
      - `no_sort` / `no_sort_ascending/descending`: Restricts sorting options
    
    By default, tables sort items by comparing the content set (before string conversion). For custom sorting
    logic, use the `ordering_value` property to define how items should be ordered.
    """
    import random
    
    # Create a sortable table
    table = dcg.Table(C, 
                     header=True,
                     flags=dcg.TableFlag.BORDERS | 
                           dcg.TableFlag.SORTABLE |
                           dcg.TableFlag.SORT_MULTI |
                           dcg.TableFlag.ROW_BG,
                     height=250)
    
    # Set column headers
    table.col_config[0].label = "ID"
    table.col_config[1].label = "Name"
    table.col_config[2].label = "Displayed Value"
    table.col_config[3].label = "Hidden Value"
    
    # Generate data with custom sort values
    data = []
    names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", 
             "Zeta", "Eta", "Theta", "Iota", "Kappa"]
    
    for i in range(len(names)):
        name = names[i]
        # Create a displayed value that's different from the sort value
        displayed_value = random.randint(1, 100)
        # Create a hidden value for custom sorting
        hidden_value = random.randint(1, 100)
        data.append((i+1, name, displayed_value, hidden_value))
    
    # Add data to the table with custom sort values
    for i, (id_val, name, displayed, hidden) in enumerate(data):
        # ID column
        table[i, 0] = id_val
        
        # Name column
        table[i, 1] = name
        
        # Displayed value column (sorts by displayed value)
        table[i, 2] = displayed
        
        # Hidden value column (sorts by hidden value)
        table[i, 3] = {
            "content": f"Sort: {hidden}",
            "ordering_value": hidden  # This controls how it sorts
        }
    
    # Instructions and controls
    dcg.Text(C, value="Click on column headers to sort. Hold Shift for multi-column sorting.")
    
    # Sorting option controls
    with dcg.HorizontalLayout(C):
        # Toggle for sortable flag
        def toggle_sortable(sender, table=table):
            if sender.value:
                table.flags |= dcg.TableFlag.SORTABLE
            else:
                table.flags &= ~dcg.TableFlag.SORTABLE
            
        dcg.Checkbox(C, label="Sortable", value=True, callback=toggle_sortable)
        
        # Toggle for multi-sort flag
        def toggle_multi_sort(sender, table=table):
            if sender.value:
                table.flags |= dcg.TableFlag.SORT_MULTI
            else:
                table.flags &= ~dcg.TableFlag.SORT_MULTI
            
        dcg.Checkbox(C, label="Multi-Sort (Shift)", value=True, callback=toggle_multi_sort)
        
        # Toggle for tristate flag
        def toggle_tristate(sender, table=table):
            if sender.value:
                table.flags |= dcg.TableFlag.SORT_TRISTATE
            else:
                table.flags &= ~dcg.TableFlag.SORT_TRISTATE
            
        dcg.Checkbox(C, label="Tri-State Sorting", value=False, callback=toggle_tristate)
    
    # Advanced example with sort types
    dcg.Separator(C)
    dcg.Text(C, value="Advanced example with different sort types:")
    
    # Table with different data types
    table2 = dcg.Table(C, 
                      header=True,
                      flags=dcg.TableFlag.BORDERS | 
                            dcg.TableFlag.SORTABLE |
                            dcg.TableFlag.ROW_BG,
                      height=150)
    
    # Set column headers
    table2.col_config[0].label = "Text"
    table2.col_config[1].label = "Number"
    table2.col_config[2].label = "Date"  # Will be sorted by timestamp
    
    # Sample data with different types
    import datetime
    
    mixed_data = [
        ("Zebra", 42, datetime.date(2023, 5, 15)),
        ("Apple", 17, datetime.date(2022, 12, 25)),
        ("Monkey", 99, datetime.date(2023, 1, 10)),
        ("Banana", 5, datetime.date(2021, 8, 3)),
        ("Cat", 33, datetime.date(2022, 3, 21))
    ]
    
    # Add data with appropriate ordering values
    for i, (text, number, date) in enumerate(mixed_data):
        # Text column - sorts lexicographically 
        table2[i, 0] = text
        
        # Number column - sorts numerically
        table2[i, 1] = number
        
        # Date column - format for display but sort by timestamp
        formatted_date = date.strftime("%b %d, %Y")
        timestamp = date.toordinal()  # Convert to ordinal for sorting
        
        table2[i, 2] = {
            "content": formatted_date,
            "ordering_value": timestamp  # Sort by timestamp
        }
    
    dcg.Text(C, value="The date column sorts chronologically, not alphabetically")

@demosection(dcg.Table, dcg.TableFlag, dcg.Selectable)
@documented
@democode
def _selection(C: dcg.Context):
    """
    ### Row and Cell Selection
    
    Tables often need selection capabilities to let users interact with specific
    rows or cells. DearCyGui provides selection mechanisms through the
    `dcg.Selectable` widget.

    The demo below includes examples of:
    - `dcg.Selectable` widgets inside table cells
    - Using `span_columns=True` to make an entire row selectable
    - Handling selection events with callbacks

    """
    # Selection state trackers
    selected_row = dcg.Text(C, value="None")
    selected_cell = dcg.Text(C, value="None")
    
    # Helper function to create a selectable table
    def create_selectable_table(selection_type="row"):
        table = dcg.Table(C, 
                         header=True, 
                         flags=dcg.TableFlag.BORDERS | dcg.TableFlag.ROW_BG)
        
        # Set column headers
        table.col_config[0].label = "ID"
        table.col_config[1].label = "Name"
        table.col_config[2].label = "Value"
        
        # Sample data
        data = [
            (1, "Alpha", 42),
            (2, "Beta", 73),
            (3, "Gamma", 15),
            (4, "Delta", 29),
            (5, "Epsilon", 56)
        ]
        
        # Row selection callback
        def on_row_select(sender):
            selected_row.value = f"Row {sender.user_data}"
            
        # Cell selection callback
        def on_cell_select(sender):
            row, col = sender.user_data
            selected_cell.value = f"Row {row}, Column {col}"
        
        # Add rows with selectables
        for i, (id, name, value) in enumerate(data):
            with table.next_row:
                # For row selection, we use one selectable that spans columns
                if selection_type == "row":
                    # First column contains the selectable that spans all columns
                    dcg.Selectable(C, 
                                  label=f"{id}: {name} ({value})",
                                  span_columns=True,
                                  callback=on_row_select,
                                  user_data=i)
                    
                # For cell selection, each cell gets its own selectable
                else:
                    dcg.Selectable(C, 
                                  label=str(id),
                                  callback=on_cell_select,
                                  user_data=(i, 0))
                    
                    dcg.Selectable(C, 
                                  label=name,
                                  callback=on_cell_select,
                                  user_data=(i, 1))
                    
                    dcg.Selectable(C, 
                                  label=str(value),
                                  callback=on_cell_select,
                                  user_data=(i, 2))
        
        return table
    
    # Row selection example
    dcg.Text(C, value="Row Selection Example:")
    create_selectable_table("row")
    text = dcg.Text(C, value="Selected: ", no_newline=True)
    selected_row.previous_sibling = text
    
    dcg.Separator(C)
    
    # Cell selection example
    dcg.Text(C, value="Cell Selection Example:")
    create_selectable_table("cell")
    text = dcg.Text(C, value="Selected: ", no_newline=True)
    selected_cell.previous_sibling = text
    
    # Explanation
    dcg.Text(C, value="Click on any row or cell to select it")

@demosection(dcg.Table, dcg.TableColConfig, dcg.GotHoverHandler, dcg.LostFocusHandler,
             dcg.ClickedHandler, dcg.ToggledCloseHandler, dcg.ToggledOpenHandler)
@documented
@democode
def _column_handlers(C: dcg.Context):
    """
    ### Column Interaction Handlers
    
    Table columns can have various event handlers attached to respond to user interactions.
    This enables creating interactive tables that respond to events like:
    
    - Column hovering (GotHoverHandler/LostHoverHandler)
    - Column clicking (ClickedHandler)
    - Column visibility changes (ToggledOpenHandler/ToggledCloseHandler)
    
    This example demonstrates how to use these handlers to create dynamic column behaviors.
    Note rows do not support handlers.
    """
    # Create a table with interactive features
    table = dcg.Table(C, 
                     header=True,
                     flags=dcg.TableFlag.BORDERS | 
                           dcg.TableFlag.HIDEABLE |
                           dcg.TableFlag.HIGHLIGHT_HOVERED_COLUMN)
    
    # Create a status indicator
    status = dcg.Text(C, value="Interact with columns to see events")
    
    # Set column headers
    table.col_config[0].label = "Hover Column"
    table.col_config[1].label = "Click Column"
    table.col_config[2].label = "Hide/Show Column"
    
    # Add some content
    for i in range(4):
        with table.next_row:
            dcg.Text(C, value=f"Row {i}, Col 0")
            dcg.Text(C, value=f"Row {i}, Col 1")
            dcg.Text(C, value=f"Row {i}, Col 2")
    
    # Column 0: Hover handlers
    def on_hover_col(sender, status=status):
        status.value = "Column 0 is being hovered"
        # Highlight cells in hovered column
        for i in range(table.num_rows):
            cell = table[i, 0]
            cell.bg_color = (255, 255, 0, 100)  # Yellow highlight
            table[i, 0] = cell  # Need to update the cell after changing it
    
    def on_unhover_col(sender, status=status):
        status.value = "Interact with columns to see events"
        # Remove highlighting
        for i in range(table.num_rows):
            cell = table[i, 0]
            cell.bg_color = 0  # Reset background color
            table[i, 0] = cell
    
    # Add hover handlers to first column
    table.col_config[0].handlers += [
        dcg.GotHoverHandler(C, callback=on_hover_col),
        dcg.LostHoverHandler(C, callback=on_unhover_col)
    ]
    
    # Column 1: Click handler
    def on_click_col(sender, status=status):
        status.value = "Column 1 was clicked"
        # Change text color in the column
        for i in range(table.num_rows):
            cell = table[i, 1]
            # Create new text with red color
            new_text = dcg.Text(C, value=cell.content.value, color=(255, 0, 0))
            # Replace old content
            table[i, 1] = new_text
    
    # Add click handler to second column
    table.col_config[1].handlers += [
        dcg.ClickedHandler(C, callback=on_click_col)
    ]
    
    # Column 2: Visibility handlers
    def on_col_hidden(sender, status=status):
        status.value = "Column 2 was hidden (right-click header and uncheck to show)"
        
    def on_col_shown(sender, status=status):
        status.value = "Column 2 was shown"
    
    # Add visibility handlers to third column
    table.col_config[2].handlers += [
        dcg.ToggledCloseHandler(C, callback=on_col_hidden),
        dcg.ToggledOpenHandler(C, callback=on_col_shown)
    ]
    
    # Instructions
    dcg.Separator(C)
    dcg.Text(C, value="Try these interactions:")
    dcg.Text(C, bullet=True, value="Hover over the first column to highlight it")
    dcg.Text(C, bullet=True, value="Click the second column to change text color")
    dcg.Text(C, bullet=True, value="Right-click on the header and toggle the third column")

@demosection(dcg.Table, dcg.TableFlag, dcg.GotHoverHandler, dcg.LostHoverHandler,
             dcg.ClickedHandler, dcg.ResizeHandler)
@documented
@democode
def _table_handlers(C: dcg.Context):
    """
    ### Table-Level Handlers
    
    While columns can have their own handlers, tables themselves can also respond
    to various events through handlers, with similar behaviour to normal widgets.
    
    - **HoverHandler**: Detects mouse hovering over the entire table
    - **ClickedHandler**, etc: Detects clicks over the entire table
    - **ResizeHandler**: Triggered when the table size changes
    
    These handlers allow you to respond to table-wide interactions rather than just
    column-specific events.
    """
    # Create a status display for table events
    status = dcg.Text(C, value="Interact with the table to see events")
    
    # Create a simple table with some content
    table = dcg.Table(C, 
                     header=True,
                     flags=dcg.TableFlag.BORDERS | 
                           dcg.TableFlag.ROW_BG |
                           dcg.TableFlag.RESIZABLE)
    
    # Set column headers
    table.col_config[0].label = "ID"
    table.col_config[1].label = "Name"
    table.col_config[2].label = "Value"
    
    # Add some data rows
    for i in range(5):
        with table.next_row:
            dcg.Text(C, value=str(i+1))
            dcg.Text(C, value=f"Item {i+1}")
            dcg.Text(C, value=str(i*10 + 5))
    
    # Add table hover handlers
    def on_table_hover(sender):
        status.value = "Table is being hovered"
        # You could highlight the table or update UI elements
        
    def on_table_unhover(sender):
        if status.value == "Table is being hovered": # do not hide clicks
            status.value = "Interact with the table to see events"
    
    def on_table_clicked(sender):
        status.value = "Table was clicked"
        # This could be used to show additional controls or reset sorting
    
    # Add table content resize handler
    def on_table_resize(sender, target, data):
        status.value = f"Table was resized ({target.rect_size})"
    
    # Attach the handlers to the table
    table.handlers += [
        dcg.GotHoverHandler(C, callback=on_table_hover),
        dcg.LostHoverHandler(C, callback=on_table_unhover),
        dcg.ClickedHandler(C, callback=on_table_clicked),
        dcg.ResizeHandler(C, callback=on_table_resize)
    ]
    
    # Add demo controls to trigger resize events
    dcg.Separator(C)
    dcg.Text(C, value="Resize controls:")
    
    def add_row(table=table):
        new_idx = table.num_rows
        with table.next_row:
            dcg.Text(C, value=str(new_idx+1))
            dcg.Text(C, value=f"Item {new_idx+1}")
            dcg.Text(C, value=str(new_idx*10 + 5))
        
    def remove_row(table=table):
        if table.num_rows > 0:
            table.remove_row(table.num_rows-1)
    
    with dcg.HorizontalLayout(C):
        dcg.Button(C, label="Add Row", callback=add_row)
        dcg.Button(C, label="Remove Row", callback=remove_row)
    
    # Display status
    dcg.Separator(C)
    text = dcg.Text(C, value="Event status:")
    status.previous_sibling = text
    
    # Instructions
    dcg.Text(C, value="Try these interactions:")
    dcg.Text(C, bullet=True, value="Hover over and leave the table")
    dcg.Text(C, bullet=True, value="Click on the table headers")
    dcg.Text(C, bullet=True, value="Add or remove rows")
    dcg.Text(C, bullet=True, value="Resize the table by dragging column dividers")


pop_group()  # End Interactions

push_group("Styling")


@demosection(dcg.Table, dcg.TableFlag, dcg.HorizontalLayout, dcg.VerticalLayout)
@documented
@democode
def _table_borders(C: dcg.Context):
    """
    ### Table Borders

    Tables can display various types of borders to visually separate content.
    Border flags control the visibility of:
    - Inner horizontal borders (between rows)
    - Outer horizontal borders (top and bottom)
    - Inner vertical borders (between columns)
    - Outer vertical borders (left and right)

    The `BORDERS` flag is a shorthand that enables all borders.
    """
    # Create a table with all borders enabled
    table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS)
    
    # Populate the table with sample content
    for i in range(5):
        with table.next_row:
            for j in range(3):
                dcg.Text(C, value=f"Cell {i},{j}")
    
    # Interactive controls to toggle different border types
    dcg.Text(C, value="Toggle borders to see their effect:")
    
    # We need a callback function to change table flags
    def toggle_flag(sender, table=table):
        flag = sender.user_data
        if sender.value:
            table.flags |= flag
        else:
            table.flags &= ~flag
    
    with dcg.HorizontalLayout(C):
        with dcg.VerticalLayout(C):
            dcg.Checkbox(C, label="Inner Horizontal", 
                         value=True, 
                         callback=toggle_flag, 
                         user_data=dcg.TableFlag.BORDERS_INNER_H)
            dcg.Checkbox(C, label="Inner Vertical", 
                         value=True,
                         callback=toggle_flag,
                         user_data=dcg.TableFlag.BORDERS_INNER_V)
        with dcg.VerticalLayout(C):
            dcg.Checkbox(C, label="Outer Horizontal", 
                         value=True,
                         callback=toggle_flag,
                         user_data=dcg.TableFlag.BORDERS_OUTER_H)
            dcg.Checkbox(C, label="Outer Vertical",
                         value=True,
                         callback=toggle_flag,
                         user_data=dcg.TableFlag.BORDERS_OUTER_V)

@demosection(dcg.Table, dcg.TableFlag, dcg.TableRowConfig, dcg.Checkbox)
@documented
@democode
def _table_row_background(C: dcg.Context):
    """
    ### Row Backgrounds

    Tables can display alternating row background colors for better readability.
    
    The `ROW_BG` flag enables alternating row backgrounds using the theme's 
    `TableRowBg` and `TableRowBgAlt` colors.
    
    You can also manually set a row's background color using `row_config[i].bg_color`.
    """
    # Create a table with alternating row backgrounds
    table = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS | dcg.TableFlag.ROW_BG)
    
    # Populate the table with sample content
    for i in range(8):
        with table.next_row:
            for j in range(3):
                dcg.Text(C, value=f"Cell {i},{j}")
    
    # Toggle for row background
    def toggle_row_bg(sender, table=table):
        if sender.value:
            table.flags |= dcg.TableFlag.ROW_BG
        else:
            table.flags &= ~dcg.TableFlag.ROW_BG
    
    dcg.Checkbox(C, label="Alternating Row Backgrounds", 
                 value=True,
                 callback=toggle_row_bg)
    
    # Example of manual row coloring
    dcg.Separator(C)
    dcg.Text(C, value="Manual row coloring example:")
    
    table2 = dcg.Table(C, header=False, flags=dcg.TableFlag.BORDERS)
    for i in range(5):
        with table2.next_row:
            for j in range(3):
                dcg.Text(C, value=f"Cell {i},{j}")
    
    # Set specific colors for each row (increasing alpha)
    for i in range(5):
        opacity = 50 + i * 40  # Increasing opacity
        table2.row_config[i].bg_color = (255, 128, 0, opacity)
    
    dcg.Text(C, value="Each row has manually set background color with increasing opacity")

@demosection(dcg.Table, dcg.TableFlag, dcg.TableElement)
@documented
@democode
def _cell_background(C: dcg.Context):
    """
    ### Cell Background Colors
    
    In addition to row backgrounds, you can customize individual cell backgrounds.
    This is useful for highlighting specific cells or creating visual patterns
    within your table.
    
    There are several ways to set cell background colors:
    
    1. Accessing and modifying the cell's `bg_color` property
    2. Using the dictionary syntax with a "bg_color" key
    3. Creating a `TableElement` directly
    
    Cell background colors take precedence over row background colors.
    """
    # Create a table
    table = dcg.Table(C, header=True, flags=dcg.TableFlag.BORDERS)
    
    # Set column headers
    table.col_config[0].label = "Method 1"
    table.col_config[1].label = "Method 2"
    table.col_config[2].label = "Method 3"
    
    # Add rows
    for i in range(5):
        with table.next_row:
            for j in range(3):
                dcg.Text(C, value=f"Cell {i},{j}")
    
    # Method 1: Get element, modify, set back
    table_element = table[1, 0]
    table_element.bg_color = (255, 0, 0, 100)  # Red with alpha
    table[1, 0] = table_element
    
    # Method 2: Dictionary syntax
    table[2, 1] = {"content": "Colored Cell", "bg_color": (0, 255, 0, 100)}  # Green with alpha
    
    # Method 3: Direct TableElement
    table[3, 2] = dcg.TableElement(C, content="TableElement", bg_color=(0, 0, 255, 100))  # Blue with alpha
    
    # Important note
    dcg.Text(C, value="Important: To modify cell properties, you must get the cell,")
    dcg.Text(C, value="modify it, and set it back. Simply modifying the return value")
    dcg.Text(C, value="of table[i, j].bg_color = ... won't work!")

@demosection(dcg.Table, dcg.TableFlag, dcg.TableColConfig, dcg.ThemeColorImGui)
@documented
@democode
def _combining_colors(C: dcg.Context):
    """
    ### Combining Color Settings
    
    DearCyGui allows multiple levels of color settings to be combined:
    
    1. **Theme colors**: Set by `ROW_BG` flag using TableRowBg/TableRowBgAlt
    2. **Row colors**: Set using `row_config[i].bg_color`
    3. **Cell colors**: Set using cell's `bg_color` property
    
    The precedence order is: Cell > Row > Theme
    
    When alpha values are less than 255, blending occurs between the layers.
    This enables sophisticated visual effects and highlighting.
    """
    dcg.Text(C, value="Demonstrating color precedence and blending:")
    
    # Create table with alternating row backgrounds
    table = dcg.Table(C, header=True, flags=dcg.TableFlag.BORDERS | dcg.TableFlag.ROW_BG)
    
    # Set column headers
    table.col_config[0].label = "Default"
    table.col_config[1].label = "Row Color"
    table.col_config[2].label = "Cell Color"
    table.col_config[3].label = "Row + Cell"
    
    # Set custom theme colors for alternating rows - using more muted colors
    table.theme = dcg.ThemeColorImGui(C,
        TableRowBg=(70, 90, 120),     # Muted blue
        TableRowBgAlt=(80, 100, 80)   # Muted green
    )
    
    # Add rows
    for i in range(6):
        with table.next_row:
            for j in range(4):
                dcg.Text(C, value=f"Cell {i},{j}")
    
    # Apply row colors to even rows - darker red that works with white text
    for i in range(0, 6, 2):
        table.row_config[i].bg_color = (120, 60, 60, 180)  # Semi-transparent darker red
    
    # Apply cell colors to selected cells
    for i in range(6):
        # Apply cell color to column 2
        element = table[i, 2]
        element.bg_color = (90, 80, 130, 180)  # Semi-transparent purple/blue
        table[i, 2] = element
        
        # Apply cell color to column 3 (shows blending with row color)
        element = table[i, 3]
        element.bg_color = (90, 80, 130, 180)  # Same semi-transparent purple/blue
        table[i, 3] = element
    
    # Explanation
    dcg.Text(C, value="Color levels in this example:")
    dcg.Text(C, bullet=True, value="Theme: Alternating light blue/light green rows")
    dcg.Text(C, bullet=True, value="Row: Semi-transparent red on even rows")
    dcg.Text(C, bullet=True, value="Cell: Semi-transparent purple in columns 2 & 3")
    dcg.Text(C, bullet=True, value="Notice the blending effects in column 3 where row and cell colors combine")


@demosection(dcg.Table, dcg.TableFlag, dcg.ThemeList, dcg.ThemeColorImGui, dcg.ThemeStyleImGui)
@documented
@democode
def _table_theme_attributes(C: dcg.Context):
    """
    ### Table Theme Attributes
    
    Tables in DearCyGui can be styled using various theme attributes.
    This demo shows all the theme attributes that affect tables:
    
    - **Text**: Affects header text color
    - **PopupBg**: Background of table context menus and tooltips
    - **ScrollbarBg**: Background color of table scrollbars
    - **ScrollbarGrab**: Color of the scrollbar slider
    - **ScrollbarGrabHovered**: Scrollbar slider color when hovered
    - **ScrollbarGrabActive**: Scrollbar slider color when dragged
    - **TableHeaderBg**: Background color for table headers
    - **TableBorderStrong**: Outer borders and header borders
    - **TableBorderLight**: Inner borders between cells
    - **TableRowBg**: Background color for even rows
    - **TableRowBgAlt**: Background color for odd rows
    
    You can toggle each theme component to see its effect on the table.
    """
    
    # Create a ThemeList to hold all our theme components
    theme_list = dcg.ThemeList(C)
    
    # Create a tall table with scrolling to demonstrate all theme elements
    table = dcg.Table(C, 
                     header=True,
                     height=250,
                     width=500,
                     theme=theme_list,
                     flags=dcg.TableFlag.BORDERS |
                           dcg.TableFlag.ROW_BG |
                           dcg.TableFlag.SCROLL_Y |
                           dcg.TableFlag.SCROLL_X |
                           dcg.TableFlag.RESIZABLE)
    
    # Set up column headers
    for i in range(5):
        table.col_config[i].label = f"Column {i+1}"
    
    # Add rows with enough content to enable scrolling
    for i in range(20):
        for j in range(5):
            table[i, j] = {"content": f"Cell {i+1},{j+1}",
                           "tooltip": f"Tooltip for Cell {i+1},{j+1}"}
        with table.next_row:
            for j in range(5):
                dcg.Text(C, value=f"Cell {i+1},{j+1}")

    
    # Instructions
    dcg.Separator(C)
    dcg.Text(C, value="Toggle theme elements using the checkboxes below:")
    dcg.Text(C, value="Try scrolling, hovering over the scrollbar, and right-clicking the table")
    
    # Helper function to create theme components with a checkbox toggle
    def add_theme_component(name, color, **kwargs):
        # Create theme component with distinctive color
        theme_component = dcg.ThemeColorImGui(C, parent=theme_list, **{name: color})
        
        # Create checkbox to toggle the theme component
        def toggle_theme(sender, component=theme_component):
            component.enabled = sender.value
        
        return dcg.Checkbox(C, label=name, value=True, callback=toggle_theme, **kwargs)
    
    # Create theme components with distinct colors
    with dcg.HorizontalLayout(C):
        with dcg.VerticalLayout(C):
            add_theme_component("Text", (255, 220, 0))  # Gold for header text
            add_theme_component("PopupBg", (20, 60, 30))  # Dark green for popups
            add_theme_component("ScrollbarBg", (30, 30, 30))  # Dark gray for scrollbar bg
            add_theme_component("ScrollbarGrab", (100, 100, 140))  # Medium purple for scrollbar
            add_theme_component("ScrollbarGrabHovered", (120, 120, 180))  # Lighter purple for hovered
        
        with dcg.VerticalLayout(C):
            add_theme_component("ScrollbarGrabActive", (140, 140, 220))  # Bright purple for active
            add_theme_component("TableHeaderBg", (60, 80, 120))  # Medium blue for header bg
            add_theme_component("TableBorderStrong", (200, 200, 255))  # Light lavender for strong borders
            add_theme_component("TableBorderLight", (120, 120, 180))  # Medium lavender for light borders
            add_theme_component("TableRowBg", (50, 70, 90))  # Dark blue for even rows
        
        with dcg.VerticalLayout(C):
            add_theme_component("TableRowBgAlt", (60, 80, 70))  # Dark green for odd rows

pop_group()  # End Styling


if __name__ == "__main__":
    launch_demo(title="Tables Demo")