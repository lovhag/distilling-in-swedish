DIRNAME="simple-lstm-256-depth-2-bert-embeddings-frozen-100"
LOG_DIRNAME="model-logdir/${DIRNAME}"
MODEL_CLASS="SimpleLSTM256Depth2BertEmbeddingsFrozen"

/home/lovhag/miniconda3/envs/distilling-in-swedish-run-ner/bin/python /home/lovhag/projects/transformers/examples/token-classification/run_ner_old_any_model.py \
--data_dir /disk/lovhag/IOB2_splitted_NER \
--model_class $MODEL_CLASS \
--model_name_or_path /disk/lovhag/distilling_in_swedish_models/bert-model-first \
--labels /disk/lovhag/IOB2_splitted_NER/labels.txt \
--output_dir $DIRNAME \
--logging_dir $LOG_DIRNAME \
--max_seq_length 128 \
--seed 1 \
--per_device_train_batch_size 32 \
--per_device_eval_batch_size 32 \
--num_train_epochs 0 \
--save_steps 10000 \
--learning_rate 0.001 \
--evaluation_strategy epoch \
--do_train \
--do_eval \
--do_predict \
--kd_param 0 \
--loss_fct_kd KL \
--bert_embeddings_path /disk/lovhag/distilling_in_swedish_models/bert-model-first/embeddings.pt \
--num_emb_frozen_train_epochs 100 \

#default lr here=1e-3
#default lr BERT=5e-5
