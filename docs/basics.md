# Starting with **DearCyGui**

## What is **DearCyGui**

**DearCyGui** is a tool
to write *GUI* applications in **Python**.
It is mainly written in **Cython**, thus the name.
**Cython** knowledge is not required and 99% of your
needs should be met using **Python** only.

**Python** is quite handy,
but is not performant enough to render at full frame-rate
complex UIs. The main idea of this library is to create items
and declare how they should behave, and let the library handle
rendering the items and check the conditions you registered for.
The library is written mostly using **Cython** code,
which is converted into efficient **C ++** code and
compiled."

## The Context

The first item you need to create is a *Context*.
```python
    C = dcg.Context()
```

The Context manages the state of your UI items.

## The viewport and the rendering tree

With the Context is attached a single *"Viewport"*.
The Viewport basically corresponds to your application window as seen
by the operating system. It has a title, decoration, etc (this is configurable).
Every frame, rendering starts from the viewport and, in a tree traversal fashion,
all children of the viewport, their children, the children of their children,
etc will be rendered. An item outside of this *rendering* tree can
exist, but will not be rendered. In addition items attached in the rendering tree
can prevent being rendered using the `show` attribute."

Items can be created as soon as the Context is created,
but for anything to be displayed, you need to initialize the viewport.

```python
    C.viewport.initialize()
```

Once attached to the rendering tree, you do not need
to retain a reference to the item for it to remain alive. You can
retain a reference if you want to access later the object, or you
can assign the `tag` field in order to give a name
to your object and later reaccess it by indexing the Context with
the assigned tag.

## Building the rendering tree

To attach an item to another, several options are available.

- You can set the `parent` attribute of your
item to a reference to the parent or its `tag`.

- You can append the item to the `children` attribute of the target parent.

- Using the `with` syntax on the parent
will attach all items inside the `with` to that parent.
```python
        with my_parent_item:
            item = create_my_new_item()
```

- By default items try to attach to a parent unless
`attach=False` is set during item creation.

## Creating an item

All items in **DearCyGui** are built with the following properties:
- *Everything* is properties. Items can be configured by writing to their attributes
at any time, and their current state can be retrieved by reading their attributes.
- All items take the context instance as mandatory positional first argument. You can add more
when subclassing.
- All other arguments of standard **DearCyGui** items (except very few exceptions) are optionnal
keyword arguments. By default all item attributes are set to reasonable default values, and for
most boolean attributes, the default value is `False`. Some exceptions are `show`, or `enabled`
which are set to `True` by default.
- At item creation the default value of the attributes are set, and the keyword arguments are
then converted in a later phase in `__init__` into setting the attributes of the same name (except
very few exceptions for compatibility reasons). It is important to take this into account when
subclassing an object, as you might want to delay (or not) the configuration of the attributes.
Note when subclassing, the attributes are already initialized to the default value when entering
your custom class's `__init__`.
Essentially, the execution flow of item creation when subclassing is

> The Item's memory structure is initialized and values set to the default value
>
> Your `__init__()`
>
> (Optional) At some point in your `__init__` you call the base class `__init__` method
>
> The base class `__init__` iterates on the keyword parameters and tries to set them as attributes.

## Thread safety

Each item is protected by its own mutex instally and it is safe to manipulate items from several threads.
It is possible to lock the internal mutex, but with special care (see `lock_mutex` and the `mutex` attribute).

## Autocompletion

**DearCyGui** provides .pyi files to help linters suggest code completion and show documentation.
This is effective for item names and attributes, but at the time of writing this document, it is
not effective to autocomplete keyword arguments. To know the name of possible keyword arguments,
look at the documentation of the attributes (as keyword arguments are converted into attributes).