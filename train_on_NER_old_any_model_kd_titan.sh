DIRNAME="window-sequence-kd-1"
LOG_DIRNAME="model-logdir/${DIRNAME}"
MODEL_CLASS="WindowSequenceModel"

/home/lovhag/miniconda3/envs/distilling-in-swedish-run-ner/bin/python /home/lovhag/projects/transformers/examples/token-classification/run_ner_old_any_model.py \
--data_dir /disk/lovhag/IOB2_splitted_NER \
--model_class $MODEL_CLASS \
--model_name_or_path /home/lovhag/bert-model-first \
--labels /disk/lovhag/IOB2_splitted_NER/labels.txt \
--output_dir $DIRNAME \
--logging_dir $LOG_DIRNAME \
--max_seq_length 128 \
--seed 1 \
--per_device_train_batch_size 32 \
--num_train_epochs 1 \
--save_steps 5000 \
--learning_rate 0.001 \
--evaluation_strategy epoch \
--do_train \
--do_eval \
--do_predict \
--kd_param 0.5 \
--loss_fct_kd KL \

#default learning rate=5e-5