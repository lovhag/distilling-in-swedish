python3 ~/Support_Modules/transformers/examples/token-classification/run_ner_old.py \
--data_dir data/IOB2_splitted_NER \
--model_name_or_path ./bert-model-first \
--labels data/IOB2_splitted_NER/labels.txt \
--output_dir bert-model-first-test \
--max_seq_length 128 \
--seed 1 \
--do_eval \
--do_predict \