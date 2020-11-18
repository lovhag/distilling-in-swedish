import xml.etree.ElementTree as ET
import csv

_SUC_DATA_LOCATION = 'data/suc3.xml'
_NO_ENTITY_TAG = 'O'
_SAVE_TO_DATA_LOCATION = 'data/'

tree = ET.parse(_SUC_DATA_LOCATION)
root = tree.getroot()

# the NER text data will have the dimensions [nbr_sentences, nbr_words_per_sentence]
NER_text = []
# the NER entity type data will have the dimensions [nbr_sentences, nbr_words_per_sentence]
# each element gives the named entity type for the element
NER_entity_type = []

max_nbr_sentences = 1000

print(f"NER data save process started. Saving data to {_SAVE_TO_DATA_LOCATION}...")

with open (_SAVE_TO_DATA_LOCATION+'NER_text.csv', 'w') as f, open (_SAVE_TO_DATA_LOCATION+'NER_entity_type.csv', 'w') as g, open (_SAVE_TO_DATA_LOCATION+'NER_problem_text.csv', 'w') as h:
    text_writer = csv.writer(f, quoting=csv.QUOTE_NONE, delimiter=',', lineterminator='\r\n', escapechar='\\')
    entity_type_writer = csv.writer(g, quoting=csv.QUOTE_NONE, delimiter=',', lineterminator='\r\n', escapechar='\\')
    problem_text_writer = csv.writer(h, quoting=csv.QUOTE_NONE, delimiter=',', lineterminator='\r\n', escapechar='\\')

    i = 0
    for sentence in root.findall("./text/sentence"):
        sentence_words = []
        sentence_entity_types = []
        have_problematic_sentence = False
        for child in sentence:
            if child.tag == "w":
                sentence_words.append(child.text)
                sentence_entity_types.append(_NO_ENTITY_TAG)
            elif child.tag == "ne":
                sentence_words.append(child.attrib['name'])
                sentence_entity_types.append(child.attrib['type'])
            else:
                have_problematic_sentence = True
                sentence_words.append("<problem>")
                #raise ValueError(child.tag)

        if have_problematic_sentence:
            problem_text_writer.writerow(sentence_words)
        else:
            text_writer.writerow(sentence_words)
            entity_type_writer.writerow(sentence_entity_types)

        i +=1 
        if i>=max_nbr_sentences:
            break

print("NER data saved!")