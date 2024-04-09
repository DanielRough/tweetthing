import streamlit as st
import pandas as pd
from textblob import TextBlob
from nltk.sentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns
import plotly.express as px
import re

# Sentiment Analysis Function
def sentiment_scores(df, text_field):
    sia = SentimentIntensityAnalyzer()
    
    df['Polarity'] = df[text_field].apply(lambda x: TextBlob(x).sentiment.polarity)
    df['Subjectivity'] = df[text_field].apply(lambda x: TextBlob(x).sentiment.subjectivity)
    
    df['Compound'] = df[text_field].apply(lambda x: sia.polarity_scores(x)['compound'])
    df['Positive'] = df[text_field].apply(lambda x: sia.polarity_scores(x)['pos'])
    df['Negative'] = df[text_field].apply(lambda x: sia.polarity_scores(x)['neg'])
    df['Neutral'] = df[text_field].apply(lambda x: sia.polarity_scores(x)['neu'])
    
    return df

# Data Cleaning Function
def clean_tweet(tweet):
    tweet = re.sub(r"http\S+|www\S+|https\S+", '', tweet, flags=re.MULTILINE)  # Remove URLs
    tweet = re.sub(r'\@w+|\#','', tweet)  # Remove mentions and hashtags
    tweet = re.sub(r'[^\w\s]', '', tweet)  # Remove punctuations
    tweet = tweet.lower()  # Convert to lowercase
    return tweet

def show_sentiment_analysis():
    st.title('Twitter Sentiment Analysis')

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        # Assuming the file has a column named 'tweet'
        df['Cleaned_Tweet'] = df['tweet'].apply(clean_tweet)
        df = sentiment_scores(df, 'Cleaned_Tweet')

        # Showing the table of raw and cleaned tweets
        st.write("Raw and Cleaned Tweets")
        st.dataframe(df[['tweet', 'Cleaned_Tweet']].head(10))

        # Visualization Table
        st.write("Sentiment Analysis Results")
        st.dataframe(df[['Cleaned_Tweet', 'Polarity', 'Subjectivity', 'Positive', 'Negative', 'Neutral', 'Compound']].head(10))
        
        # Pie Chart for Overall Sentiment Distribution
        fig, ax = plt.subplots()
        sentiment_counts = df['Compound'].apply(lambda c: 'positive' if c > 0 else ('negative' if c < 0 else 'neutral')).value_counts()
        ax.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        st.pyplot(fig)

        # Word Cloud
        wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(" ".join(df['Cleaned_Tweet']))
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

        # Polarity Histogram
        fig, ax = plt.subplots()
        sns.histplot(df['Polarity'], bins=20, kde=True, ax=ax)
        ax.set_title('Polarity Distribution')
        ax.set_xlabel('Polarity Score')
        ax.set_ylabel('Frequency')
        st.pyplot(fig)

        # Subjectivity Histogram
        fig, ax = plt.subplots()
        sns.histplot(df['Subjectivity'], bins=20, kde=True, ax=ax)
        ax.set_title('Subjectivity Distribution')
        ax.set_xlabel('Subjectivity Score')
        ax.set_ylabel('Frequency')
        st.pyplot(fig)


        # Interactive Scatter Plot with Plotly
        fig = px.scatter(df, x='Polarity', y='Subjectivity', color=df['Compound'].apply(lambda c: 'Positive' if c > 0 else ('Negative' if c < 0 else 'Neutral')), title="Polarity vs. Subjectivity")
        st.plotly_chart(fig)

    # This ensures the search functionality only appears if there's uploaded file and data frame is not empty.
    if uploaded_file is not None and not df.empty:
        # Search Functionality for Detailed Analysis
        selected_tweet = st.selectbox("Choose a tweet to analyze", df['tweet'])
        if selected_tweet:
            tweet_data = df.loc[df['tweet'] == selected_tweet].iloc[0]
            st.write("Raw Tweet:", tweet_data['tweet'])
            st.write("Cleaned Tweet:", tweet_data['Cleaned_Tweet'])
            st.write("Polarity:", tweet_data['Polarity'])
            st.write("Subjectivity:", tweet_data['Subjectivity'])
            st.write("Sentiments - Positive:", tweet_data['Positive'], ", Negative:", tweet_data['Negative'], ", Neutral:", tweet_data['Neutral'])
            # Explanation based on sentiment
            explanation = "This tweet is considered "
            if tweet_data['Compound'] > 0:
                explanation += "positive due to a higher presence of positively connoted words."
            elif tweet_data['Compound'] < 0:
                explanation += "negative due to a higher presence of negatively connoted words."
            else:
                explanation += "neutral as it does not significantly lean towards positive or negative connotations."
            st.write(explanation)