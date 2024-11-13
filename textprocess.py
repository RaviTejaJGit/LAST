def process_text(text):
    processed_list = []
    spec_chars=['©','@','&','>','<','â€˜','¢','<< ','>>','â€œ','« ','¢ ']

    for word in text:
        #print(word,"\n")
        if any(char in word for char in spec_chars):
            words = word.split()
            for indi_char in words:
                if not any(char in indi_char for char in spec_chars):
                    processed_list.append(indi_char)
        else:
            processed_list.append(word)

    return processed_list