from .config.result_path_config import PATH_CONFIG
import os


if not os.path.exists(PATH_CONFIG.RESULT_BASE_DIRECTORY) or not os.path.isdir(PATH_CONFIG.RESULT_BASE_DIRECTORY) :
    os.mkdir(PATH_CONFIG.RESULT_BASE_DIRECTORY)

if not os.path.exists(PATH_CONFIG.ORIGINAL_DATA_DIRECTORY) or not os.path.isdir(PATH_CONFIG.ORIGINAL_DATA_DIRECTORY):
    os.mkdir(PATH_CONFIG.ORIGINAL_DATA_DIRECTORY)

if not os.path.exists(PATH_CONFIG.PREPROCESSED_DATA) or not os.path.isdir(PATH_CONFIG.PREPROCESSED_DATA):
    os.mkdir(PATH_CONFIG.PREPROCESSED_DATA)

if not os.path.exists(PATH_CONFIG.PREPROCESS_TRANSFORMER) or not os.path.isdir(PATH_CONFIG.PREPROCESS_TRANSFORMER):
    os.mkdir(PATH_CONFIG.PREPROCESS_TRANSFORMER)

if not os.path.exists(PATH_CONFIG.MODEL) or not os.path.isdir(PATH_CONFIG.MODEL):
    os.mkdir(PATH_CONFIG.MODEL)

if not os.path.exists(PATH_CONFIG.LOG) or not os.path.isdir(PATH_CONFIG.LOG):
    os.mkdir(PATH_CONFIG.LOG)
