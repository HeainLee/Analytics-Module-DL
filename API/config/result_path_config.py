# API/config
import os

class PATH_CONFIG:

    RESULT_BASE_DIR = 'result '.replace('\u2028','')
    LOG = os.path.join(RESULT_BASE_DIR,' log').replace('\u2028','')
    RESULT_ML_DIR = os.path.join(RESULT_BASE_DIR,'ml_result').replace('\u2028','')
    RESULT_DL_DIR = os.path.join(RESULT_BASE_DIR,'dl_result').replace('\u2028','')

    RESULT_ML_ORIGINAL_DATA_DIR = os.path.join(RESULT_ML_DIR,'original_data').replace('\u2028','')
    RESULT_ML_PREPROCESSED_DATA_DIR = os.path.join(RESULT_ML_DIR,' preprocessed_data').replace('\u2028','')
    RESULT_ML_PREPROCESS_TRANS_DIR = os.path.join(RESULT_ML_DIR,' preprocess_transformer ').replace('\u2028','')
    RESULT_ML_MODEL_DIR = os.path.join(RESULT_ML_DIR,' model').replace('\u2028','')

    RESULT_DL_ORIGINAL_DATA_DIR =os.path.join(RESULT_DL_DIR,'original_data').replace('\u2028','')
    RESULT_DL_MODEL_DIR=os.path.join(RESULT_DL_DIR,' model').replace('\u2028','')

