#################[데이터 원본(학습데이터) 관리]#################
from __future__ import absolute_import

import time
import kombu.five
from itertools import chain
from ast import literal_eval
from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from celery.task.control import inspect

from smartcity.celery import app
from ..services.utils.custom_decorator import where_exception


class AsyncTask(APIView):
	def get(self, request):
		try:
			task_id = request.GET.get('task_id', None)
		except:
			task_id = False
		try:
			if task_id:
				task_status = app.backend.get_status(task_id=task_id)
				if task_status != "SUCCESS":
					task_result = 'None'
				else:
					task_result = app.backend.get_result(task_id=task_id)

				return_value = dict(status=task_status, result=task_result)
				return Response(return_value, status=status.HTTP_200_OK)
			else:
				check_dict = dict()
				curr_time = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(time.time()))
				check_dict['current_time'] = curr_time


				i = inspect()
				celery_stats = i.stats()
				all_tasks_list = list(chain.from_iterable(i.registered_tasks().values()))


				active_tasks = i.active()
				active_tasks_list = list(chain.from_iterable(active_tasks.values()))
				total_return = list()
				i = 0 
				for active_info in active_tasks_list:
					return_value = dict()
					return_value["id"] = active_info["id"]
					return_value["name"] = active_info["name"]
					return_value["pid"] = active_info["worker_pid"]
					time_start = time.time() - (kombu.five.monotonic() - active_info['time_start'])
					time_start = time.strftime('%Y-%m-%d %I:%M:%S %p', time.localtime(time_start))
					return_value["start_time"] = time_start
					get_args = literal_eval(active_info["args"])
					model_no = 'M_{}'.format(get_args[2])
					return_value["model_number"] = model_no

					total_return.append(return_value)
					i += 1

				check_dict['task_lists'] = total_return
				check_dict['celery_stats'] = celery_stats
				return Response(check_dict, status=status.HTTP_200_OK)

		except Exception as e:
			where_exception(error_msg=e)
			return Response('error', status=status.HTTP_200_OK)