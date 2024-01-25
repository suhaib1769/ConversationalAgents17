import networkx as nx
import itertools
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from cltl.triple_extraction.api import Chat
from cltl.triple_extraction.cfg_analyzer import CFGAnalyzer
from cltl.triple_extraction.utils.helper_functions import utterance_to_capsules
import time
from transformers import pipeline
import numpy as np
import nltk 
import datetime
import spacy 
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import pandas as pd 
from scipy.spatial.distance import cosine



# create class for contextual memory
class contextualMemory:
    def __init__(self, Agent, User):
        self.graph_memory = nx.Graph()
        self.meta_memory = []
        self.chat = Chat(Agent, User)
        self.analyzer = CFGAnalyzer()

    def add_graph_memory(self, new_triple):
        self.graph_memory = add_and_connect_node2(self.graph_memory, new_triple)

    def add_meta_memory(self, new_meta_data):
        # keep memory at size 5 only, if memory is full, remove the oldest memory
        if len(self.meta_memory) == 5:
            self.meta_memory.pop(0)
        self.meta_memory.append(new_meta_data)
    
    def get_graph_memory(self):
        return self.graph_memory
    
    def get_meta_memory(self):
        return self.meta_memory

 # Download the VADER lexicon
nltk.download('all')
# Create an instance of the SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

# Function to conduct sentiment analysis on a sentence
def analyze_sentiment(sentence):
    sentiment_scores = sia.polarity_scores(sentence)
    return sentiment_scores

def extract_triples1(sentence, chat, analyzer):
    chat = chat
    analyzer = analyzer

    triples = []
    # Get user input
    user_input = sentence

    sentiment = analyze_sentiment(user_input)

    # check if the utterance is a question or statement
    if '?' in user_input:
        utterance_type = 'question'
    else:
        utterance_type = 'statement'


    # Add user utterance to the chat
    chat.add_utterance(user_input)

    # Analyze utterance in context
    analyzer.analyze_in_context(chat)

    # Print triples extracted from the last utterance
    # print(chat.last_utterance.triples)

    # Iterate through each triple and extract the subject, predicate, and object
    for utterance in chat.last_utterance.triples:
        subject_label = utterance['subject']['label'] if 'subject' in utterance and 'label' in utterance['subject'] else "Unknown"
        predicate_label = utterance['predicate']['label'] if 'predicate' in utterance and 'label' in utterance['predicate'] else "Unknown"
        object_label = utterance['object']['label'] if 'object' in utterance and 'label' in utterance['object'] else "Unknown"
        certainty_label = utterance['perspective']['certainty'] if 'perspective' in utterance and 'certainty' in utterance['perspective'] else "Unknown"
        polarity_label = utterance['perspective']['polarity'] if 'perspective' in utterance and 'polarity' in utterance['perspective'] else "Unknown"
        emotion_label = utterance['perspective']['emotion'] if 'perspective' in utterance and 'emotion' in utterance['perspective'] else "Unknown"
        current_time = time.strftime("%H:%M:%S", time.localtime())
        triple_dict = {
            'triple' : (subject_label, predicate_label, object_label),  
            'meta-data': (sentiment['compound'], certainty_label, polarity_label, emotion_label, current_time, utterance_type)
        }
        triples.append(triple_dict)       
    
    return triples

def time_to_seconds(time_str):
    time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S')
    return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second

def encode_label(label):
    # Simple binary encoding for demonstration
    return 1 if label == "statement" else 0

def vectorize_meta_data(item):
    vector = list(item[:4])  # First four numerical values
    vector.append(time_to_seconds(item[4]))  # Convert time to seconds
    vector.append(encode_label(item[5]))  # Encode the label
    # if any of the values are unknown, convert them to 0
    vector = [0 if x == "Unknown" else x for x in vector]
    return vector

# Load the spaCy model
nlp = spacy.load("en_core_web_md")

# Function to calculate cosine similarity using spaCy
def calculate_similarity(str1, str2):
    doc1 = nlp(str1)
    doc2 = nlp(str2)
    return doc1.similarity(doc2)


def add_and_connect_node2(graph, new_triple, similarity_threshold=0.6):
    """
    Adds a new node to the graph and connects it to existing nodes based on similarity.
    If the graph is initially empty, it just adds the node.

    :param graph: The NetworkX graph to which the node is to be added.
    :param new_triple: The new triple to be added as a node.
    :param similarity_threshold: The threshold for cosine similarity to establish an edge.
    """
    # check if the new triple already exists in the graph
    existing_triples = [data['triple'] for _, data in graph.nodes(data=True)]
    if new_triple in existing_triples:
        return graph
    
    # Create a new node ID
    new_node_id = f"Triple_{len(graph.nodes)}"
    graph.add_node(new_node_id, triple=new_triple)

    # If the graph is not empty, attempt to connect the new node to existing nodes
    if len(graph.nodes) == 0:
        # add the first node to the graph
        graph.add_node(new_node_id, triple=new_triple)
    if len(graph.nodes) > 1:
        for existing_node_id, existing_node_data in graph.nodes(data=True):
            if existing_node_id != new_node_id:
                for part_new, part_existing in itertools.product(new_triple, existing_node_data['triple']):
                    if calculate_similarity(part_new, part_existing) > similarity_threshold:
                        print(calculate_similarity(part_new, part_existing))
                        graph.add_edge(new_node_id, existing_node_id)
                        break  # Break if a connection is made to avoid multiple edges between same nodes

    return graph

def graph_extraction(graph, sentence):
     # if graph is empty, return "memory empty"
    if len(graph.nodes) == 0:
        return "memory empty"
    # Modify the function to compare the sentence with the entire triple as a single string
    most_similar_triple = max(graph.nodes(data=True), key=lambda x: calculate_similarity(sentence, ' '.join(x[1]['triple'])))[1]['triple']
    return most_similar_triple

def graph_extraction2(graph, sentence):
    # if graph is empty, return "memory empty"
    if len(graph.nodes) == 0:
        return "memory empty"
    
    highest_similarity = 0
    most_similar_triple = None

    # Iterate over each node in the graph
    for node in graph.nodes(data=True):
        # Concatenate the elements of the triple
        triple_string = ' '.join(node[1]['triple'])
        # remove '-' from the triple string
        triple_string = triple_string.replace('-', ' ')
        
        # Calculate similarity
        similarity = calculate_similarity(sentence, triple_string)

        # Print the two strings and their similarity score
        print(f"Sentence: {sentence}")
        print(f"Triple: {triple_string}")
        print(f"Similarity: {similarity}\n")

        # Check if this is the most similar triple so far
        if similarity > highest_similarity:
            highest_similarity = similarity
            most_similar_triple = node[1]['triple']

    return most_similar_triple if most_similar_triple else "No similar triple found"


def vectorized_meta_data_extraction(meta_data_list, new_meta_data):
    length = len(meta_data_list)
    if length == 0:
        return "memory empty"
    # cosine similarity between the new triple and the vectorized meta-data to find the most similar meta-data
    similarity_scores = [cosine_similarity([meta_data_list[i]], [new_meta_data]) for i in range(length)]
    # find the index of the most similar meta-data
    index = np.argmax(similarity_scores)
    # return the most similar meta-data
    return meta_data_list[index]