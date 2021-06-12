import sys
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

sys.path.append('../Code/')
from ingest_facebook import check_username as fcu
from ingest_facebook import main_facebook

#from .tasks import celery_task 
#from .tasks import celery_checkuser

@api_view(['GET', 'POST'])
def facebook_function(request):
	if request.method == 'GET':
		return Response({"message": "Got some data!"})

	elif request.method == 'POST':
		print(request.data)
		user_id = request.data['user_id']
		user_status = request.data['user_status']
		username = request.data['username']
		message_count = request.data['message_count']
		task_id = request.data['task_id']
		task_start_time = request.data['task_start_time']
		keywords = request.data['keywords']
		condition_set_id = request.data['condition_set_id']
		org_id = request.data['org_id']
		agency_id = request.data['agency_id']
		project_id = request.data['project_id']
		start_date = request.data['start_date']
		end_date = request.data['end_date']
		print(user_id, user_status, username, message_count, task_id, task_start_time, keywords, condition_set_id, org_id, agency_id, project_id, start_date, end_date)
		result = main_facebook(user_id, user_status, username, message_count, task_id, task_start_time, keywords, condition_set_id, org_id, agency_id, project_id, start_date, end_date)
		#print(user_id,user_status,start_datetime,stop_datetime,username)
		#result = celery_task.delay(user_id, user_status, start_datetime, stop_datetime, username)
		#result = main_facebook(user_id, user_status, start_datetime, stop_datetime, username)
		return Response({"message": result})


@api_view(['GET', 'POST'])
def facebook_checkUser(request):
	if request.method == 'GET':
		return Response({"message": "Got some data!"})

	elif request.method == 'POST':
		print(request.data)
		username = request.data['username']
		user_id = request.data['user_id']
		user_status = request.data['user_status']
		org_id = request.data['org_id']
		agency_id = request.data['agency_id']
		result = fcu(username=username, user_id=user_id, user_status=user_status, org_id=org_id, agency_id=agency_id)
		return Response({"message": result})
		#result = fcu(username=username)
		#result = celery_checkuser.delay(username=username)
		#return Response({"message": result})
