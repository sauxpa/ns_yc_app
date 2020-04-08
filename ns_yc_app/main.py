import numpy as np
import pandas as pd
from ns_yc import NelsonSiegel

from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Panel
from bokeh.models.widgets import Slider, Tabs, Div
from bokeh.layouts import row, WidgetBox
from bokeh.plotting import figure


def make_dataset(y2, y5, y10, y30, div_):
    """Creates a ColumnDataSource object with data to plot.
    """
    maturities = np.linspace(0.25, 30)

    constraints = dict(zip([2, 5, 10, 30], [y2, y5, y10, y30]))
    NS = NelsonSiegel()
    NS.calibrate(constraints)
    df = pd.DataFrame(
        {
            'maturities': maturities,
            'ytm': NS.ytm(maturities)
        }).set_index('maturities')

    params_text = '<b>Parameters:</b><br><ul\
    ><li>beta_0 = {:.4f}</li>\
    <li>beta_1 = {:.4f}</li>\
    <li>beta_2 = {:.4f}</li>\
    <li>tau = {:.4f}</li>\
    </ul>'.format(NS.b0, NS.b1, NS.b2, NS.tau)
    div_.text = params_text

    df_cstr = pd.DataFrame(columns=['maturities', 'ytm'])
    df_cstr['maturities'] = constraints.keys()
    df_cstr['ytm'] = constraints.values()
    df_cstr = df_cstr.set_index('maturities')

    # Convert dataframe to column data source
    return ColumnDataSource(df), ColumnDataSource(df_cstr)


def make_plot(src, cstr):
    """Create a figure object to host the plot.
    """
    # Blank plot with correct labels
    fig = figure(plot_width=700,
                 plot_height=700,
                 title='Nelson-Siegel Yield Curve model',
                 x_axis_label='Maturities (years)',
                 y_axis_label='YTM',
                 )

    # original function
    fig.line('maturities',
             'ytm',
             source=src,
             color='color',
             legend='Yield Curve model',
             line_color='blue',
             )

    fig.circle('maturities',
               'ytm',
               source=cstr,
               size=5,
               color='red',
               legend='Target yields'
               )

    fig.legend.click_policy = 'hide'
    fig.legend.location = 'bottom_right'
    return fig


def update(attr, old, new):
    """Update ColumnDataSource object.
    """
    # Change n to selected value
    y2 = yield_2_select.value
    y5 = yield_5_select.value
    y10 = yield_10_select.value
    y30 = yield_30_select.value

    # Create new ColumnDataSource
    new_src, new_cstr = make_dataset(y2, y5, y10, y30, div)

    # Update the data on the plot
    src.data.update(new_src.data)
    cstr.data.update(new_cstr.data)


# Slider to select target yields
yield_2_select = Slider(start=-0.5,
                        end=5,
                        step=0.1,
                        value=1.25,
                        title='2y yield (%)'
                        )

yield_5_select = Slider(start=-0.5,
                        end=5,
                        step=0.1,
                        value=1.31,
                        title='5y yield (%)'
                        )

yield_10_select = Slider(start=-0.5,
                         end=5,
                         step=0.1,
                         value=1.5,
                         title='10y yield (%)'
                         )

yield_30_select = Slider(start=-0.5,
                         end=5,
                         step=0.1,
                         value=2.0,
                         title='30y yield (%)'
                         )

# Update the plot when yields are changed
yield_2_select.on_change('value', update)
yield_5_select.on_change('value', update)
yield_10_select.on_change('value', update)
yield_30_select.on_change('value', update)

div = Div(text='<b>Parameters:</b><br>', width=200, height=100)

src, cstr = make_dataset(yield_2_select.value,
                         yield_5_select.value,
                         yield_10_select.value,
                         yield_30_select.value,
                         div,
                         )

fig = make_plot(src, cstr)

controls = WidgetBox(yield_2_select,
                     yield_5_select,
                     yield_10_select,
                     yield_30_select,
                     div,
                     )

# Create a row layout
layout = row(controls, fig)

# Make a tab with the layout
tab = Panel(child=layout, title='Nelson-Siegel')

# ALL TABS TOGETHER
tabs = Tabs(tabs=[tab])

curdoc().add_root(tabs)
