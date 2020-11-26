from os import read
import xml.etree.ElementTree as ET
import csv
import pandas as pd
from sklearn.model_selection import train_test_split

_DIALECT = {}
_DIALECT['delimiter'] = ','
_DIALECT['lineterminator'] = '\n'#'\r\n'
_DIALECT['escapechar'] = '\\'
csv.register_dialect('NER_data_format', quoting=csv.QUOTE_NONE, delimiter=_DIALECT['delimiter'], lineterminator=_DIALECT['lineterminator'], escapechar=_DIALECT['escapechar'])

_SUC_DATA_LOCATION = 'data/suc3.xml'
_NER_TEXT_FILENAME = 'NER_text.csv'
_NER_ENTITY_TYPE_FILENAME = 'NER_entity_type.csv'
_NO_ENTITY_TAG = 'O'
_SAVE_TO_DATA_LOCATION = 'data/'

class NameKeeper():
    def __init__(self):
        self.nbr_name_tags = 0
        self.nbr_per_name_tag = {'person': 0, 
                                 'animal': 0, 
                                 'myth': 0, 
                                 'place': 0, 
                                 'inst': 0, 
                                 'product': 0, 
                                 'work': 0, 
                                 'event': 0, 
                                 'other': 0
                                 }

    def get_name_info(self, name_entity):
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
            
        if len(set(name_entity_types)) > 1:
            # expect to only have one type per name tag
            raise ValueError(name_entity_types)
        
        self.nbr_name_tags += len(name_entity_types)
        self.nbr_per_name_tag[name_entity_types[0]] += len(name_entity_types)

        return name_entity_words, name_entity_types

def saveNERdataFromSUC():
    tree = ET.parse(_SUC_DATA_LOCATION)
    root = tree.getroot()

    print(f"NER data save process started. Saving data to {_SAVE_TO_DATA_LOCATION}...")

    with open (_SAVE_TO_DATA_LOCATION+_NER_TEXT_FILENAME, 'w') as f, open (_SAVE_TO_DATA_LOCATION+_NER_ENTITY_TYPE_FILENAME, 'w') as g:
        text_writer = csv.writer(f, dialect='NER_data_format')
        entity_type_writer = csv.writer(g, dialect='NER_data_format')

        num_saved = 0
        nbr_extra_ne = 0
        nbr_extra_name = 0
        name_keeper = NameKeeper()

        sentence_index = 0
        for sentence in root.findall("./text/sentence"):
            sentence_index += 1
            sentence_words = []
            sentence_entity_types = []
            for child in sentence:
                if child.tag == "w":
                    sentence_words.append(child.text)
                    sentence_entity_types.append(_NO_ENTITY_TAG)
                elif child.tag == "ne":
                    for subchild in child:
                        if subchild.tag == "name":
                            entity_text, entity_type = name_keeper.get_name_info(subchild)
                            sentence_words.extend(entity_text)
                            sentence_entity_types.extend(entity_type)
                        elif subchild.tag == "w":
                            nbr_extra_ne += 1
                        else:
                            # can a ne tag contain anything other than name or word?
                            raise ValueError(sentence_index)
                elif child.tag == "name":
                    nbr_extra_name += 1
                    entity_text, entity_type = name_keeper.get_name_info(child)
                    sentence_words.extend(entity_text)
                    sentence_entity_types.extend(entity_type)
                else:
                    raise ValueError(child.tag)
            num_saved += 1
            text_writer.writerow(sentence_words)
            entity_type_writer.writerow(sentence_entity_types)

    print(f"NER data saved! \n{sentence_index} sentences available. \nSaved a total of {num_saved} sentences.")
    print(f"The dataset contains a total of {name_keeper.nbr_name_tags} named entity tokens.")
    print(f"Number of named entity tokens per classification category:")
    [print(f"{category}: {number_of_tokens}") for category, number_of_tokens in name_keeper.nbr_per_name_tag.items()]
    print(f"There were {nbr_extra_name} name tags not covered by ne tags and {nbr_extra_ne} ne tags not covered by name tags.")

def save_splits_from_file(read_filename, write_train_filename, write_eval_filename, write_test_filename, train_ix, eval_ix, test_ix):
    with open(read_filename, 'rt') as f, open(write_train_filename, 'w') as f_train, open(write_eval_filename, 'w') as f_eval, open(write_test_filename, 'w') as f_test:
        reader = csv.reader(f, dialect='NER_data_format')
        train_writer = csv.writer(f_train, dialect='NER_data_format')
        eval_writer = csv.writer(f_eval, dialect='NER_data_format')
        test_writer = csv.writer(f_test, dialect='NER_data_format')

        reader_ix = 0
        for row in reader:
            if reader_ix in train_ix:
                train_writer.writerow(row)
            elif reader_ix in test_ix:
                test_writer.writerow(row)
            elif reader_ix in eval_ix:
                eval_writer.writerow(row)
            else:
                raise ValueError(reader_ix)
            reader_ix += 1
            
def create_splits_from_saved_NER_data(nbr_sentences):
    data_ix = range(nbr_sentences)
    train_ix, test_ix = train_test_split(data_ix, test_size=0.3, random_state=42)
    test_ix, eval_ix = train_test_split(test_ix, test_size=0.33, random_state=42)

    save_splits_from_file(_SAVE_TO_DATA_LOCATION+_NER_TEXT_FILENAME, 
                          _SAVE_TO_DATA_LOCATION+'train_'+_NER_TEXT_FILENAME, 
                          _SAVE_TO_DATA_LOCATION+'eval_'+_NER_TEXT_FILENAME, 
                          _SAVE_TO_DATA_LOCATION+'test_'+_NER_TEXT_FILENAME, 
                          train_ix, eval_ix, test_ix)

    save_splits_from_file(_SAVE_TO_DATA_LOCATION+_NER_ENTITY_TYPE_FILENAME, 
                          _SAVE_TO_DATA_LOCATION+'train_'+_NER_ENTITY_TYPE_FILENAME, 
                          _SAVE_TO_DATA_LOCATION+'eval_'+_NER_ENTITY_TYPE_FILENAME, 
                          _SAVE_TO_DATA_LOCATION+'test_'+_NER_ENTITY_TYPE_FILENAME, 
                          train_ix, eval_ix, test_ix)

    print(f"NER data splitted!")
    print(f"Created {len(train_ix)} train samples, {len(eval_ix)} eval samples and {len(test_ix)} test samples.")

def create_NER_datasets():
    # read the csv data
    text_data = []
    #with open(_SAVE_TO_DATA_LOCATION+_NER_TEXT_FILENAME, 'rb') as f:
    #    reader = csv.reader(f, dialect='NER_data_format')
    #    for row in reader:
            
    # split it into training, eval and testing (70, 10, 20)?

    # save to files

#saveNERdataFromSUC()
create_splits_from_saved_NER_data(74245)