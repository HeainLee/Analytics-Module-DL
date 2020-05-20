from API.config.result_path_config import PATH_CONFIG
import os

if not os.path.exists(PATH_CONFIG.RESULT_BASE_DIR) or not os.path.isdir(PATH_CONFIG.RESULT_BASE_DIR) :
    os.mkdir(PATH_CONFIG.RESULT_BASE_DIR)

if not os.path.exists(PATH_CONFIG.LOG) or not os.path.isdir(PATH_CONFIG.LOG):
    os.mkdir(PATH_CONFIG.LOG)

if not os.path.exists(PATH_CONFIG.RESULT_ML_DIR) or not os.path.isdir(PATH_CONFIG.RESULT_ML_DIR):
    os.mkdir(PATH_CONFIG.RESULT_ML_DIR)

if not os.path.exists(PATH_CONFIG.RESULT_DL_DIR) or not os.path.isdir(PATH_CONFIG.RESULT_DL_DIR):
    os.mkdir(PATH_CONFIG.RESULT_DL_DIR)

if not os.path.exists(PATH_CONFIG.RESULT_ML_ORIGINAL_DATA_DIR) or not os.path.isdir(PATH_CONFIG.RESULT_ML_ORIGINAL_DATA_DIR):
    os.mkdir(PATH_CONFIG.RESULT_ML_ORIGINAL_DATA_DIR)

if not os.path.exists(PATH_CONFIG.RESULT_ML_PREPROCESSED_DATA_DIR) or not os.path.isdir(PATH_CONFIG.RESULT_ML_PREPROCESSED_DATA_DIR):
    os.mkdir(PATH_CONFIG.RESULT_ML_PREPROCESSED_DATA_DIR)

if not os.path.exists(PATH_CONFIG.RESULT_ML_PREPROCESS_TRANS_DIR) or not os.path.isdir(PATH_CONFIG.RESULT_ML_PREPROCESS_TRANS_DIR):
    os.mkdir(PATH_CONFIG.RESULT_ML_PREPROCESS_TRANS_DIR)

if not os.path.exists(PATH_CONFIG.RESULT_ML_MODEL_DIR) or not os.path.isdir(PATH_CONFIG.RESULT_ML_MODEL_DIR):
    os.mkdir(PATH_CONFIG.RESULT_ML_MODEL_DIR)

if not os.path.exists(PATH_CONFIG.RESULT_DL_ORIGINAL_DATA_DIR) or not os.path.isdir(PATH_CONFIG.RESULT_DL_ORIGINAL_DATA_DIR):
    os.mkdir(PATH_CONFIG.RESULT_DL_ORIGINAL_DATA_DIR)

if not os.path.exists(PATH_CONFIG.RESULT_DL_MODEL_DIR) or not os.path.isdir(PATH_CONFIG.RESULT_DL_MODEL_DIR):
    os.mkdir(PATH_CONFIG.RESULT_DL_MODEL_DIR)


# python manage.py makemigrations API
# python manage.py showmigrations API
# python manage.py migrate API