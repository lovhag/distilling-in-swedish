#!/bin/sh
/home/lovhag/miniconda3/envs/distilling-in-swedish-run-ner/bin/python /home/lovhag/projects/transformers/examples/token-classification/run_ner_old_any_model.py \
--data_dir /disk/lovhag/IOB2_splitted_NER \
--model-class BERT \
--model_name_or_path /home/lovhag/bert-model-first \
--labels /disk/lovhag/IOB2_splitted_NER/labels.txt \
--output_dir bert-model-first-test-any-model \
--max_seq_length 128 \
--seed 1 \
--do_eval \
--do_predict \
