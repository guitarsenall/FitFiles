
"""
==================
My Ellipse Selector
==================

Do a mouseclick somewhere, move the mouse to some destination, release
the button.  This class gives click- and release-events and also draws
a line or a box from the click-point to the actual mouseposition
(within the same axes) until the button is released.  Within the
method 'self.ignore()' it is checked whether the button from eventpress
and eventrelease are the same.
"""
from matplotlib.widgets import RectangleSelector
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Ellipse


class MyEllipseSelector(RectangleSelector):
    """
    Select an elliptical region of an axes.

    For the cursor to remain responsive you must keep a reference to
    it.

    Example usage::

        import numpy as np
        import matplotlib.pyplot as plt
        from matplotlib.widgets import EllipseSelector

        def onselect(eclick, erelease):
            "eclick and erelease are matplotlib events at press and release."
            print('startposition: (%f, %f)' % (eclick.xdata, eclick.ydata))
            print('endposition  : (%f, %f)' % (erelease.xdata, erelease.ydata))
            print('used button  : ', eclick.button)

        def toggle_selector(event):
            print(' Key pressed.')
            if event.key in ['Q', 'q'] and toggle_selector.ES.active:
                print('EllipseSelector deactivated.')
                toggle_selector.RS.set_active(False)
            if event.key in ['A', 'a'] and not toggle_selector.ES.active:
                print('EllipseSelector activated.')
                toggle_selector.ES.set_active(True)

        x = np.arange(100.) / 99
        y = np.sin(x)
        fig, ax = plt.subplots()
        ax.plot(x, y)

        toggle_selector.ES = EllipseSelector(ax, onselect, drawtype='line')
        fig.canvas.connect('key_press_event', toggle_selector)
        plt.show()
    """
    _shape_klass = Ellipse

    def draw_shape(self, extents):
        x1, x2, y1, y2 = extents
        xmin, xmax = sorted([x1, x2])
        ymin, ymax = sorted([y1, y2])
        center = [x1 + (x2 - x1) / 2., y1 + (y2 - y1) / 2.]
        a = (xmax - xmin) / 2.
        b = (ymax - ymin) / 2.

        if self.drawtype == 'box':
            self.to_draw.center = center
            self.to_draw.width = 2 * a
            self.to_draw.height = 2 * b
        else:
            rad = np.deg2rad(np.arange(31) * 12)
            x = a * np.cos(rad) + center[0]
            y = b * np.sin(rad) + center[1]
            self.to_draw.set_data(x, y)


    @property
    def _rect_bbox(self):
        if self.drawtype == 'box':
            x, y = self.to_draw.center
            width = self.to_draw.width
            height = self.to_draw.height
            return x - width / 2., y - height / 2., width, height
        else:
            x, y = self.to_draw.get_data()
            x0, x1 = min(x), max(x)
            y0, y1 = min(y), max(y)
            return x0, y0, x1 - x0, y1 - y0


def line_select_callback(eclick, erelease):
    'eclick and erelease are the press and release events'
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
    print(" The button you used were: %s %s" % (eclick.button, erelease.button))


def toggle_selector(event):
    print(' Key pressed.')
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print(' RectangleSelector deactivated.')
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print(' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)


fig, current_ax = plt.subplots()                 # make a new plotting range
N = 100000                                       # If N is large one can see
x = np.linspace(0.0, 10.0, N)                    # improvement by use blitting!

plt.plot(x, +np.sin(.2*np.pi*x), lw=3.5, c='b', alpha=.7)  # plot something
plt.plot(x, +np.cos(.2*np.pi*x), lw=3.5, c='r', alpha=.5)
plt.plot(x, -np.sin(.2*np.pi*x), lw=3.5, c='g', alpha=.3)

print("\n      click  -->  release")

# drawtype is 'box' or 'line' or 'none'
toggle_selector.RS = MyEllipseSelector(current_ax, line_select_callback,
                                       drawtype='line', useblit=True,
                                       button=[1, 3],  # don't use middle button
                                       minspanx=5, minspany=5,
                                       spancoords='pixels',
                                       interactive=True)
plt.connect('key_press_event', toggle_selector)
plt.show()
