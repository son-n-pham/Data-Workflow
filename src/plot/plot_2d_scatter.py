import plotly.express as px
import streamlit as st
from data_wrangle import prepare_data_for_plotting


def plot_2d_scatter(df, x=None, y=None, color=None, size=None, width=800, height=800, marker_size=5, **kwargs):
    columns = [x, y, color, size]
    df_copy = prepare_data_for_plotting(df, columns)

    if df_copy is not None:
        # Plotting
        fig = px.scatter(df_copy, x=x, y=y,
                         color=color, size=size,
                         color_continuous_scale="Viridis",)
        fig.update_traces(marker=dict(size=marker_size))
        fig.update_layout(width=width, height=height)

        # Plotly with Streamlit
        st.plotly_chart(fig)
