# Squarified Treemap Layout
# Implements algorithm from Bruls, Huizing, van Wijk, "Squarified Treemaps"
#   (but not using their pseudocode)


# INTERNAL FUNCTIONS not meant to be used by the user


def pad_rectangle(rect):
    if rect["dx"] > 2:
        rect["x"] += 1
        rect["dx"] -= 2
    if rect["dy"] > 2:
        rect["y"] += 1
        rect["dy"] -= 2


def layoutrow(sizes, x, y, dx, dy):
    # generate rects for each size in sizes
    # dx >= dy
    # they will fill up height dy, and width will be determined by their area
    # sizes should be pre-normalized wrt dx * dy (i.e., they should be same units)
    covered_area = sum(sizes)
    width = covered_area / dy
    rects = []
    for size in sizes:
        rects.append({"x": x, "y": y, "dx": width, "dy": size / width})
        y += size / width
    return rects


def layoutcol(sizes, x, y, dx, dy):
    # generate rects for each size in sizes
    # dx < dy
    # they will fill up width dx, and height will be determined by their area
    # sizes should be pre-normalized wrt dx * dy (i.e., they should be same units)
    covered_area = sum(sizes)
    height = covered_area / dx
    rects = []
    for size in sizes:
        rects.append({"x": x, "y": y, "dx": size / height, "dy": height})
        x += size / height
    return rects


def layout(sizes, x, y, dx, dy):
    return (
        layoutrow(sizes, x, y, dx, dy) if dx >= dy else layoutcol(sizes, x, y, dx, dy)
    )


def leftoverrow(sizes, x, y, dx, dy):
    # compute remaining area when dx >= dy
    covered_area = sum(sizes)
    width = covered_area / dy
    leftover_x = x + width
    leftover_y = y
    leftover_dx = dx - width
    leftover_dy = dy
    return (leftover_x, leftover_y, leftover_dx, leftover_dy)


def leftovercol(sizes, x, y, dx, dy):
    # compute remaining area when dx >= dy
    covered_area = sum(sizes)
    height = covered_area / dx
    leftover_x = x
    leftover_y = y + height
    leftover_dx = dx
    leftover_dy = dy - height
    return (leftover_x, leftover_y, leftover_dx, leftover_dy)


def leftover(sizes, x, y, dx, dy):
    return (
        leftoverrow(sizes, x, y, dx, dy)
        if dx >= dy
        else leftovercol(sizes, x, y, dx, dy)
    )


def worst_ratio(sizes, x, y, dx, dy):
    return max(
        [
            max(rect["dx"] / rect["dy"], rect["dy"] / rect["dx"])
            for rect in layout(sizes, x, y, dx, dy)
        ]
    )


# PUBLIC API


def squarify(sizes, x, y, dx, dy):
    """Compute treemap rectangles.

    Given a set of values, computes a treemap layout in the specified geometry
    using an algorithm based on Bruls, Huizing, van Wijk, "Squarified Treemaps".
    See README for example usage.

    Parameters
    ----------
    sizes : list-like of numeric values
        The set of values to compute a treemap for. `sizes` must be positive
        values sorted in descending order and they should be normalized to the
        total area (i.e., `dx * dy == sum(sizes)`)
    x, y : numeric
        The coordinates of the "origin".
    dx, dy : numeric
        The full width (`dx`) and height (`dy`) of the treemap.

    Returns
    -------
    list[dict]
        Each dict in the returned list represents a single rectangle in the
        treemap. The order corresponds to the input order.
    """
    sizes = list(map(float, sizes))

    if len(sizes) == 0:
        return []

    if len(sizes) == 1:
        return layout(sizes, x, y, dx, dy)

    # figure out where 'split' should be
    i = 1
    while i < len(sizes) and worst_ratio(sizes[:i], x, y, dx, dy) >= worst_ratio(
        sizes[: (i + 1)], x, y, dx, dy
    ):
        i += 1
    current = sizes[:i]
    remaining = sizes[i:]

    (leftover_x, leftover_y, leftover_dx, leftover_dy) = leftover(current, x, y, dx, dy)
    return layout(current, x, y, dx, dy) + squarify(
        remaining, leftover_x, leftover_y, leftover_dx, leftover_dy
    )


def padded_squarify(sizes, x, y, dx, dy):
    """Compute padded treemap rectangles.

    See `squarify` docstring for details. The only difference is that the
    returned rectangles have been "padded" to allow for a visible border.
    """
    rects = squarify(sizes, x, y, dx, dy)
    for rect in rects:
        pad_rectangle(rect)
    return rects


def normalize_sizes(sizes, dx, dy):
    """Normalize list of values.

    Normalizes a list of numeric values so that `sum(sizes) == dx * dy`.

    Parameters
    ----------
    sizes : list-like of numeric values
        Input list of numeric values to normalize.
    dx, dy : numeric
        The dimensions of the full rectangle to normalize total values to.

    Returns
    -------
    list[numeric]
        The normalized values.
    """
    total_size = sum(sizes)
    total_area = dx * dy
    sizes = map(float, sizes)
    sizes = map(lambda size: size * total_area / total_size, sizes)
    return list(sizes)


def plot(
    sizes,
    norm_x=100,
    norm_y=100,
    color=None,
    label=None,
    value=None,
    ax=None,
    pad=False,
    bar_kwargs=None,
    text_kwargs=None,
    **kwargs
):
    """Plotting with Matplotlib.

    Parameters
    ----------
    sizes
        input for squarify
    norm_x, norm_y
        x and y values for normalization
    color
        color string or list-like (see Matplotlib documentation for details)
    label
        list-like used as label text
    value
        list-like used as value text (in most cases identical with sizes argument)
    ax
        Matplotlib Axes instance
    pad
        draw rectangles with a small gap between them
    label
        fontsize of the labels
    bar_kwargs : dict
        keyword arguments passed to matplotlib.Axes.bar
    text_kwargs : dict
        keyword arguments passed to matplotlib.Axes.text
    **kwargs
        Any additional kwargs are merged into `bar_kwargs`. Explicitly provided
        kwargs here will take precedence.

    Returns
    -------
    matplotlib.axes.Axes
        Matplotlib Axes
    """

    import matplotlib.pyplot as plt

    if ax is None:
        ax = plt.gca()

    if color is None:
        import matplotlib.cm
        import random

        cmap = matplotlib.cm.get_cmap()
        color = [cmap(random.random()) for i in range(len(sizes))]

    if bar_kwargs is None:
        bar_kwargs = {}
    if text_kwargs is None:
        text_kwargs = {}
    if len(kwargs) > 0:
        bar_kwargs.update(kwargs)

    normed = normalize_sizes(sizes, norm_x, norm_y)

    if pad:
        rects = padded_squarify(normed, 0, 0, norm_x, norm_y)
    else:
        rects = squarify(normed, 0, 0, norm_x, norm_y)

    x = [rect["x"] for rect in rects]
    y = [rect["y"] for rect in rects]
    dx = [rect["dx"] for rect in rects]
    dy = [rect["dy"] for rect in rects]

    ax.bar(
        x, dy, width=dx, bottom=y, color=color, label=label, align="edge", **bar_kwargs
    )

    if not value is None:
        va = "center" if label is None else "top"

        for v, r in zip(value, rects):
            x, y, dx, dy = r["x"], r["y"], r["dx"], r["dy"]
            ax.text(x + dx / 2, y + dy / 2, v, va=va, ha="center", **text_kwargs)

    if not label is None:
        va = "center" if value is None else "bottom"
        for l, r in zip(label, rects):
            x, y, dx, dy = r["x"], r["y"], r["dx"], r["dy"]
            ax.text(x + dx / 2, y + dy / 2, l, va=va, ha="center", **text_kwargs)

    ax.set_xlim(0, norm_x)
    ax.set_ylim(0, norm_y)

    return ax

# Adaptation to make nested treemaps.

class Rectangle():
    """Rectangle contains data and methods to create a nested treemap.
    The Rectangle object greatly simplifies the recursive calculations 
    required to make a nested treemap.
    
    Parameters
    ----------
    name : string
        The name of the Rectangle.
    value : numeric
        The value of the Rectangle, defaults to 0.
    children (optional) : list or list-like of Rectangle objects
        Defaults to None.
    **kwargs
        Additional data to be stored in the Rectangle. These will be saved as 
        attributes of the Rectangle, i.e. :
            test = Rectangle('test', value=25, children=None, 
                             **{'a':1, 'b':2, 'c':3})
            
            will store the values 'a', 'b', and 'c' as accessible attributes:
            Rectangle.a = 1
            Rectangle.b = 2
            Rectangle.c = 3
            
            This is useful when a second attribute is used to set the color of 
            the Rectangle when it is plotted, or to quickly change what value 
            is used to sum, normalize, and sort the Rectangle for plotting.
            
            See the Rectangle.change_value method for more details.
    """
    
    def __init__(self, name, value=0, children=None, **kwargs):
        self.name = name
        self.value = value
        self.children = children
        self.nsum = None
        
        not_allowed = ('nested_sum', 'sort_children', 'sort_all_children', 
                       'normalize', 'normalize_children')
        for k, v in kwargs.items():
            if k in not_allowed:
                raise TypeError(('{} is a method of the Rectangle class and '
                                 'cannot be used as an attribute name.').format(k))
            else:
                setattr(self, k, v)
    
    def __str__(self):
        return "name = {}, value = {}, nested_sum = {}". \
            format(self.name, self.value, self.nested_sum())
    
    def change_value(self, attr):
        """Changes the value used for summing, normalizing, and sorting.
        
        Parameters
        ----------
        attr : string or numeric
            If string, must be the name of an existing attribute. 
        """
        if isinstance(attr, str):
            self.value = getattr(self, attr)
        else:
            self.value = attr
        
    def change_all_values(self, attr):
        """Changes the Rectangle's value used for summing, normalizing, and 
        sorting, and all its children, recursively.
        
        Parameters
        ----------
        attr : string or numeric
            If string, must be the name of an existing attribute.
        """
        self.change_value(attr)
        if self.children:
            for c in self.children:
                c.change_all_values(attr)
    
    def nested_sum(self, force=False):
        """Calculates the sum of the current Rectangle, and all child 
        Rectangles, recursively.
        If the current Rectangle has no children and no value, returns 1. This 
        is useful for cases when a child is known to exist, but no information 
        is known about its value.
        
        Parameters
        ----------
        force (optional) : boolean
            The nested sum is saved as the attribute Rectangle.nsum and is 
            recalled as long as nsum != None and force == False. That way the 
            nested sum is only calculated once for each Rectangle. The nested 
            sum can be forced to recalculate, instead of recalling the nsum 
            attribute, by setting force = True. Defaults to False.
            
            If you change the values of the elements of a Rectangle tree that 
            has already been sorted and plotted, make sure you are changing 
            the element that you REALLY want (since they move around during 
            the sort), and make sure to force a new nested sum on the whole 
            tree!
        
        Returns
        -------
        numeric
            Sum of the parent and all child Rectangles.
        """
        if self.nsum != None and not force:
            value = self.nsum
        elif self.children:
            value = self.value + sum(r.nested_sum(force = force) 
                                     for r in self.children)
            self.nsum = value
        else:
            value = self.value
            self.nsum = value
        
        if value == 0:
            return 1
        else:
            return value
    
    def sort_children(self):
        """Sorts the immediate children of the current Rectangle in descending 
        order by their nested sums.
        
        Parameters
        ----------
        N/A
        """
        if self.children:
            self.children.sort(key=lambda r: r.nested_sum(), reverse=True)
    
    def sort_all_children(self):
        """Sorts all children of the current Rectangle recursively in 
        descending order by their nested sums.
        
        Parameters
        ----------
        N/A
        """
        if self.children:
            self.sort_children()
            for c in self.children:
                c.sort_all_children()
    
    def normalize(self, total_size, total_area):
        """Normalize the nested sum of the current Rectangle.
        More useful when used with normalize_nested inside the squarify_nested 
        function where the size of the plot area changes as you recurse down 
        the tree.
        
        Parameters
        ----------
        total_size : numeric
            The sum of the nested sums of this Rectangle's value and all other 
            Rectangle's values on the same level of the tree, .
        total_area : numeric
            The size of the area to plot on.
        
        Returns
        -------
        None, but adds nvalue as a new attribute of the Rectangle.
        """
        self.nvalue = self.nested_sum() * total_area / total_size
    
    def normalize_children(self, total_size, total_area):
        """Normalize the nested sum of the current Rectangle, and all child 
        Rectangles, recursively.
        
        Parameters
        ---------
        N/A
        
        Returns
        -------
        None, but adds nvalue as a new attribute of the Rectangle.
        """
        self.normalize(total_size, total_area)
        if self.children:
            for c in self.children:
                c.normalize_children(total_size, total_area)

def change_nested(tree, attr):
    """Change the value used by each Rectangle in the tree.
    
    Parameters
    ----------
    tree : list of nested Rectangle instances
    attr : string
        If string, must be the name of an existing attribute on all Rectangles.
    """
    for r in tree:
        r.change_all_values(attr)

def force_nested_sum(tree):
    """Force the calculation of the nested sum of all Rectangles in a tree.
    
    Parameters
    ----------
    tree : list of nested Rectangle instances
    """
    for r in tree:
        r.nested_sum(force=True)

def sort_nested(tree):
    """Sort a tree of nested Rectangle objects.
    Rectangles are sorted based on their nested sum, which is the sum of the 
    parent rectangle value and the value of all other rectangles nested 
    underneath it.
    
    Parameters
    ----------
    tree : list of nested Rectangle instances
    
    Returns
    -------
    None, sorts in place.
    """
    for r in tree:
        r.sort_all_children()

def normalize_nested(tree, dx, dy):
    """Normalizes a tree of Rectangles.
    Normalizes a whole tree to the whole plot size. More useful within the 
    squarify_nested function where the area changes as you recurse down the 
    tree.
    
    Parameters
    ----------
    tree : list of nested Rectangle instances
    dx, dy : numeric
        The dimensions of the full rectangle to normalize total values to.
    
    Returns
    -------
    None, but adds the result to the instance as the Rectangle.nvalue attribute
    """
    total_size = sum(r.nested_sum() for r in tree)
    total_area = dx * dy
    for r in tree:
        r.normalize(total_size, total_area)

def squarify_nested(tree, x, y, dx, dy, pad=(2,5)):
    """Compute nested treemap rectangles.
    Given a nested hierarchy of Rectangles, where the highest level is a list, 
    calculates a nested treemap layout using sqarify. Rectangles can have both 
    values and children.
    
    Parameters
    ----------
    tree : list of nested Rectangle instances
        The values of each rectangle must be positive, and the tree must be 
        sorted in descending order. Normalization occurs within this function.
    x, y : numeric
        The coordinates of the "origin".
    dx, dy : numeric
        The full width ('dx') and height ('dy') of the treemap.
    pad (optional) : 2-tuple (x-pad, y-pad), or 4-tuple (lpad, rpad, bpad, tpad)
        If pad is a 2-tuple, then the nested rectangles will be centered 
        parallel to the x-axis, but bottom aligned parallel to the y-axis. 
        This is useful when a title or other text is required.
        
        If pad is a 4-tuple, then the nested rectangles will be padded from 
        the left, right, bottom, and top as entered.
    
    Returns
    -------
    None, but adds the output from squarify to the instance as the 
    Rectangle.rect attribute.
    """
    
    # Set up padding.
    if len(pad) == 2:
        lpad, rpad, bpad, tpad = pad[0]/2, pad[0], 1, pad[1]-1
    elif len(pad) == 4:
        lpad, rpad, bpad, tpad = pad[0], pad[0]+pad[1], pad[2], pad[2]+pad[3]
    else:
        raise ValueError("Invalid pad argument.")
    
    # Calculate rectangles for this layer of the tree.
    normalize_nested(tree, dx, dy)
    t = [r.nvalue for r in tree]
    rects = squarify(t, x, y, dx, dy)
    
    # Calculate rectangles for the next layer of the tree. Includes padding, 
    # and can handle rectangles where the parent has its own value.
    for rect, r in zip(rects, tree):
        r.rect = rect
        if r.children and r.value != 0:
            
            normal_pad_area = (lpad + rpad) * rect['dy'] + \
                                (tpad + bpad) * (rect['dx']-(lpad + rpad))
            area_of_rect_value = r.value * (dx * dy) / r.nested_sum()
            
            if area_of_rect_value <= normal_pad_area:
                squarify_nested(r.children, rect['x']+lpad, rect['y']+bpad, 
                                rect['dx']-rpad, rect['dy']-tpad)
            else:
                
                ratio = (r.nvalue - area_of_rect_value) / r.nvalue
                dx = rect['dx'] * ratio
                dy = rect['dy'] * ratio
                x = rect['x'] + (rect['dx'] - dx)/2
                y = rect['y'] + (rect['dy'] - dx)/2
                squarify_nested(r.children, x, y, dx, dy)
        
        elif r.children:
            squarify_nested(r.children, rect['x']+lpad, rect['y']+bpad, 
                            rect['dx']-rpad, rect['dy']-tpad)

def plot_nested(tree, ax, color_and_alpha):
    """Plotting with matplotlib.
    
    Parameters
    ----------
    tree : list of nested Rectangle instances
        Must already be normalized and squarified.
    ax : matplotlib axis to plot to
    color_and_alpha : function
        Function used to determine the color and alpha of each Rectangle in 
        the tree.
    """
    for r in tree:
        x, y, dx, dy = r.rect['x'], r.rect['y'], r.rect['dx'], r.rect['dy']
        
        # Color and alpha
        color, alpha = color_and_alpha(r)
        ax.bar(x=x, height=dy, width=dx, bottom=y, align='edge', edgecolor='k', 
               color=color, alpha=alpha)
        
        # Label
        rotation = 90 if dx < 5 else 0
        label = "{0}\n{1}".format(r.name[:-6],r.name[-6:]) if rotation == 0 \
                    and dx < 10 else r.name
        ax.text(x + dx/2, y-0.5 + dy, label, va='top', ha='center', 
                rotation=rotation)
        
        # Value
        if r.value == 0:
            value = ""
        else:
            value = r.value
        ax.text(x + dx/2, y-2.5 + dy, value, va='top', ha='center')
        
        if r.children:
            plot_nested(r.children, ax, color_and_alpha)