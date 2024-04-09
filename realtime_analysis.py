import streamlit as st
import pandas as pd
import tweepy
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import re
import nltk
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import seaborn as sns

# Ensure NLTK VADER lexicon is downloaded
nltk.download('vader_lexicon', quiet=True)

def show_realtime_analysis():
    st.title("Real-time Twitter Sentiment Analysis")

    bearer_token = 'AAAAAAAAAAAAAAAAAAAAAI%2B6sgEAAAAA9YKYEQrkhIldk%2Ba28loj12%2BrYLo%3DqNCqiyNA7kp0yqygWGh6kdlsFoMoz67gnBua0V2uakubIfxFVB'
    client = tweepy.Client(bearer_token=bearer_token)

    def clean_tweet(tweet):
        tweet = re.sub(r"http\S+|www\S+|https\S+", '', tweet, flags=re.MULTILINE)
        tweet = re.sub(r'\@\w+|\#','', tweet)
        tweet = tweet.strip().lower()
        return tweet

    hashtags = st.text_input("Enter hashtags :")
    tweet_count = st.slider("Number of Tweets", 10, 100, 50)
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
    end_date = st.date_input("End Date", datetime.now())

    start_date_time = datetime.combine(start_date, datetime.min.time()).isoformat() + "Z"
    end_date_time = datetime.combine(end_date, datetime.max.time()).isoformat() + "Z"

    if st.button("Analyze Tweets") and hashtags:
        query = hashtags.replace(',', ' OR ') + " -is:retweet lang:en"
        tweets_data = []
        for tweet in tweepy.Paginator(client.search_recent_tweets, query=query, tweet_fields=['created_at', 'public_metrics', 'lang', 'text'], max_results=100, start_time=start_date_time, end_time=end_date_time).flatten(limit=tweet_count):
            text = tweet.text
            cleaned_text = clean_tweet(text)
            created_at = tweet.created_at
            likes = tweet.public_metrics['like_count']
            retweets = tweet.public_metrics['retweet_count']
            
            sia = SentimentIntensityAnalyzer()
            sentiment_scores = sia.polarity_scores(cleaned_text)
            compound_score = sentiment_scores['compound']
            sentiment = 'Neutral'
            if compound_score > 0:
                sentiment = 'Positive'
            elif compound_score < 0:
                sentiment = 'Negative'
            
            tweets_data.append([created_at, text, cleaned_text, likes, retweets, compound_score, sentiment])
        
        df = pd.DataFrame(tweets_data, columns=['Date', 'Raw Tweet', 'Cleaned Tweet', 'Likes', 'Retweets', 'Compound', 'Sentiment'])


        if not df.empty:
            visualize_data(df)
        else:
            st.write("No tweets found. Try adjusting your search criteria.")

def visualize_data(df):
    df['Date'] = pd.to_datetime(df['Date']).dt.date  # Format the date

    # Display all details in a table
    st.write("### Detailed Tweet Data")
    st.dataframe(df.assign(hack='').set_index('hack'))  # Trick to show index-less DataFrame

    # Display a focused table with Raw Tweet, Cleaned Tweet, and Sentiment
    st.write("### Tweet Sentiment Analysis")
    sentiment_analysis_df = df[['Raw Tweet', 'Cleaned Tweet', 'Sentiment']]
    st.table(sentiment_analysis_df)


    # Sentiment Distribution Pie Chart
    with st.container():
        st.write("### Sentiment Distribution Pie Chart")
        sentiment_counts = df['Sentiment'].value_counts()
        fig1, ax1 = plt.subplots()
        ax1.pie(sentiment_counts, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)

    # For example, the word cloud visualization
    with st.container():
        st.write("### Word Cloud for Tweets")
        all_tweets = ' '.join(tweet for tweet in df['Cleaned Tweet'])
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_tweets)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)

if __name__ == "__main__":
    show_realtime_analysis()

