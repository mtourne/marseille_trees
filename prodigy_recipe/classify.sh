#!/bin/sh

DATASET_FILE="../dataset_marseille/deepforest_pred_laplaine_patches_IGN0.2m.jsonl"
ANNOTATED_DATASET="classify-trees deepforest_tree_laplaine_classify-2"

prodigy $ANNOTATED_DATASET $DATASET_FILE -F classify_tree_patches.py
