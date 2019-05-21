squarify
========
![](https://img.shields.io/pypi/v/squarify.svg?style=flat)
[![Build Status](https://travis-ci.org/laserson/squarify.svg?branch=master)](https://travis-ci.org/laserson/squarify)
![](https://img.shields.io/pypi/pyversions/squarify.svg?style=flat)
![](https://img.shields.io/pypi/l/squarify.svg?style=flat)

Pure Python implementation of the squarify treemap layout algorithm.

Based on algorithm from [Bruls, Huizing, van Wijk, "Squarified Treemaps"](https://doi.org/10.1007/978-3-7091-6783-0_4), but
implements it differently.

Installation
------------

Compatible with Python 2 and Python 3.

    pip install squarify


Usage
-----

The main function is `squarify` and it requires two things:

* A coordinate system comprising values for the origin (`x` and `y`) and the
width/height (`dx` and `dy`).
* A list of positive values sorted from largest to smallest and normalized to
the total area, i.e., `dx * dy`).

The function returns a list of `dict`s (i.e., JSON objects), each one a
rectangle with coordinates corresponding to the given coordinate system and area
proportional to the corresponding value.  Here's an example rectangle:

```json
{
    "x": 0.0,
    "y": 0.0,
    "dx": 327.7,
    "dy": 433.0
}
```

The rectangles can be easily plotted using, for example,
[d3.js](http://d3js.org/).

There is also a version of `squarify` called `padded_squarify` that returns
rectangles that, when laid out, have a bit of padding to show their borders.

The helper function `normalize_sizes` will compute the normalized values, and
the helper function `plot` will generate a Matplotlib-based treemap
visualization of your data (see docstring).


Example
-------
```python
import squarify

# these values define the coordinate system for the returned rectangles
# the values will range from x to x + width and y to y + height
x = 0.
y = 0.
width = 700.
height = 433.

values = [500, 433, 78, 25, 25, 7]

# values must be sorted descending (and positive, obviously)
values.sort(reverse=True)

# the sum of the values must equal the total area to be laid out
# i.e., sum(values) == width * height
values = squarify.normalize_sizes(values, width, height)

# returns a list of rectangles
rects = squarify.squarify(values, x, y, width, height)

# padded rectangles will probably visualize better for certain cases
padded_rects = squarify.padded_squarify(values, x, y, width, height)
```

The variable `rects` contains

```json
[
  {
    "dy": 433,
    "dx": 327.7153558052434,
    "x": 0,
    "y": 0
  },
  {
    "dy": 330.0862676056338,
    "dx": 372.2846441947566,
    "x": 327.7153558052434,
    "y": 0
  },
  {
    "dy": 102.9137323943662,
    "dx": 215.0977944236371,
    "x": 327.7153558052434,
    "y": 330.0862676056338
  },
  {
    "dy": 102.9137323943662,
    "dx": 68.94160077680677,
    "x": 542.8131502288805,
    "y": 330.0862676056338
  },
  {
    "dy": 80.40135343309854,
    "dx": 88.24524899431273,
    "x": 611.7547510056874,
    "y": 330.0862676056338
  },
  {
    "dy": 22.51237896126767,
    "dx": 88.2452489943124,
    "x": 611.7547510056874,
    "y": 410.4876210387323
  }
]
```

The `Rectangle` class is necessary to plot nested treemaps with hierarchical 
data. There are also different, recursive functions to create a nested treemap.

Example
-------

```python
import squarify
import matplotlib.pyplot as plt

# Define a hierarchy of Rectangle objects. In this case, Socks.
socks = [Rectangle('All Socks', children = [
          Rectangle('Blue Socks', value=10), 
          Rectangle('Magenta Fabulous Socks', value=16), 
          Rectangle('Green Socks', value=2), 
          Rectangle('Orange Socks', value=26), 
          Rectangle('Dryer Socks')])]

# A function to supply colors is also required.
def socks_color_and_alpha(rectangle):
    if rectangle.children:
        alpha = 0.25
    else:
        alpha = 1
    
    if rectangle.value == 0:
        color = 'grey'
    elif rectangle.value <= 2:
        color = (3/255, 115/255, 77/255)
    elif rectangle.value <= 10:
        color = (24/255, 102/255, 180/255)
    elif rectangle.value <= 16:
        color = (215/255, 9/255, 71/255)
    elif rectangle.value <= 26:
        color = (204/255, 67/255, 0)
    else:
        color = (1, 1, 1)
    
    return color, alpha

# These values define the coordinate system for the nested rectangles that 
# make up the treemap.
x, y, dx, dy = 0, 0, 100, 100

# The Rectangles must be sorted by their nested sum, which is their own value, 
# and the value of all Rectangles in the list of children. Values must be 
# positive, and the sorted tree is in descending order.
sort_nested(socks)

# Adds a new 'rect' attribute to each Rectangle in the tree. Normalization is 
# included in this function, since the plot area changes at different levels 
# of the hierarchy. Padding is required for the nested treemap to have a 
# sensible plot, and can be specified using the 'pad' parameter of the
# squarify_nested function.
squarify_nested(socks, x, y, dx, dy)

# Set up the figure and axes to plot to.
fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111)

# Plot the tree. The tree hierarchy, plot axis, and color function are 
# required for the plot_nested function to work.
plot_nested(socks, ax, socks_color_and_alpha)

# Adjust some plot parameters.
ax.axis('off')
fig.tight_layout()
```

Sometimes it is useful to be able to plot a known category with an unknown 
value, as with the dryer socks Rectangle. Seriously, where do they go!?

There are also cases where a Rectangle will have a value *and* children.
Let's say, for example, that a researcher administered a survey containing a 
list of mythical creatures, and asked participants to mark all those which 
they had heard of. Not wanting to display all the mythical creatures that 
no one had heard of, he created the following plot.

```python
# Mythical creatures hierarchical tree
mythical_creatures = [Rectangle('All Mythical Creatures', value=25, children = [
                    Rectangle('Well-known Creatures', children = [
                     Rectangle('Minotaur', value=7),
                     Rectangle('Gargoyle', value=15),
                     Rectangle('Dragon', value=10),
                     Rectangle('Phoenix', value=10),
                     Rectangle('Basilisk', value=5),
                     Rectangle('Kraken', value=4)]),
                    Rectangle('Ridable Creatures', children = [
                     Rectangle('Griffin', value=10), 
                     Rectangle('Unicorn', value=10), 
                     Rectangle('Liger', value=5)])])]

def simple_color_and_alpha(rectangle):
    if rectangle.children:
        alpha = 0.25
    else:
        alpha = 1
    
    if rectangle.children:
        color = 'blue'
    else:
        color = 'grey'
    
    return color, alpha

x, y, dx, dy = 0, 0, 100, 100
sort_nested(mythical_creatures)
squarify_nested(mythical_creatures, x, y, dx, dy)
fig = plt.figure(figsize=(10,10))
ax = fig.add_subplot(111)
plot_nested(mythical_creatures, ax, simple_color_and_alpha)
ax.axis('off')
fig.tight_layout()
```

This plot would indicate that there were 25 mythical creatures no one had 
heard of, in addition to those that were familiar to some respondents.