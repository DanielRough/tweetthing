import streamlit as st
import tweepy
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter

# Initialize Tweepy client for API v2 with Bearer Token
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAI%2B6sgEAAAAA9YKYEQrkhIldk%2Ba28loj12%2BrYLo%3DqNCqiyNA7kp0yqygWGh6kdlsFoMoz67gnBua0V2uakubIfxFVB"

def initialize_tweepy_v2():
    client = tweepy.Client(bearer_token=BEARER_TOKEN)
    return client

def fetch_tweets_by_hashtag(client, hashtag, limit=100):
    query = f"#{hashtag} -is:retweet lang:en"
    tweets = client.search_recent_tweets(query=query, max_results=min(limit, 100),
                                         tweet_fields=['author_id', 'text', 'entities', 'lang'],
                                         user_fields=['username'],
                                         expansions='author_id')
    return tweets

def process_fetched_tweets(tweets):
    # Extracting user details
    users = {u.id: u.username for u in tweets.includes['users']}
    
    tweet_data = []
    for tweet in tweets.data:
        user_name = users[tweet.author_id]
        text = tweet.text
        hashtags = [tag['tag'] for tag in tweet.entities['hashtags']] if 'hashtags' in tweet.entities else []
        tweet_data.append({"User Name": user_name, "Tweet": text, "Hashtags": hashtags})
    
    return tweet_data, users  # Return the mapping of author_id to username as well

def extract_hashtags(tweets):
    hashtags = []
    for tweet in tweets.data:
        if 'entities' in tweet.data and 'hashtags' in tweet.data['entities']:
            hashtags += [tag['tag'] for tag in tweet.data['entities']['hashtags']]
    return hashtags

def build_network_from_tweets(tweets, user_info, graph_type='directed'):
    G = nx.DiGraph() if graph_type == 'directed' else nx.Graph()
    
    for tweet in tweets.data:
        author_id = tweet.author_id
        username = user_info.get(author_id, "Unknown User")  # Safely get username with a default
        G.add_node(username, type='user')  # Use username as the node identifier
        
        if 'entities' in tweet.data and 'hashtags' in tweet.data['entities']:
            for tag in tweet.data['entities']['hashtags']:
                hashtag = tag['tag'].lower()
                G.add_node(hashtag, type='hashtag')
                G.add_edge(username, hashtag)  # Connect using username
                
    return G

def visualize_graph(G, graph_type, hashtag):
    plt.figure(figsize=(12, 12))
    pos = nx.spring_layout(G)

    # Identifying node types
    user_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('type') == 'user']
    hashtag_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('type') == 'hashtag']
    input_hashtag_node = [node for node in hashtag_nodes if node.lower() == hashtag.lower()]

    # Drawing nodes
    nx.draw_networkx_nodes(G, pos, nodelist=user_nodes, node_color='green', node_size=300, label='Users')
    nx.draw_networkx_nodes(G, pos, nodelist=list(set(hashtag_nodes) - set(input_hashtag_node)), node_color='skyblue', node_size=500, label='Hashtags')
    if input_hashtag_node:  # Highlight the input hashtag node in a different color
        nx.draw_networkx_nodes(G, pos, nodelist=input_hashtag_node, node_color='red', node_size=700, label='Input Hashtag')

    # Drawing edges
    nx.draw_networkx_edges(G, pos, arrows=graph_type == 'directed', edge_color='grey')

    # Drawing labels
    nx.draw_networkx_labels(G, pos, font_size=8, font_color='black')

    plt.title(f"Twitter {graph_type.capitalize()} Graph for #{hashtag}")
    plt.axis('off')

    # Adding a legend
    plt.legend(scatterpoints=1, frameon=True, title="Node Types", loc='upper left', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()
    return plt


def main():
    client = initialize_tweepy_v2()

    st.title("Twitter Hashtag Network Analysis")
    graph_type = st.selectbox("Choose the type of graph:", ['directed', 'undirected'])
    hashtag = st.text_input("Enter a hashtag to analyze:")
    limit = st.number_input("Enter the number of tweets to fetch:", min_value=10, max_value=100, value=50)

    if st.button("Fetch and visualize"):
        with st.spinner("Fetching tweets..."):
            tweets = fetch_tweets_by_hashtag(client, hashtag, limit)
            if tweets.data:
                st.success(f"Fetched {len(tweets.data)} tweets containing #{hashtag}.")
                tweet_data, user_info = process_fetched_tweets(tweets)  # Get tweets and user_info
                st.table(tweet_data)
                
                extracted_hashtags = extract_hashtags(tweets)
                hashtag_counts = Counter(extracted_hashtags)
                G = build_network_from_tweets(tweets, user_info, graph_type)  # Pass user_info here
                fig = visualize_graph(G, graph_type, hashtag)
                st.pyplot(fig)

                if graph_type == 'undirected':
                    connected_components = list(nx.connected_components(G))
                    st.write(f"There are {len(connected_components)} connected components in the graph.")
                else:
                    st.write("For directed graphs, connected components are more complex due to the directionality of edges. Instead, consider looking at strongly or weakly connected components.")
            else:
                st.error("No tweets found. Try a different hashtag.")

if __name__ == "__main__":
    main()
