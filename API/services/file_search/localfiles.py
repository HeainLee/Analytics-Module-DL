import os
import csv
import json
from shutil import rmtree
from datetime import datetime
from collections import OrderedDict

class InvalidPathContainedError(Exception):
    def __str__(self):
        return "Path couldn't contain " + "../ character"


class NotSupportedFileTypeError(Exception):
    def __str__(self):
        return "Supported File Type is only " + "json or csv"


class NotSupporteCommandError(Exception):
    def __str__(self):
        return "Command is failed"


class Localfiles:
    def __init__(self):
        self.sample_num = 5

    def convert_date(self, timestamp):
        date_obj = datetime.fromtimestamp(timestamp)
        return date_obj

    def case_get(self, case, path):
        if path is None or "../" in path:
            raise InvalidPathContainedError()
        case_name = "case_" + str(case)
        selected_function = getattr(self, case_name)
        return selected_function(path)

    def case_get_list(self, path):
        file_list = [
            file_name
            for file_name in os.listdir(path)
            if os.path.isfile(os.path.join(path, file_name))
            and not file_name.startswith(".")
        ]
        dir_list = [
            dir_name
            for dir_name in os.listdir(path)
            if not os.path.isfile(os.path.join(path, dir_name))
            and not dir_name.startswith(".")
        ]
        return file_list, dir_list

    def case_get_info(self, path):
        # mtime=최근변경시간, ctime=생성시간
        mtime = self.convert_date(os.path.getmtime(path))
        ctime = self.convert_date(os.path.getctime(path))
        stsize = os.path.getsize(path)
        return mtime, ctime, stsize

    def case_get_sample(self, path):
        if not (path.endswith(".json") or path.endswith(".csv")):
            raise NotSupportedFileTypeError()
        limit = self.sample_num
        samples = []

        if path.endswith(".json"):
            with open(path) as f:
                while True:
                    limit = limit - 1
                    line = f.readline()
                    if limit < 0 or not line:
                        break
                    samples.append(json.loads(line))
                    
        elif path.endswith(".csv"):
            with open(path) as f:
                line = csv.DictReader(f)
                for row in line:
                    limit = limit - 1                 
                    if limit < 0 or not row:
                        break
                    get_row = json.dumps(row)
                    samples.append(json.loads(get_row))
        return samples

    def case_delete(self, path):
        if os.path.isfile(path):
            os.remove(path)
        elif not os.path.isfile(path):
            os.rmdir(path)
            # rmtree(path) -> 기본은 폴더만 지울 수 있도록 처리하였으며,
            # 재귀적으로 파일을 지우고 싶을 시 os.rmdir(path) 대신 rmtree(path)를 지움

    def case_default(self, path):
        raise NotSupporteCommandError
