from .features import Feature
import streamlit as st
import plot
from datetime import datetime

# Assuming this is where prepare_data_for_plotting is defined
from data_wrangle import prepare_data_for_plotting


plot_types = {
    "2D Scatter Plot": ["x", "y", "color", "size"],
    "3D Scatter Plot": ["x", "y", "z", "color", "size"],
    # Add more plot types and their parameters here
}


class GraphFeature(Feature):

    def __init__(self, name: str, parameters: dict = None, plot_type: str = None):
        super().__init__(name, "Graph", "Plots a graph based on the selected parameters", parameters)
        # self.plot_type = plot_type
        self.parameters = parameters or {}

    def execute(self, df, feature_session_state):

        if self.plot_type == "2D Scatter Plot":
            fig = self.plot_2d_scatter(df)
        elif self.plot_type == "3D Scatter Plot":
            fig = self.plot_3d_scatter(df)
        else:
            raise ValueError(f"Unknown plot type: {self.plot_type}")

        return fig

    def select_plot_type(self, feature_session_state):
        # if not self.plot_type:
        #     self.plot_type = list(plot_types.keys())[
        #         0]  # Set to the first key as default

        # if self.activated:
        #     default_plot_type = list(
        #         plot_types.keys()).index(self.plot_type)
        # else:
        #     default_plot_type = 0

        # plot_type = st.radio("Select plot type", list(plot_types.keys(
        # )), default_plot_type, key=f"plot_type_{self.name}_{self.created_at}")

        # return plot_type

        # radio button to select plot type from the list
        # of plot types defined in the plot_types dictionary
        # default value of radio button is 0 if
        # feature_session_state.parameters["plot_type"] is not set
        # otherwise, default value is the index of the
        # feature_session_state.parameters["plot_type"] in the list of plot types
        plot_type = st.radio("Select plot type", list(plot_types.keys()), 0 if feature_session_state.parameters["plot_type"] is None else list(
            plot_types.keys()).index(feature_session_state.parameters["plot_type"]), key=f"plot_type_{self.name}_{self.created_at}")

        return plot_type

    # def set_feature_parameters(self, columns):

    def set_feature_parameters(self, feature_session_state):
        plot_type = self.select_plot_type(feature_session_state)

        plot_columns = plot_types[plot_type]

        selected_columns = {}
        # Create a row of columns
        cols = st.columns(len(plot_columns))

        for i, param in enumerate(plot_columns):
            default_index = feature_session_state.parameters["columns"].index(
                self.parameters[param]) if param in self.parameters and self.parameters[param] in columns else 0
            selected_columns[param] = cols[i].selectbox(
                f"Select {param} column",
                feature_session_state.parameters["columns"],
                index=default_index,
                key=f"{param}_{self.name}_{self.created_at}_{i}"
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
