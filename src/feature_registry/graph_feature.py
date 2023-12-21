from .features import Feature
import streamlit as st
import plot
# from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from typing import List, Dict, Optional

# Assuming this is where prepare_data_for_plotting is defined
from data_wrangle import prepare_data_for_plotting

plot_types = {
    "2D Scatter Plot": ["x", "y", "color", "size"],
    "3D Scatter Plot": ["x", "y", "z", "color", "size"],
    # Add more plot types and their parameters here
}


class GraphFeature(Feature):
    def __init__(self, name, parameters=None, created_at=None, activated=False):
        super().__init__(name=name,
                         feature_type="Graph",
                         description="Plots a graph based on the selected parameters",
                         parameters=parameters or {},
                         created_at=created_at or datetime.now().isoformat(),
                         activated=activated)

    def execute(self, df, cleaned_columns, feature_session_state):
        plot_type, plotted_columns = self.set_feature_parameters(
            cleaned_columns, feature_session_state)

        # Plot button
        button_key_plot = f"plot_{feature_session_state.created_at}_{st.session_state['loaded_count']}"
        plot_clicked = st.button("Plot", key=button_key_plot)

        if plot_clicked:
            self.activated = True
            self.parameters["plot_type"] = plot_type
            self.parameters["plotted_columns"] = plotted_columns

        if self.activated:

            feature_session_state.parameters = self.parameters
            feature_session_state.activated = self.activated

            if self.parameters['plot_type'] == "2D Scatter Plot":
                fig = self.plot_2d_scatter(
                    df, feature_session_state)
            elif self.parameters['plot_type'] == "3D Scatter Plot":
                fig = self.plot_3d_scatter(
                    df, feature_session_state)
            else:
                raise ValueError(
                    f"Unknown plot type: {self.parameters['plot_type']}")

            return fig

    def select_plot_type(self, feature_session_state):

        if self.activated:
            default_plot_type = list(
                plot_types.keys()).index(feature_session_state.parameters["plot_type"])
        else:
            default_plot_type = 0

        plot_type = st.radio("Select plot type", list(
            plot_types.keys()), default_plot_type,
            key=f"plot_type_{feature_session_state.name}_{feature_session_state.created_at}")
        return plot_type

    def set_feature_parameters(self, columns, feature_session_state):
        plot_type = self.select_plot_type(feature_session_state)

        selected_columns = {}
        # Create a columns for holding input columns for plotting
        cols = st.columns(len(plot_types[plot_type]))

        for i, param in enumerate(plot_types[plot_type]):
            default_index = columns.index(
                feature_session_state.parameters[param]) if param in feature_session_state.parameters and feature_session_state.parameters[param] in columns else 0
            selected_columns[param] = cols[i].selectbox(
                f"Select {param} column", columns, index=default_index, key=f"{param}_{self.name}_{self.created_at}_{i}"
            )

        return plot_type, selected_columns

    def plot_2d_scatter(self, df, feature_session_state):
        plotted_columns = feature_session_state.parameters['plotted_columns']
        df_copy = prepare_data_for_plotting(df, [plotted_columns['x'], plotted_columns['y'],
                                                 plotted_columns['color'], plotted_columns['size']])

        if df_copy is not None:
            # Call the plot_2d_scatter function from the plot module
            fig = plot.plot_2d_scatter(
                df_copy, plotted_columns)
            return fig

    def plot_3d_scatter(self, df, feature_session_state):
        plotted_columns = feature_session_state.parameters['plotted_columns']
        df_copy = prepare_data_for_plotting(df, [plotted_columns['x'], plotted_columns['y'], plotted_columns['z'],
                                                 plotted_columns['color'], plotted_columns['size']])

        if df_copy is not None:
            # Call the plot_3d_scatter function from the plot module
            fig = plot.plot_3d_scatter(
                df_copy, plotted_columns)
            return fig
