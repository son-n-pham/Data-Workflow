import plotly.express as px
import streamlit as st
from data_wrangle import prepare_data_for_plotting


def plot_3d_scatter(df, x=None, y=None, z=None, color=None, size=None, width=800, height=800, marker_size=5, **kwargs):
    columns = [x, y, z, color, size]
    df_copy = prepare_data_for_plotting(df, columns)

    if df_copy is not None:
        # Plotting
        fig = px.scatter_3d(df_copy, x=x, y=y,
                            z=z, color=color, size=size,
                            color_continuous_scale="Viridis", )
        fig.update_traces(marker=dict(size=marker_size))
        fig.update_layout(width=width, height=height)

        # Update the starting point of each axis to 0
        fig.update_scenes(xaxis=dict(range=[0, df_copy[x].max()]),
                          yaxis=dict(range=[0, df_copy[y].max()]),
                          zaxis=dict(range=[0, df_copy[z].max()]))

        # Plotly with Streamlit
        st.plotly_chart(fig)
