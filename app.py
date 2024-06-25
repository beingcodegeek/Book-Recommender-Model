import pickle
import numpy as np
import streamlit as st
from streamlit_lottie import st_lottie
import requests
import urllib.parse

# Load data
popular_df = pickle.load(open('popular.pkl', 'rb'))
pt = pickle.load(open('pt.pkl', 'rb'))
books = pickle.load(open('books.pkl', 'rb'))
similarity_score = pickle.load(open('similarity_scores.pkl', 'rb'))


def recommend(book_name):
    # fetching the index
    try:
        index = np.where(pt.index == book_name)[0][0]
    except IndexError:
        st.error(f"Book '{book_name}' not found in the index.")
        return []

    similar_items = sorted(list(enumerate(similarity_score[index])), key=lambda x: x[1], reverse=True)[1:6]

    recommended_books = []
    for i in similar_items:
        item = {}
        book_title = pt.index[i[0]]
        book_info = books[books['Book-Title'] == book_title]

        if book_info.empty:
            continue

        item['title'] = book_title
        item['author'] = book_info['Book-Author'].values[0]
        item['image_url'] = book_info['Image-URL-M'].values[0]

        # Create Google Books search URL
        query = f"{item['title']} {item['author']}"
        item['link'] = f"https://www.google.com/search?q={urllib.parse.quote(query)}&tbm=bks"

        recommended_books.append(item)

    return recommended_books


def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


# Load Lottie animation
lottie_animation = load_lottieurl("https://lottie.host/da4c00cd-b1dc-4f07-b9ff-f8f502fd08e4/L5eqGNoUdy.json")

# Streamlit app configuration
st.set_page_config(page_title="HobbyHub - Book Recommender", page_icon="📚", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    body {
        background-color: #0e1117;
        color: #ffffff;
    }
    .main {
        background-color: #0e1117;
        padding: 20px;
    }
    .title {
        color: red;
        text-align: center;
        font-size: 3em;
        font-weight: bold;

    }
    .subheader {
        color: yellow;
        text-align: center;
        font-size: 1.5em;
        margin-bottom: 20px;
        text-shadow: 2px 2px 5px red;
    }
    .recommendations {
        margin-top: 30px;
    }
    .book-title a {
        font-size: 1.2em;
        font-weight: bold;
        color: red;
        text-decoration: none;
    }
    .book-author {
        color: #aaaaaa;
    }

    </style>
""", unsafe_allow_html=True)

# Title and Lottie animation
st.markdown("<div class='title'>The Book 📚 Recommender</div>", unsafe_allow_html=True)
st.markdown("<div class='subheader'>Discover your next favorite book!</div>", unsafe_allow_html=True)

if lottie_animation:
    st_lottie(lottie_animation, height=200)

# Dropdown to select a book
st.markdown("### Select a Book")
book_list = popular_df['Book-Title'].values
selected_book = st.selectbox("Type or select a book from the dropdown", book_list)

if st.button('Show Recommendation'):
    with st.spinner('Fetching recommendations...'):
        recommended_books = recommend(selected_book)

    st.write("### Recommended Books")
    st.markdown("<div class='recommendations'>", unsafe_allow_html=True)
    for i in range(0, len(recommended_books), 5):
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            if i + idx < len(recommended_books):
                book = recommended_books[i + idx]
                with col:
                    st.image(book['image_url'], width=100)
                    st.markdown(
                        f"<div class='book-title'><a href='{book['link']}' target='_blank'>{book['title']}</a></div>",
                        unsafe_allow_html=True)
                    st.markdown(f"<div class='book-author'>by {book['author']}</div>", unsafe_allow_html=True)
        # Add padding between rows
        st.markdown("<div style='padding: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# Top 10 Books of All Times section
if 'show_top_books' not in st.session_state:
    st.session_state.show_top_books = False

toggle_label = 'Show Top 10 Books of All Times' if not st.session_state.show_top_books else 'Collapse the Top 10 Books Section'
if st.button(toggle_label):
    st.session_state.show_top_books = not st.session_state.show_top_books

if st.session_state.show_top_books:
    st.write("### Top 10 Books of All Times")
    top_books = popular_df.head(10)  # Assuming popular_df is already sorted by sales or popularity
    for i in range(0, len(top_books), 5):
        cols = st.columns(5)
        for idx, col in enumerate(cols):
            if i + idx < len(top_books):
                book = top_books.iloc[i + idx]
                with col:
                    st.image(book['Image-URL-M'], width=100)
                    st.markdown(f"<div class='book-title'>{book['Book-Title']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='book-author'>by {book['Book-Author']}</div>", unsafe_allow_html=True)
        # Add padding between rows
        st.markdown("<div style='padding: 10px;'></div>", unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: black;
        text-align: center;
        padding: 5px 0;
        color: yellow;
        font-size: 14px;
        text-shadow: 2px 2px 5px red;
    }
    .footer a {
        color: red;
        text-decoration: none;
    }
    </style>
    <div class="footer">
        Made with ❤️ by Sachin <br> Data Source: Book Dataset
    </div>
    """,
    unsafe_allow_html=True
)
