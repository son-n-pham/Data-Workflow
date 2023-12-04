# plot.py

import plotly.express as px


def plot_2d_scatter(df, plot_params):
    fig = px.scatter(df, x=plot_params['x'], y=plot_params['y'],
                     color=plot_params['color'], size=plot_params['size'],
                     color_continuous_scale="Viridis")
    fig.update_traces(marker=dict(size=plot_params.get('marker_size', 5)))
    fig.update_layout(width=plot_params.get('width', 800),
                      height=plot_params.get('height', 800))
    return fig


def plot_3d_scatter(df, plot_params):
    fig = px.scatter_3d(df, x=plot_params['x'], y=plot_params['y'], z=plot_params['z'],
                        color=plot_params['color'], size=plot_params['size'],
                        color_continuous_scale="Viridis")
    fig.update_traces(marker=dict(size=plot_params.get('marker_size', 5)))
    fig.update_layout(width=plot_params.get('width', 800),
                      height=plot_params.get('height', 800))
    return fig
