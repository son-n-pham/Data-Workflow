from .features import Feature
import streamlit as st
import plot
from datetime import datetime

# Assuming this is where prepare_data_for_plotting is defined
from data_wrangle import prepare_data_for_plotting


class GraphFeature(Feature):
    plot_types = {
        "2D Scatter Plot": ["x", "y", "color", "size"],
        "3D Scatter Plot": ["x", "y", "z", "color", "size"],
        # Add more plot types and their parameters here
    }

    def __init__(self, name: str, parameters: dict = None, plot_type: str = None):
        super().__init__(name, "Graph", "Plots a graph based on the selected parameters", parameters)
        self.plot_type = plot_type
        self.parameters = parameters or {}

    def execute(self, df):
        if self.plot_type == "2D Scatter Plot":
            self.plot_2d_scatter(df)
        elif self.plot_type == "3D Scatter Plot":
            self.plot_3d_scatter(df)
        else:
            raise ValueError(f"Unknown plot type: {self.plot_type}")

    def select_plot_type(self):
        self.plot_type = st.radio("Select plot type", list(
            self.plot_types.keys()), key=f"plot_type_{self.name}_{self.created_at}")

    def set_feature_parameters(self, columns):
        selected_columns = {}
        # Create a row of columns
        cols = st.columns(len(self.plot_types[self.plot_type]))

        for i, param in enumerate(self.plot_types[self.plot_type]):
            # Place each select box in a separate column
            if param not in self.parameters:
                selected_columns[param] = cols[i].selectbox(
                    f"Select {param} column", columns, key=f"{param}_{self.name}_{self.created_at}_{i}"
                )
            else:
                default_index = columns.index(
                    self.parameters[param]) if self.parameters[param] in columns else 0
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
            st.plotly_chart(fig)

    def plot_3d_scatter(self, df):
        df_copy = prepare_data_for_plotting(df, [self.parameters['x'], self.parameters['y'], self.parameters['z'],
                                                 self.parameters['color'], self.parameters['size']])

        if df_copy is not None:
            # Call the plot_3d_scatter function from the plot module
            fig = plot.plot_3d_scatter(df_copy, self.parameters)
            st.plotly_chart(fig)

    def to_dict(self):
        data = super().to_dict()
        data["plot_type"] = self.plot_type
        return data

    @classmethod
    def from_dict(cls, data):
        # Create a new GraphFeature object
        feature = cls(
            name=data["name"],
            parameters=data["parameters"],
            plot_type=data["plot_type"]
        )

        # Set the properties of the GraphFeature object based on the values in the dictionary
        feature.description = data["description"]
        feature.created_at = datetime.strptime(
            data["created_at"], "%Y-%m-%dT%H:%M:%S.%f")
        feature.activated = data["activated"]

        return feature
