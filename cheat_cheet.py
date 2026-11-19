import streamlit as sl
# from navigation import show_sidebar_navigation
# show_sidebar_navigation()

def home():
    # import os
    # import streamlit as st
    #
    # user = os.environ.get("X_MS_CLIENT_PRINCIPAL_NAME")
    # st.write("Logged in as:", user)

    sl.title('Title')
    sl.header('header')
    sl.subheader('subheader')
    sl.text('Text \nText a kdg ksk')
    sl.markdown('**Bold** Markdown text <br> O hdf sh')
    sl.latex(r'\begin{pmatrix}a&b\\c&d\end{pmatrix}')  # katex.org
    json = {"a": "1,2,3", "b": [1, 2, 3]}
    sl.json(json)
    code_ = """
    print('aaa')
    """
    sl.code(code_, language="python")
    sl.write("## H2")
    sl.metric(label="Wind speed", value=2, delta=1)
    import pandas as pd
    data = {"fruits": ["oranges", "bananas"], "qty": [2, 3]}
    df = pd.DataFrame(data)
    sl.table(df)
    sl.dataframe(df)

    path = r"C:\Users\48575\Downloads\archive (3)\fav\IMG_3390.jpeg"
    sl.subheader("Medias")
    sl.image(path, caption='The image caption', width=300)
    sl.audio(r"C:\Users\48575\Music\Recording0037.mp3")
    sl.video(r'https://www.youtube.com/watch?v=2Myrv3FGPiQ')

    sl.subheader("Checkboxes")
    status_school = sl.checkbox(label="The school  is tomorrow", value=False)
    if status_school:
        sl.text("Yes!")
    else:
        sl.text('Nope')

    def change():
        sl.text('Changes detected')

    status_work = sl.checkbox(label="The work is tomorrow", value=False, on_change=change)

    sl.subheader('Radiobutton')
    status_adult = sl.radio('I am over 18', options=('Yes', 'No', 'I dont know'))
    if status_adult == 'Yes':
        sl.text('Adult')
    else:
        sl.text('No')

    def do_after_click():
        sl.text('OOOOO')

    button_click = sl.button('Click click!', on_click=do_after_click)
    sl.selectbox(label='Whats your fav car?', options=('Audi', 'BMW'))

    sl.multiselect('Whats you fav subject?', options=('Algebra', 'Statistics', 'C'))

    sl.subheader('Upload Files')
    image = sl.file_uploader('Please upload file', type=['png', 'jpg'])
    if image is not None:
        sl.image(image)
    slider = int(sl.slider('Select value', min_value=0, max_value=100))

    sl.text_input('Please enter some text')

    sl.date_input('Enter date')

    import time

    bar = sl.progress(0)

    for i in range(100):
        bar.progress(i + 1)
        time.sleep(0.05)
