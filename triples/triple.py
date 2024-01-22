import networkx as nx
import itertools
from sklearn.feature_extraction.text import CountVectorizer
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

nltk.download('all')

# Create an instance of the SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

# Function to conduct sentiment analysis on a sentence
def analyze_sentiment(sentence):
    sentiment_scores = sia.polarity_scores(sentence)
    return sentiment_scores

def extract_triples1(sentence):
    chat = Chat("Leolani", "Lenka")
    analyzer = CFGAnalyzer()

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
    # remove duplicate triples from the dictionary
    triples = [dict(t) for t in {tuple(d.items()) for d in triples}]
    return triples

def time_to_seconds(time_str):
        time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S')
        return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second

def encode_label(label):
    # Simple binary encoding for demonstration
    return 1 if label == "statement" else 0

def metadata_embedding(triples):
    # store the meta-data in a list
    meta_data = []
    for triple in triples:
        meta_data.append(triple['meta-data'])

    vectorized_data = []
    for item in meta_data:
        vector = list(item[:4])  # First four numerical values
        vector.append(time_to_seconds(item[4]))  # Convert time to seconds
        vector.append(encode_label(item[5]))  # Encode the label
        vectorized_data.append(vector)

    return vectorized_data

def triple_embedding(triples):
    # store all triples in a list
    triple_list = []
    for triple in triples:
        triple_list.append(triple['triple'])
    print(triple_list)

    # Load the spaCy model
    nlp = spacy.load("en_core_web_md")

    # Function to calculate cosine similarity using spaCy
    def calculate_similarity(str1, str2):
        doc1 = nlp(str1)
        doc2 = nlp(str2)
        return doc1.similarity(doc2)

    # Your triples and graph initialization remains the same
    triples = triple_list
    G2 = nx.Graph()
    triple_nodes = {}
    for i, utterance in enumerate(triples):
        node_id = f"Triple_{i}"
        triple_nodes[node_id] = utterance
        G2.add_node(node_id, triple=utterance)

    # Connect triples based on contextual similarity
    similarity_threshold = 0.6
    for node_id1, triple1 in triple_nodes.items():
        for node_id2, triple2 in triple_nodes.items():
            if node_id1 != node_id2:
                for part1, part2 in itertools.product(triple1, triple2):
                    if calculate_similarity(part1, part2) > similarity_threshold:
                        G2.add_edge(node_id1, node_id2)
                        break

    # # Draw the graph
    # nx.draw(G2, with_labels=True)
    # plt.show()
    return triple_list

# add new triple function to knowledge graph
def add_new_triple(triple):
    # get the subject, predicate, and object from the triple
    subject = triple[0]
    predicate = triple[1]
    object = triple[2]

    # check if the subject is already in the graph
    if subject in G.nodes:
        # check if the predicate is already in the graph
        if predicate in G.nodes:
            # check if the object is already in the graph
            if object in G.nodes:
                # add the triple to the graph
                G.add_edge(subject, object, predicate=predicate)
            else:
                # add the object to the graph
                G.add_node(object)
                # add the triple to the graph
                G.add_edge(subject, object, predicate=predicate)
        else:
            # add the predicate to the graph
            G.add_node(predicate)
            # check if the object is already in the graph
            if object in G.nodes:
                # add the triple to the graph
                G.add_edge(subject, object, predicate=predicate)
            else:
                # add the object to the graph
                G.add_node(object)
                # add the triple to the graph
                G.add_edge(subject, object, predicate=predicate)
    else:
        # add the subject to the graph
        G.add_node(subject)
        # check if the predicate is already in the graph
        if predicate in G.nodes:
            # check if the object is already in the graph
            if object in G.nodes:
                # add the triple to the graph
                G.add_edge(subject, object, predicate=predicate)
            else:
                # add the object to the graph
                G.add_node(object)
                # add the triple to the graph
                G.add_edge(subject, object, predicate=predicate)
        else:
            # add the predicate to the graph
            G.add_node(predicate)
            # check if the object is already in the graph
            if object in G.nodes:
                # add the triple to the graph
                G.add_edge(subject, object, predicate=predicate)
            else:
                # add the object to the graph
                G.add_node(object)
                # add the triple to the graph
                G.add_edge(subject, object, predicate=predicate)