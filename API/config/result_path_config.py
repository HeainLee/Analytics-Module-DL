import os

class PATH_CONFIG:

    RESULT_BASE_DIRECTORY= 'result '.replace('\u2028','')
    ORIGINAL_DATA_DIRECTORY=os.path.join(RESULT_BASE_DIRECTORY,'original_data').replace('\u2028','')
    PREPROCESSED_DATA=os.path.join(RESULT_BASE_DIRECTORY,' preprocessed_data').replace('\u2028','')
    PREPROCESS_TRANSFORMER=os.path.join(RESULT_BASE_DIRECTORY,' preprocess_transformer ').replace('\u2028','')
    MODEL=os.path.join(RESULT_BASE_DIRECTORY,' model').replace('\u2028','')
    LOG=os.path.join(RESULT_BASE_DIRECTORY,' log').replace('\u2028','')


