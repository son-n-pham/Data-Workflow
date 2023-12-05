import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Example data
x = [1, 2, 3, 4]
y = [10, 11, 12, 13]

# Create a figure
fig = make_subplots()

# Add trace
fig.add_trace(go.Scatter(x=x, y=y, mode='markers'))

# Function to be called when the plot is clicked


def on_click(trace, points, state):
    for point in points:
        fig.add_annotation(x=point.x, y=point.y,
                           text="Comment",
                           showarrow=True,
                           arrowhead=1)


# Add click event
fig.data[0].on_click(on_click)

# Show plot
fig.show()
