import streamlit as st
from user_information import show_user_information
# Import other modules as you create them
from sentiment_analysis import show_sentiment_analysis
from realtime_analysis import show_realtime_analysis
from networking import main

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Applying the custom CSS
local_css("C:/Users/Chethan/Desktop/TweetSight/style.css")

# Display the app name and logo next to each other
col1, col2 = st.columns([2, 3])  # Adjust the ratio as needed

with col1:  # This column is for the app name
    st.markdown('<h1 style="color: blue;">TweetSight</h1>', unsafe_allow_html=True)

with col2:  # This column is for the Twitter bird logo
    st.image("C:/Users/Chethan/Desktop/TweetSight/logo-twitter-png-5871.png", width=50)

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ('User Information', 
                                  'Twitter Sentiment Analysis', 
                                  'Real-time Twitter Sentiment Analysis', 
                                  'Networking with Visualizations'))

if page == 'User Information':
    show_user_information()
elif page == 'Twitter Sentiment Analysis':
     show_sentiment_analysis()
elif page == 'Real-time Twitter Sentiment Analysis':
     show_realtime_analysis()
elif page == 'Networking with Visualizations':
     main()
