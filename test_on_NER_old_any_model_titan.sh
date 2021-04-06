MODEL_DIR="simple-lstm-256-depth-2-bert-embeddings-frozen-100"
CHECKPOINT_NUM="100000"
MODEL_CLASS="SimpleLSTM256Depth2BertEmbeddingsFrozen"
DIRNAME="${MODEL_DIR}-checkpoint-${CHECKPOINT_NUM}"
LOG_DIRNAME="model-logdir/${DIRNAME}"

CUSTOM_STATE_DICT_PATH="/home/lovhag/${MODEL_DIR}/checkpoint-${CHECKPOINT_NUM}/pytorch_model.bin"

/home/lovhag/miniconda3/envs/distilling-in-swedish-run-ner/bin/python /home/lovhag/projects/transformers/examples/token-classification/run_ner_old_any_model.py \
--data_dir /disk/lovhag/IOB2_splitted_NER \
--model_class $MODEL_CLASS \
--model_name_or_path /disk/lovhag/distilling_in_swedish_models/bert-model-first \
--custom_model_state_dict_path $CUSTOM_STATE_DICT_PATH \
--labels /disk/lovhag/IOB2_splitted_NER/labels.txt \
--output_dir $DIRNAME \
--logging_dir $LOG_DIRNAME \
--max_seq_length 128 \
--seed 1 \
--do_eval \
--do_predict \
--bert_embeddings_path /disk/lovhag/distilling_in_swedish_models/bert-model-first/embeddings.pt \
