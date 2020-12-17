DIRNAME="bert-model-first-train-predictions"
LOG_DIRNAME="model-logdir/${DIRNAME}"

/home/lovhag/miniconda3/envs/distilling-in-swedish-run-ner/bin/python /home/lovhag/projects/transformers/examples/token-classification/run_ner_old_any_model.py \
--data_dir /disk/lovhag/IOB2_splitted_NER \
--model_name_or_path /home/lovhag/bert-model-first \
--labels /disk/lovhag/IOB2_splitted_NER/labels.txt \
--output_dir $DIRNAME \
--logging_dir $LOG_DIRNAME \
--max_seq_length 128 \
--seed 1 \
--num_train_epochs 1 \
--save_steps 5000 \
--evaluation_strategy epoch \
--do_eval \

#default learning rate=5e-5