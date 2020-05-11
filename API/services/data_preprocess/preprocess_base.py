import logging
import warnings
import numpy as np
from distutils import util
# to handle str to bool conversion
from ast import literal_eval

from ..utils.custom_call import CallMixin, PreprocessUtils
from ..utils.custom_decorator import where_exception

warnings.filterwarnings("ignore")
logger = logging.getLogger("collect_log_helper")


class PreprocessorBase(CallMixin, PreprocessUtils):
    """
    For Preparing data, Loading transformer, Changing parameters

    Base Class of TestPreprocessor (preprocess_tester.py)
              and InspectUserRequest (preprocess_helper.py)
    """

    # 요청된 전처리 조건에 맞게 파라미터 값 변경
    @staticmethod
    def _change_transformer_params(transformer, params_dict):
        """
        Change Parameters of Transformer according to params_dict

        Parameters:
        -----------
             transformer (object) : Requested Original transformer
             params_dict (dict) : 'condition' value from Request Body

        Returns:
        --------
             transformer (object) : transformer with changed parameters
                                    according to param_dict

        """
        try:
            for k, v in params_dict.items():
                if not isinstance(v, str):
                    v = str(v)
                v = v.lower()
                logger.warning(
                    '[전처리 파라미터 변경] 파라미터 변경 요청=> key="{}", value="{}"'.format(k, v)
                )
                if "." in v:
                    if v.replace(".", "").isdigit():  # float 인 경우
                        v = float(v)
                        setattr(transformer, k, v)
                    else:
                        setattr(transformer, k, v)
                elif v.isdigit():  # int 인 경우
                    v = int(v)
                    setattr(transformer, k, v)
                elif v == "true" or v == "false":  # boolean 인 경우
                    v = bool(util.strtobool(v))
                    setattr(transformer, k, v)
                elif v == "none":  # None 인 경우
                    setattr(transformer, k, None)
                elif v.startswith("["):  # list 인 경우
                    v = v[1:-1].replace(" ", "").split(",")
                    setattr(transformer, k, v)
                elif v.startswith("("):  # tuple 인 경우
                    v = literal_eval(v)
                    setattr(transformer, k, v)
                elif v == "nan":  # np.nan 인 경우
                    setattr(transformer, k, np.nan)
                else:
                    setattr(transformer, k, v)
            logger.warning(transformer)
            return transformer
        except Exception as e:
            logger.error("[전처리 파라미터 변경] 전처리기 파라미터 변경을 실패했습니다")
            where_exception(error_msg=e)
            return dict(error_name="ParameterSyntaxError", error_detail=v)
