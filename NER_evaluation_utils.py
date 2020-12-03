import sys
from seqeval.metrics import classification_report as classification_report_seqeval

#load test set and predictions for it

def read_examples_from_file(file_path):
    with open(file_path, 'r') as f:
        examples = {"words": [], "labels": []}
        words = []
        labels = []
        
        for line in f:
            if line.startswith("-DOCSTART-") or line == "" or line == "\n":
                if words:
                    examples["words"].append(words)
                    examples["labels"].append(labels)
                    words = []
                    labels = []
            else:
                splits = line.split(" ")
                words.append(splits[0])
                if len(splits) > 1:
                    labels.append(splits[-1].replace("\n", ""))
                else:
                    # Examples could have no label for mode = "test"
                    labels.append("O")
    return examples

def get_matched_examples(examples_to_match, reference_examples):
    matched_examples = {"words": [], "labels": []}
    nbr_not_matching = 0
    assert len(examples_to_match["words"]) == len(examples_to_match["labels"])
    assert len(examples_to_match["words"]) == len(reference_examples["words"])
    
    for index in range(len(examples_to_match["words"])):
        true_len = len(examples_to_match["words"][index])
        pred_len = len(reference_examples["words"][index])
        if not true_len == pred_len:
            nbr_not_matching += 1
            matched_example_word = examples_to_match["words"][index][:pred_len]
            matched_example_label = examples_to_match["labels"][index][:pred_len]
        else:
            matched_example_word = examples_to_match["words"][index]
            matched_example_label = examples_to_match["labels"][index]
            
        assert matched_example_word == reference_examples["words"][index]
        matched_examples["words"].append(matched_example_word)
        matched_examples["labels"].append(matched_example_label)
        
    #assert matched_examples == reference_examples
    print(f"Found {nbr_not_matching} examples not matching in length.")
    return matched_examples

def print_classification_report_to_file(filename, y_true, y_pred):
    original_stdout = sys.stdout # Save a reference to the original standard output

    with open(filename, 'w') as f:
        sys.stdout = f # Change the standard output to the file we created.
        print(classification_report_seqeval(y_true, y_pred))
        sys.stdout = original_stdout # Reset the standard output to its original value
    
    
def generate_classification_report_to_file(test_file_path, predictions_file_path, print_to_file_path):
    true_examples = read_examples_from_file(test_file_path)
    pred_examples = read_examples_from_file(predictions_file_path)
    matched_true_examples = get_matched_examples(true_examples, pred_examples)
    print_classification_report_to_file(print_to_file_path, 
                                        matched_true_examples["labels"],
                                        pred_examples["labels"])
    
def get_error_indeces(max_nbr_samples, y_true, y_pred):
    error_indeces = []
    for index in range(len(y_true)):
        if not y_true[index] == y_pred[index]:
            error_indeces.append(index)
            if len(error_indeces) >= max_nbr_samples:
                return error_indeces
    return error_indeces
    
def print_error_sentences_to_file(filename, error_indeces, true_examples, pred_examples):
    with open(filename, 'w') as f:
        for index in error_indeces:
            for word_index in range(len(true_examples["words"][index])):
                f.write((" ").join([true_examples["words"][index][word_index], 
                                    true_examples["labels"][index][word_index], 
                                    pred_examples["labels"][index][word_index]]))
                f.write("\n")
            f.write("\n")      
def generate_error_sentences_to_file(test_file_path, predictions_file_path, print_to_file_path):
    true_examples = read_examples_from_file(test_file_path)
    pred_examples = read_examples_from_file(predictions_file_path)
    matched_true_examples = get_matched_examples(true_examples, pred_examples)
    error_indeces = get_error_indeces(20, matched_true_examples["labels"], pred_examples["labels"])
    
    print_error_sentences_to_file(print_to_file_path, error_indeces, true_examples, pred_examples)


test_file_path = "data/IOB2_splitted_NER/test.txt"
predictions_file_path = "bert-model-first-test/test_predictions.txt"

# generate_classification_report_to_file(test_file_path, 
#                                        predictions_file_path, 
#                                        "bert-model-first-test/classification_report.txt")

generate_error_sentences_to_file(test_file_path, predictions_file_path, "bert-model-first-test/error_sentences.txt")
