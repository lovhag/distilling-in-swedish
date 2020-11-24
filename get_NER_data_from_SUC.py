import xml.etree.ElementTree as ET
import csv

csv.register_dialect('NER_data_format', quoting=csv.QUOTE_NONE, delimiter=',', lineterminator='\r\n', escapechar='\\')

_SUC_DATA_LOCATION = 'data/suc3.xml'
_NO_ENTITY_TAG = 'O'
_SAVE_TO_DATA_LOCATION = 'data/'

def get_name_info(name_entity):
    # there can be more than one word after a name tag. e.g. Vytautas Landsbergis
    # there can also be ne _overlap within names, we only want the words
    name_entity_words = []
    name_entity_types = []
    for child in name_entity:
        if child.tag == "w":
            name_entity_words.append(child.text)
            name_entity_types.append(name_entity.attrib['type'])
        elif child.tag == "ne":
            for ne_child in child:
                if ne_child.tag == "w":
                    name_entity_words.append(ne_child.text)
                    name_entity_types.append(name_entity.attrib['type'])
                else:
                    raise ValueError(ne_child.tag)
        else:
            raise ValueError(child.tag)
    return name_entity_words, name_entity_types

def saveNERdataFromSUC():
    tree = ET.parse(_SUC_DATA_LOCATION)
    root = tree.getroot()

    print(f"NER data save process started. Saving data to {_SAVE_TO_DATA_LOCATION}...")

    with open (_SAVE_TO_DATA_LOCATION+'NER_text.csv', 'w') as f, open (_SAVE_TO_DATA_LOCATION+'NER_entity_type.csv', 'w') as g, open (_SAVE_TO_DATA_LOCATION+'NER_problem_text.csv', 'w') as h:
        text_writer = csv.writer(f, dialect='NER_data_format')
        entity_type_writer = csv.writer(g, dialect='NER_data_format')
        problem_text_writer = csv.writer(h, dialect='NER_data_format')

        num_saved = 0
        nbr_extra_ne = 0
        nbr_extra_name = 0

        sentence_index = 0
        for sentence in root.findall("./text/sentence"):
            sentence_index += 1
            sentence_words = []
            sentence_entity_types = []
            have_problematic_sentence = False
            for child in sentence:
                if child.tag == "w":
                    sentence_words.append(child.text)
                    sentence_entity_types.append(_NO_ENTITY_TAG)
                elif child.tag == "ne":
                    for subchild in child:
                        if subchild.tag == "name":
                            entity_text, entity_type = get_name_info(subchild)
                            sentence_words.extend(entity_text)
                            sentence_entity_types.extend(entity_type)
                        elif subchild.tag == "w":
                            nbr_extra_ne += 1
                        else:
                            # can a ne tag contain anything other than name or word?
                            raise ValueError(sentence_index)
                elif child.tag == "name":
                    nbr_extra_name += 1
                    entity_text, entity_type = get_name_info(child)
                    sentence_words.extend(entity_text)
                    sentence_entity_types.extend(entity_type)
                else:
                    raise ValueError(child.tag)
            num_saved += 1
            text_writer.writerow(sentence_words)
            entity_type_writer.writerow(sentence_entity_types)

    print(f"NER data saved! \n{sentence_index} sentences available. \nSaved a total of {num_saved} sentences.")
    print(f"There were {nbr_extra_name} name tags not covered by ne tags and {nbr_extra_ne} ne tags not covered by name tags.")

saveNERdataFromSUC()