from os import read
import xml.etree.ElementTree as ET
import csv
import pandas as pd
from sklearn.model_selection import train_test_split

_DIALECT = {}
_DIALECT['delimiter'] = ' '
_DIALECT['lineterminator'] = '\n'#'\r\n'
_DIALECT['escapechar'] = '\\'
csv.register_dialect('NER_data_format', quoting=csv.QUOTE_NONE, delimiter=_DIALECT['delimiter'], lineterminator=_DIALECT['lineterminator'], escapechar=_DIALECT['escapechar'])
_CSV_DIALECT = "NER_data_format"
_USE_IOB2_FORMAT = True
_WRITE_FIELDNAMES = False
_CSV_FIELDNAMES = ['word', 'ner_label']

_SUC_DATA_LOCATION = 'data/suc3.xml'
_NER_FILENAME = 'NER.txt'

_NO_ENTITY_TAG = 'O'
_SAVE_TO_DATA_LOCATION = 'data/'

SUC_to_CONLL = {'person': 'PER',
                'animal': 'PER',
                'myth': 'PER',
                'place': 'LOC',
                'inst': 'ORG',
                'product': 'MISC',
                'work': 'MISC',
                'event': 'MISC',
                'other': 'MISC'
}

class NameKeeper():
    def __init__(self):
        self.nbr_name_tags = 0
        self.SUC_tags = {'person': 0, 
                                 'animal': 0, 
                                 'myth': 0, 
                                 'place': 0, 
                                 'inst': 0, 
                                 'product': 0, 
                                 'work': 0, 
                                 'event': 0, 
                                 'other': 0
                                 }
        self.CONLL_tags = {'LOC': 0,
                           'MISC': 0,
                           'ORG': 0,
                           'PER': 0}

    def get_name_info(self, name_entity):
        # there can be more than one word after a name tag. e.g. Vytautas Landsbergis
        # there can also be ne _overlap within names, we only want the words
        name_entity_rows = []
        name_type = SUC_to_CONLL[name_entity.attrib['type']]
        prefixed_name_type = "B-"+name_type
        for child in name_entity:
            if child.tag == "w":
                name_entity_rows.append([child.text, prefixed_name_type if _USE_IOB2_FORMAT else name_type])
            elif child.tag == "ne":
                for ne_child in child:
                    if ne_child.tag == "w":
                        name_entity_rows.append([ne_child.text, prefixed_name_type if _USE_IOB2_FORMAT else name_type])
                    else:
                        raise ValueError(ne_child.tag)
            else:
                raise ValueError(child.tag)
            prefixed_name_type = "I-"+name_type
            
        self.nbr_name_tags += len(name_entity_rows)
        self.SUC_tags[name_entity.attrib['type']] += len(name_entity_rows)
        self.CONLL_tags[name_type] += len(name_entity_rows)

        return name_entity_rows

def saveNERdataFromSUC():
    # want entity type tags of LOC|MISC|ORG|PER
    # sort of following format described by "Introduction to the CoNLL-2003 Shared Task:
    # Language-Independent Named Entity Recognition"
    
    tree = ET.parse(_SUC_DATA_LOCATION)
    root = tree.getroot()

    print(f"NER data save process started. Saving data to {_SAVE_TO_DATA_LOCATION}...")

    with open (_SAVE_TO_DATA_LOCATION+_NER_FILENAME, 'w') as f:
        writer = csv.writer(f, dialect=_CSV_DIALECT)
        if _WRITE_FIELDNAMES:
            writer.writerow(_CSV_FIELDNAMES)

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
                    writer.writerow([child.text, _NO_ENTITY_TAG])
                elif child.tag == "ne":
                    for subchild in child:
                        if subchild.tag == "name":
                            entity_rows = name_keeper.get_name_info(subchild)
                            writer.writerows(entity_rows)
                        elif subchild.tag == "w":
                            nbr_extra_ne += 1
                            writer.writerow([subchild.text, _NO_ENTITY_TAG])
                        else:
                            # can a ne tag contain anything other than name or word?
                            raise ValueError(sentence_index)
                elif child.tag == "name":
                    nbr_extra_name += 1
                    entity_rows = name_keeper.get_name_info(child)
                    writer.writerows(entity_rows)
                else:
                    raise ValueError(child.tag)
            writer.writerow([])
            num_saved += 1

    print(f"NER data saved! \n{sentence_index} sentences available. \nSaved a total of {num_saved} sentences.")
    print(f"The dataset contains a total of {name_keeper.nbr_name_tags} named entity tokens.")
    print(f"Number of SUC named entity tokens per classification category:")
    [print(f"{category}: {number_of_tokens}") for category, number_of_tokens in name_keeper.SUC_tags.items()]
    print(f"Number of CONLL named entity tokens per classification category:")
    [print(f"{category}: {number_of_tokens}") for category, number_of_tokens in name_keeper.CONLL_tags.items()]
    print(f"There were {nbr_extra_name} name tags not covered by ne tags and {nbr_extra_ne} ne tags not covered by name tags.")

class NER_split_saver():
    def __init__(self, read_filename, write_train_filename, write_eval_filename, write_test_filename):
        f = open(read_filename, 'rt')
        f_train = open(write_train_filename, 'w')
        f_eval = open(write_eval_filename, 'w')
        f_test = open(write_test_filename, 'w')
        
        self.reader = csv.reader(f, dialect=_CSV_DIALECT)
        self.writers = {'train': csv.writer(f_train, dialect=_CSV_DIALECT),
                        'eval': csv.writer(f_eval, dialect=_CSV_DIALECT),
                        'test': csv.writer(f_test, dialect=_CSV_DIALECT)}
        if _WRITE_FIELDNAMES:
            for writer in self.writers.values():
                writer.writerow(_CSV_FIELDNAMES)
        
        default_CONLL_tags = {'LOC': 0,
                                'MISC': 0,
                                'ORG': 0,
                                'PER': 0,
                                'O': 0}
        self.CONLL_tags = {'train': default_CONLL_tags.copy(),
                           'eval': default_CONLL_tags.copy(),
                           'test': default_CONLL_tags.copy()}
        
    def decide_on_state(self, reader_ix, train_ix, eval_ix, test_ix):
        if reader_ix in train_ix:
            return 'train'
        elif reader_ix in test_ix:
            return 'test'
        elif reader_ix in eval_ix:
            return 'eval'
        else:
            raise ValueError(reader_ix)
        
    def save_splits_from_file(self, nbr_sentences, train_ix, eval_ix, test_ix):
            reader_ix = 0
            # skip the first header row
            if _WRITE_FIELDNAMES:
                next(self.reader)
                reader_ix = 1
                
            current_state = self.decide_on_state(reader_ix, train_ix, eval_ix, test_ix)
            for row in self.reader:
                # check for sentence breaks
                if len(row) == 0:
                    self.writers[current_state].writerow(row)
                    reader_ix += 1
                    if reader_ix >= nbr_sentences:
                        break
                    current_state = self.decide_on_state(reader_ix, train_ix, eval_ix, test_ix)
                else:
                    self.writers[current_state].writerow(row)
                    name_type = row[1]
                    if _USE_IOB2_FORMAT:
                        name_type = name_type.strip("B-").strip("I-")
                    self.CONLL_tags[current_state][name_type] += 1
            
def create_splits_from_saved_NER_data(nbr_sentences):
    # skip the header row
    if _WRITE_FIELDNAMES:
        data_ix = range(1,nbr_sentences+1)
    else:
        data_ix = range(nbr_sentences)
    train_ix, test_ix = train_test_split(data_ix, test_size=0.3, random_state=42)
    test_ix, eval_ix = train_test_split(test_ix, test_size=0.33, random_state=42)

    ner_split_saver = NER_split_saver(_SAVE_TO_DATA_LOCATION+_NER_FILENAME, 
                                      _SAVE_TO_DATA_LOCATION+'train_'+_NER_FILENAME, 
                                      _SAVE_TO_DATA_LOCATION+'eval_'+_NER_FILENAME, 
                                      _SAVE_TO_DATA_LOCATION+'test_'+_NER_FILENAME)
    ner_split_saver.save_splits_from_file(nbr_sentences, train_ix, eval_ix, test_ix)

    print(f"NER data splitted!")
    print(f"Created {len(train_ix)} train samples, {len(eval_ix)} eval samples and {len(test_ix)} test samples.")
    print()
    print(f"Entity type distribution over the splitted sets:")
    print(f"TRAIN")
    [print(f"\t{category}: {number_of_tokens}") for category, number_of_tokens in ner_split_saver.CONLL_tags['train'].items()]
    print(f"EVAL")
    [print(f"\t{category}: {number_of_tokens}") for category, number_of_tokens in ner_split_saver.CONLL_tags['eval'].items()]
    print(f"TEST")
    [print(f"\t{category}: {number_of_tokens}") for category, number_of_tokens in ner_split_saver.CONLL_tags['test'].items()]
    

def create_NER_datasets():
    # read the csv data
    text_data = []
    #with open(_SAVE_TO_DATA_LOCATION+_NER_TEXT_FILENAME, 'rb') as f:
    #    reader = csv.reader(f, dialect='_CSV_DIALECT')
    #    for row in reader:
            
    # split it into training, eval and testing (70, 10, 20)?

    # save to files

saveNERdataFromSUC()
create_splits_from_saved_NER_data(74245)