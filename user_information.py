import streamlit as st
import tweepy

def show_user_information():
    st.title('User Information')

    # Inject custom CSS with st.markdown
    st.markdown("""
    <style>
        body {
            font-family: "Arial", sans-serif;
        }
        .user-info {
            margin-bottom: 20px;
        }
        .username {
            color: #1DA1F2;
            font-weight: bold;
            font-size: 20px; /* Slightly larger for emphasis */
        }
        .description, .display-name, .stats, .tweet-text, .tweet-metrics {
            margin-top: 5px;
        }
        .stats, .tweet-metrics {
            font-size: 14px; /* Increased for readability */
            color: #555; /* Slightly darker for better contrast */
        }
        .tweet {
            padding: 15px; /* Increased padding for better spacing */
            margin-top: 15px;
            border-radius: 15px;
            background: #f0f2f6;
            transition: background-color 0.3s ease; /* Smooth transition for hover effect */
        }
        .tweet:hover {
            background-color: #e2e6ea; /* Slightly darker on hover for interactivity */
        }
        .tweet-text {
            font-size: 16px; /* Increased for readability */
        }
    </style>
""", unsafe_allow_html=True)


    # Authentication with Bearer Token
    bearer_token = 'AAAAAAAAAAAAAAAAAAAAAI%2B6sgEAAAAA9YKYEQrkhIldk%2Ba28loj12%2BrYLo%3DqNCqiyNA7kp0yqygWGh6kdlsFoMoz67gnBua0V2uakubIfxFVB'
    client = tweepy.Client(bearer_token=bearer_token)

    user_name = st.text_input('Enter Twitter Username:', '')
    if st.button('Search'):
        user_fields = ['profile_image_url', 'public_metrics', 'description', 'name', 'username']
        tweet_fields = ['public_metrics']
        
        try:
            user = client.get_user(username=user_name, user_fields=user_fields)
            tweets = client.get_users_tweets(id=user.data.id, max_results=5, tweet_fields=tweet_fields)
            
            if user.data:
                user_data = user.data
                metrics = user_data.public_metrics
                
                # Display User Info
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(user_data.profile_image_url, width=100)
                with col2:
                    st.markdown(f'<div class="user-info">', unsafe_allow_html=True)
                    st.markdown(f'<div class="username">@{user_data.username}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="display-name">{user_data.name}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="description">{user_data.description}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="stats">Tweets: {metrics["tweet_count"]} | Followers: {metrics["followers_count"]} | Following: {metrics["following_count"]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                if tweets.data:
                    st.markdown('### Latest Tweets')
                    for tweet in tweets.data:
                        metrics = tweet.public_metrics
                        st.markdown(f'<div class="tweet">', unsafe_allow_html=True)
                        st.markdown(f'<div class="tweet-text">{tweet.text}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="tweet-metrics">Retweets: {metrics["retweet_count"]} | Likes: {metrics["like_count"]} | Replies: {metrics["reply_count"]} | Quotes: {metrics["quote_count"]}</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.write("This user has no tweets.")
                    
        except Exception as e:
            st.error(f"Error fetching data: {e}")

if __name__ == "__main__":
    show_user_information()
