from cltl.triple_extraction.api import Chat
from cltl.triple_extraction.cfg_analyzer import CFGAnalyzer
from cltl.triple_extraction.utils.helper_functions import utterance_to_capsules

chat = Chat("Leolani", "Lenka")
analyzer = CFGAnalyzer()

while True:
    # Get user input
    user_input = input("Enter an utterance (or type 'exit' to quit): ")

    # Check if the user wants to exit the loop
    if user_input.lower() == 'exit':
        print("Exiting the program.")
        break

    # Add user utterance to the chat
    chat.add_utterance(user_input)

    # Analyze utterance in context
    analyzer.analyze_in_context(chat)

    # Get capsules from the last utterance
    capsules = utterance_to_capsules(chat.last_utterance)

    # Print triples extracted from the last utterance
    # print(chat.last_utterance.triples)

    # Iterate through each triple and extract the subject, predicate, and object
    for triple in chat.last_utterance.triples:
        subject_label = triple['subject']['label'] if 'subject' in triple and 'label' in triple['subject'] else "Unknown"
        predicate_label = triple['predicate']['label'] if 'predicate' in triple and 'label' in triple['predicate'] else "Unknown"
        object_label = triple['object']['label'] if 'object' in triple and 'label' in triple['object'] else "Unknown"

        # Print the extracted triple
        print(f"Subject: {subject_label}, Predicate: {predicate_label}, Object: {object_label}")
