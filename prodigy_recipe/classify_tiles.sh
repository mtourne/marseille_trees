#!/bin/sh

DATASET_FILE="../dataset_marseille/deepforest_pred_tiles_prodigy.jsonl"
ANNOTATED_DATASET="box_trees"

prodigy image.manual $ANNOTATED_DATASET $DATASET_FILE --loader jsonl --label tree
