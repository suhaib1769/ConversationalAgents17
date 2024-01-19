import intentHelpers as ih

def main(utterance):
    intent = ih.getIntent(utterance)
    slots = ih.getSlots(utterance)

    print("Detected intent: {}".format(intent))
    print("Detected slots: {}".format(slots))

if __name__ == "__main__":
    main()
