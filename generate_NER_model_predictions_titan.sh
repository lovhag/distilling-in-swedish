DIRNAME="bert-model-first-train-word-predictions"
LOG_DIRNAME="model-logdir/${DIRNAME}"

/home/lovhag/miniconda3/envs/distilling-in-swedish-run-ner/bin/python /home/lovhag/projects/transformers/examples/token-classification/generate_model_logits.py \
--data_dir /disk/lovhag/IOB2_splitted_NER \
--model_name_or_path /disk/lovhag/distilling_in_swedish_models/bert-model-first \
--labels /disk/lovhag/IOB2_splitted_NER/labels.txt \
--output_dir $DIRNAME \
--logging_dir $LOG_DIRNAME \
--max_seq_length 128 \
--seed 1 \
--do_eval \

#default learning rate=5e-5
