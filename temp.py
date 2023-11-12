import streamlit as st

# Install Streamlit (if not installed) via command line: pip install streamlit

# Sample data for display purposes
my_dataframe = {'Column1': [1, 2, 3], 'Column2': ['A', 'B', 'C']}
my_image_path = 'path_to_image.png'  # Replace with the path to your image
my_video_path = 'path_to_video.mp4'  # Replace with the path to your video

# Main page layout
st.title('Streamlit Cheat Sheet')

st.markdown('---')

# Display text section
st.header('Display text')
st.text('Fixed width text')
st.markdown('*Markdown*')  # see *
st.caption('Balloons. Hundreds of them...')
st.latex(r''' e^{i\pi} + 1 = 0 ''')
st.write('Most objects')  # dataframe, err, func, keras!
st.code('for i in range(8): foo()')

st.markdown('---')

# Display data section
st.header('Display data')
st.dataframe(my_dataframe)
st.json({'foo': 'bar', 'fu': 'ba'})
st.metric(label="Temperature", value="273 K", delta="-1.2 K")

st.markdown('---')

# Display media section
st.header('Display media')
st.image(my_image_path)
st.audio(my_video_path)
st.video(my_video_path)

# Interactive widgets section
st.header('Display interactive widgets')
st.button('Hit me')
st.checkbox('Check me out')
st.radio('Pick one:', ['None', 'Earl'])
st.selectbox('Select:', [1, 2, 3])
st.multiselect('Multiselect:', [1, 2, 3])
st.slider('Slide me', min_value=0, max_value=10)
st.select_slider('Slide to select', options=[1, '2'])
st.text_input('Enter some text')
st.number_input('Enter a number')
st.text_area('Area for textual entry')
st.date_input('Date input')
st.time_input('Time entry')
st.file_uploader('File uploader')
st.download_button('On the dl', data="text", file_name='sample.txt')
st.camera_input("Take a picture")
st.color_picker('Pick a color')

# Sidebar widgets
st.sidebar.header('Sidebar')
st.sidebar.radio('Choose:', ['Option 1', 'Option 2'])

# Run this script using: streamlit run your_script_name.py
