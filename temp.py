import streamlit as st

# Title of the app
st.title('Streamlit App')

# File uploader
uploaded_file = st.file_uploader("Box to upload file")

# Multi-select boxes
option1 = st.multiselect('Box to have multiselect', [
                         'Option A', 'Option B', 'Option C'])
option2 = st.multiselect('Box to have multiselect', [
                         'Option 1', 'Option 2', 'Option 3'])

# Checkboxes for run or not
run_1 = st.checkbox('Run or not', key='1')
run_2 = st.checkbox('Run or not', key='2')

# Proceed button
if st.button('Proceed'):
    st.write('The app will proceed to run...')

# Button to add graph
if st.button('Click to add more graph'):
    # This is where you would add the logic to actually add and display more graphs
    # For demonstration, I'm just showing a text placeholder
    st.write('Graph placeholder')

# Placeholder for graph selection and display
graph_type = st.radio(
    "Select either 2D curve or 3D scatterplot", ('2D Curve', '3D Scatterplot'))

# Display the graph based on the selected type
if graph_type == '2D Curve':
    # Here you would add your 2D curve plotting code
    st.write('2D Curve Graph placeholder')
elif graph_type == '3D Scatterplot':
    # Here you would add your 3D scatterplot plotting code
    st.write('3D Scatterplot Graph placeholder')

# Run the Streamlit app from the command line using:
# streamlit run your_script_name.py
