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
    def __init__(self, name, parameters=None, created_at=None, activated=False, plot_type: str = None):
        super().__init__(name=name, feature_type="Graph", description="Plots a graph based on the selected parameters",
                         parameters=parameters or {}, created_at=created_at or datetime.now().isoformat(), activated=activated)

    def execute(self, df):
        if self.plot_type == "2D Scatter Plot":
            fig = self.plot_2d_scatter(df)
        elif self.plot_type == "3D Scatter Plot":
            fig = self.plot_3d_scatter(df)
        else:
            raise ValueError(f"Unknown plot type: {self.plot_type}")

        return fig

    def select_plot_type(self):

        if self.activated:
            default_plot_type = list(
                self.plot_types.keys()).index(self.plot_type)
        else:
            default_plot_type = 0

        self.plot_type = st.radio("Select plot type", list(
            self.plot_types.keys()), default_plot_type, key=f"plot_type_{self.name}_{self.created_at}")

    def set_feature_parameters(self, columns):
        selected_columns = {}
        # Create a row of columns
        cols = st.columns(len(self.plot_types[self.plot_type]))

        for i, param in enumerate(self.plot_types[self.plot_type]):
            default_index = columns.index(
                self.parameters[param]) if param in self.parameters and self.parameters[param] in columns else 0
            selected_columns[param] = cols[i].selectbox(
                f"Select {param} column", columns, index=default_index, key=f"{param}_{self.name}_{self.created_at}_{i}"
            )

        self.parameters = selected_columns

    def plot_2d_scatter(self, df):
        df_copy = prepare_data_for_plotting(df, [self.parameters['x'], self.parameters['y'],
                                                 self.parameters['color'], self.parameters['size']])

        if df_copy is not None:
            # Call the plot_2d_scatter function from the plot module
            fig = plot.plot_2d_scatter(df_copy, self.parameters)
            return fig
            # st.plotly_chart(fig)

    def plot_3d_scatter(self, df):
        df_copy = prepare_data_for_plotting(df, [self.parameters['x'], self.parameters['y'], self.parameters['z'],
                                                 self.parameters['color'], self.parameters['size']])

        if df_copy is not None:
            # Call the plot_3d_scatter function from the plot module
            fig = plot.plot_3d_scatter(df_copy, self.parameters)
            return fig
            # st.plotly_chart(fig)
