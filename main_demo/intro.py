from demo_utils import documented, democode, push_group, pop_group, launch_demo, demosection
from text_utils import MarkDownText
from collections import OrderedDict
import dearcygui as dcg
import numpy as np
import random
import time
import datetime
import os


# decorators:
# - documented: the description (markdown) is displayed
# - democode: the code is displayed and can edited (and run again)
# - demosection: the section is displayed in the table of contents,
#    the section name is extracted from the function name.

        

@demosection
@documented
def _welcome_to_dearcygui(C: dcg.Context):
    """
    # Welcome to DearCygui

    DearCygui is a Python GUI library that allows you to create interactive
    applications with ease.

    It is built on top of:
    * [Cython](https://cython.org/) for code execution
    * [Dear ImGui](https://github.com/ocornut/imgui) for UI rendering
    * [Dear ImPlot](https://github.com/epezent/implot) for plotting
    * [FreeType](https://www.freetype.org/) for font rendering
    * [OpenGL](https://www.opengl.org/) for rendering graphics
    * [SDL3](https://www.libsdl.org/) for window management and input handling
    * [Delaunator](https://github.com/delfrrr/delaunator-cpp) and [Constrainauthor](https://github.com/kninnug/Constrainautor)
        for concave polygon rendering.
    * [The Latin Modern Roman fonts](https://www.gust.org.pl/projects/e-foundry/latin-modern)

    In this demo, we will explore the features of DearCygui and how to use it
    to create interactive applications.
    """
    pass

@demosection
@documented
def _getting_documentation(C: dcg.Context):
    """
    # Getting Documentation

    DearCyGui provides various ways to get documentation:
    - Through typing and autocompletion in your code editor (for instance VSCode)
    - Through the `help` function in Python. `help(dcg.Button)` will display
        the documentation for the Button class.
    - Through the `?` operator in Jupyter notebooks. `dcg.Button?` will display
        the documentation for the Button class.
    - Through the *documentation.py* demo.
    - Through the *docs* folder in the DearCygui repository.
    - Through the various demos in the DearCygui repository.
    """
    pass

@demosection(dcg.Context, dcg.Window, dcg.ChildWindow,
             dcg.Callback, dcg.baseHandler, dcg.baseTheme, dcg.baseFont)
@documented
def _concepts(C: dcg.Context):
    """
    # Concepts

    ## Rendering tree

    In order to render a DearCyGui application, you will assemble a
    tree of objects. At the root of the tree resides the `Viewport`
    object. The `Viewport` object is the main window of the application.

    At each branch of the tree resides a container objects, such as
    `Window`, `ChildWindow`, `VerticalLayout` or `Plot`. The container
    is usually responsible of the layout and rendering bounds of
    its children.

    At the leaf of the tree resides objects such as `Widget` objects,
    drawing objects or plot elements.

    In this tree each item can only appear once. This means that
    each object can only have one parent. Any object that belongs
    to the Viewport's tree may be rendered (if visible).

    During rendering, the tree is traversed in depth-first order. Each
    object is responsible for rendering its children. This means that
    the order of rendering is determined by the order in which the
    objects are added to the tree. The order of rendering is important
    because it determines aspects such as occlusion.

    ## Side objects

    In addition to this tree, various side objects can be attached
    to the items to render. These objects can be
    - Handlers, which are responsible for triggering Python callbacks
        when specific conditions are met.
    - Themes, which are responsible for changing the appearance of
        the objects.
    - Fonts, which are responsible for changing the font of the
        objects.

    These side objects can be attached several times in the tree.

    ## Context

    The `Context` object is an object reference shared by all objects
    in DearCyGui. It can be accessed at all times by reading the
    `context` attribute of any object. It is used to store various
    global states. It must be passed as first argument to all
    objects that are created (except a few minor exceptions).

    ## Callbacks

    Callbacks are functions that are called when specific events
    occur. They are used to trigger actions in response to user
    interactions. Callbacks can be attached to any UI widgets,
    in which case they are triggered when the default item
    interaction occurs. They can also be attached to handlers
    for more complex interactions.

    ## Subclassing

    Subclassing is an important part of DearCyGui programming.
    While it is not mandatory to subclass, it can be a very
    convenient tool to organize your program. All DearCyGui
    objects are subclassable. Here is a small list of ideas
    of what you could do with subclassing:
    - Subclass `Context` in order to attach variables that
       are accessible from all objects.
    - Subclass containers (`ChildWindow`, `Layout`, `DrawingList`, etc)
        and upon creation attach a set of widgets to it.
    - Define the callbacks as methods of your subclass
    - Store important object specific variables or states

    ## Styles

    Styles are used to change the appearance of the objects.
    Many parts of DearCyGui are customizable, in particular
    related to colors and spacings.

    ## Threading

    DearCyGui is fully thread-safe. This means that you can
    create objects and modify them from any thread (except
    the very specific case of custom handlers). Creating
    or modifying objects while rendering is occuring will
    not block rendering, except for the very small section
    where it needs to access the object to render it.

    By default, all callbacks are run in a single secondary thread.
    If you do not want to block your handling of callbacks, try
    to avoid long computations in the callbacks.
    """
    pass

@demosection(dcg.Viewport, dcg.Window, dcg.ViewportDrawList, dcg.MenuBar)
@documented
def _getting_started(C: dcg.Context):
    """
    # Getting Started

    In order to use DearCyGui, you need to import the library
    and create a `Context` object. The `Context` object is the
    main object of DearCyGui. It is responsible for managing
    the rendering tree and the side objects.

    The `Context` object automatically creates a `Viewport` object
    which is accessible through the `viewport` attribute. The window
    is not yet created at this stage. To create it you need to
    call the `initialize` method.

    Widgets can not be attached directly to a `Viewport` object.
    Viewports accept as children `Window`, `ViewportDrawList` or
    `MenuBar` objects.

    The `Window` objects represent a sub-window of the main window.
    To span the entire viewport, you can pass `primary=True` when
    creating the window.

    Here is a small example of how to create a simple application
    with DearCyGui:

    ```python
    import dearcygui as dcg

    # Create a context
    C = dcg.Context()
    C.viewport.initialize()

    # Create a window
    window = dcg.Window(C, label="My Window", width=400, height=300)

    # Rendering loop
    while C.running:
        C.viewport.render_frame()
    ```
    """
    pass

@demosection(dcg.Button)
@documented
@democode
def _how_to_use_this_demo(C: dcg.Context):
    """
    # How to use this demo

    This demo attemps to give an overview of many of the
    tools available in DearCyGui. It features a collection
    of small examples focusing on specific features. They
    are generally accompanied by a short code snippet, as well
    as a few documentation links in the top bar.
    This snippet can be edited through the 'show Source' button.

    The code snippets are executed in a `ChildWindow` that is
    created below the explanation text. The `ChildWindow` is
    specified as default parent using the `with` statement,
    which is why it is not needed to specify the parent
    in the code snippets.

    Try to edit this example:
    """
    def rotate_letters(sender, target, data):
        # sender: the object that triggered the callback
        # target: the object for which the callback is meant
        # data: custom sender data (if any)
        text = target.label
        # rotate the letters of the text
        if len(text) > 0:
            text = text[1:] + text[0]
            target.label = text
        C.viewport.wake()

    # Create a button
    dcg.Button(C, label="Click me",
               width=200, height=50,
               callback=rotate_letters)

@demosection
@documented
def _main_documentation(C: dcg.Context):
    """
    # Main Documentation

    The main documentation is available in the `docs` folder
    of the DearCyGui repository. But to get you covered,
    here it is below:
    """
    base_dir = dcg.__path__[0]
    doc_dir = os.path.join(base_dir, 'docs')
    docs = OrderedDict()
    for doc in os.listdir(doc_dir):
        if doc[-3:] == '.md':
            docpath = os.path.join(doc_dir, doc)
            docname = os.path.basename(doc)[:-3].lower()
            with open(docpath, 'r') as fp:
                text = fp.read()
            docs[docname] = text
    # a bit of reordering :-)
    try:
        docs.move_to_end("themes", last=False)
    except:
        pass
    try:
        docs.move_to_end("drawings", last=False)
    except:
        pass
    try:
        docs.move_to_end("plots", last=False)
    except:
        pass
    try:
        docs.move_to_end("callbacks", last=False)
    except:
        pass
    try:
        docs.move_to_end("UI", last=False)
    except:
        pass
    try:
        docs.move_to_end("basics", last=False)
    except:
        pass
    for text in docs.values():
        MarkDownText(C, value=text)
        # add a separator
        dcg.Separator(C)

if __name__ == "__main__":
    launch_demo(title="Introduction")
