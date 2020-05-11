import glob
import logging
from django.shortcuts import get_object_or_404

from ...models.preprocessed_data import PreprocessedData
from ...serializers.serializers import PreprocessedDataSerializer
from ...config.result_path_config import PATH_CONFIG

logger = logging.getLogger('collect_log_helper')
transformer_saved_path = PATH_CONFIG.PREPROCESS_TRANSFORMER
data_saved_path = PATH_CONFIG.PREPROCESSED_DATA


class DeletedInstanceError(Exception):
    def __str__(self):
        return "Instance is deleted"


class InvalidParameterError(Exception):
    def __str__(self):
        return "Parameter is no valid"


class FileNotExistedError(Exception):
    def __str__(self):
        return "File is not Existed"


class PreprocessedDownload:
    def __init__(self, pk):
        self.pk = pk
        self.serializer = PreprocessedDataSerializer(
            get_object_or_404(PreprocessedData, pk=pk)).data

    def case_get(self, case):
        if self.serializer["DELETE_FLAG"]:
            raise DeletedInstanceError()
        case_name = "case_" + str(case)
        selected_function = getattr(self, case_name)
        return selected_function()
    
    def case_data(self):
        return self.serializer['FILEPATH'], self.serializer['FILENAME']

    def case_transformer(self):
        pk_savad_list = glob.glob("{}/T_{}_*.pickle".format(transformer_saved_path, self.pk))
        if not pk_savad_list:
            raise FileNotExistedError()
        return pk_savad_list
