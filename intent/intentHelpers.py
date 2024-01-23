import numpy as np
from keras.preprocessing.sequence import pad_sequences
# from dataframe import query_restaurants

import pickle
from keras.models import load_model
import pandas as pd

from intent.dataframe import query_restaurants


### CLASSES THAT ABSTRACT THE CLASSIFICATION/LABELLING PROCESS
# a class that takes in encoding/model components and returns the intent of a given text
class SlotLabeller:
    def __init__(self, model, tokenizer, label_list, index_list, max_seq_len):
        self.model = model
        self.tokenizer = tokenizer
        self.label_list = label_list
        self.index_list = index_list
        self.max_seq_len = max_seq_len

    def fill_slots(self, text):
        self.text = [text]
        self.input_seq = self.tokenizer.texts_to_sequences(self.text)
        self.sequence = pad_sequences(self.input_seq, maxlen=self.max_seq_len, padding='post')

        prediction = self.model.predict(self.sequence)
        return [self.label_list[self.index_list.index(j)] for j in [np.argmax(x) for x in prediction[0][:]] if j in self.index_list]
    

# a class that takes in encoding/model components and returns the intent of a given text
class IntentClassifier:
    def __init__(self, classes, model, tokenizer, label_encoder):
        self.classes = classes
        self.classifier = model
        self.tokenizer = tokenizer
        self.label_encoder = label_encoder

    def get_intent(self,text):
        self.text = [text]
        self.test_keras = self.tokenizer.texts_to_sequences(self.text)
        self.test_keras_sequence = pad_sequences(self.test_keras, maxlen=16, padding='post')

        self.pred = self.classifier.predict(self.test_keras_sequence)
        return self.label_encoder.inverse_transform(np.argmax(self.pred,1))[0]
    



### LOAD THE MODELS

# load the intent model
intents_model = load_model('intent/models/intents.keras')

# load the necessary supllementary components
with open('intent/utils/classes.pkl','rb') as file:
    intents_classes = pickle.load(file)

with open('intent/utils/tokenizer.pkl','rb') as file:
    intents_tokenizer = pickle.load(file)

with open('intent/utils/label_encoder.pkl','rb') as file:
    intents_label_encoder = pickle.load(file)


# load the slot labelling model
loaded_model = load_model('intent/models/slotLabelling.keras')

# load the necessary supllementary components
with open('intent/slotLabelModel/tokenizer.pkl','rb') as file:
    slot_tokenizer = pickle.load(file)

with open('intent/slotLabelModel/label_list.pkl','rb') as file:
    slot_label_list = pickle.load(file)

with open('intent/slotLabelModel/index_list.pkl','rb') as file:
    slot_index_list = pickle.load(file)

with open('intent/slotLabelModel/max_seq_length.pkl','rb') as file:
    slot_max_seq_length = pickle.load(file)





# BEHOLD: THE CLASSIFIER
intentClassifier = IntentClassifier(intents_classes, intents_model, intents_tokenizer, intents_label_encoder)


# BEHOLD: THE SLOT LABELLER
slotLabeller = SlotLabeller(loaded_model, slot_tokenizer, slot_label_list, slot_index_list, slot_max_seq_length)



### METHODS
def sample_sentence():
    return "What is a good restaurant to eat in in Spain?"

def getIntent(utterance):
    intent = intentClassifier.get_intent(utterance)
    return intent

def getSlots(utterance):
    slots = slotLabeller.fill_slots(utterance)
    return slots



# mappping from slot labels to query params
slot_label_to_query_param = {
    "served_dish": "Cuisine Style",
    "cuisine": "Cuisine Style",

    "entity_name": "Name",
    "restaurant_name": "Name",

    "city": "City",
    "country": "City",
    "spatial_relation": "City",
    "state": "City",
    "location_name": "City",
    "poi": "City",

    "restaurant_type": None,
    # open to improvement
    "sort": None,
}

# convert the slots to query params
def convert_slots_to_query_params(slots, sentence):
    slot_dict = {}
    current_slot = None
    current_value = None

    for word, slot in zip(sentence.split(), slots):
        if slot.startswith('B-'):
            if current_slot:
                slot_dict[current_slot] = current_value
            current_slot = slot[2:]
            current_value = word
        elif slot.startswith('I-'):
            if current_slot:
                current_value += ' ' + word
        else:
            if current_slot:
                slot_dict[current_slot] = current_value
            current_slot = None
            current_value = None

    if current_slot:
        slot_dict[current_slot] = current_value


    query_params = {}
    for key, value in slot_dict.items():
        if key in slot_label_to_query_param.keys() and slot_label_to_query_param[key]:
            # if slot_label_to_query_param[key] in query_params:
            #     query_params[slot_label_to_query_param[key]].append(value)
            query_params[slot_label_to_query_param[key]] = value

    return query_params



# get the intent and query params from the utterance
def get_query_params(utterance):
    intent = getIntent(utterance)
    slots = getSlots(utterance)

    clean_utterance = "".join((filter(lambda x: x.isalnum() or x.isspace(), utterance)))
    query_params = convert_slots_to_query_params(slots, clean_utterance)

    print("query_params: ", query_params)
    return query_params


# get the restaurants given the query params
def return_restaurants(query_params):
    df = pd.read_csv('intent/TA_restaurants_curated.csv')
    # encode the price range as a number from 1 to 4
    df['Price Range'] = df['Price Range'].replace('$', 1)
    df['Price Range'] = df['Price Range'].replace('$$', 2)
    df['Price Range'] = df['Price Range'].replace('$$ - $$$', 3)
    df['Price Range'] = df['Price Range'].replace('$$$$', 4)
    df['Cuisine Style'] = df['Cuisine Style'].apply(lambda x: eval(x) if pd.notnull(x) else [])
    restaurants = query_restaurants(df, query_params)

    names = restaurants[['Name', 'Price Range', 'Rating', 'City']].apply(lambda row: f"Restaurant called {row['Name']}, price range: {int(row['Price Range'])}, rating: {row['Rating']}, located in the city of {row['City']}", axis=1).tolist()
    return names

            

# meal_suggestion
# resaturant_suggestion
# travel_suggestion


### HOW TO RUN IN SCRIPT
# from intentHelpers import *
# get_query_params(sample_sentence())

# example:
# get_query_params("Find a Greek restaurant in Rotterdam")
# ('restaurant_suggestion', {'Cuisine Style': ['Greek'], 'City': ['Rotterdam']})