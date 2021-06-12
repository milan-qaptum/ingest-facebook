import facebook
import requests
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import time
from dateutil import parser
from keywrd import keyword_mapping
import pymongo
from sqlalchemy import create_engine
from urllib.parse import quote_plus

def check_username(username, user_id, user_status, org_id, agency_id):
	
	df_creds = pd.read_csv('../credentials.csv')
	try:
		access_token = df_creds[df_creds['SNO']==1]['access_token'].values[0]
		graph = facebook.GraphAPI(access_token, version='3.1')
	except:
		access_token = df_creds[df_creds['SNO']==2]['access_token'].values[0]
		graph = facebook.GraphAPI(access_token, version='3.1')

	# access_token = "EAAFIt3SFZCd8BAF9x26o5RivKl432hD7m5uQoHSvbniretuBBZCRX6NkDRlYgZAyUO3cztp0nN7HzwWAMza32bTp4mPTBhUTJEMsZASbuYDXrG2Sc9gi8OFUUeGTDEjU8gEUJQLRer13ZApNYtLhqqViluVyDnRZBQfhgePaRH4FqQGZAqeCTPdBl3cZB5N6cD5u7KXmDeNbfAZDZD"
	# access_token = "EAAFIt3SFZCd8BAA4Gwco9zeUPVZAYYeBD3P0ZAQhbqAZADdM7s6zhfiILEIhd5S1X7tqXhDXZA2GqZCLHF2RdUZBniuMwyV4DCNg9IilN04TsMXD5QecEBD00ORtpyMaVWukbEzZAeHly7RmZAZAnFQFctreoZA23UQiaZBzVkH56j30xLkF6hMzbVSorXM0CqHhkuYZD"
	# access_token = "EAALZCZBCuryk0BAG1z4AIS3EeZCckP36QXUfzxBJFOBJYw02wAZBVh7zLwxmNX3pn3pRX26MgxwfmCypXQcu3iQnkdoyvJyqRWRTZA2A3UBbz6iZBWjN3c6N2rvx9HZBrd36cp42TP8fcMvthk5qO2KvflPD8yuVCT3eIwlP44ZCg4LPwPdega0VURl6OwJuNkt1j1ni7JMtZBD8YVYAs1TMGHU4fycVly89QwrJUvr8Oa8sZAPaIDn8z8BTslzZB23giUZD"
	# user = "unicefmexico"


	if user_status == '1':
		# try:
			profile = graph.get_object(username)
			return {'1' : 'Valid Username'}
		# except facebook.GraphAPIError as e:
		# 	if e.code == 803:
		# 		return {'0' : 'Invalid Username'}
		# 	elif e.code == 4:
		# 		return {'5' : 'Request Limit Exceed. Please wait for 60 minutes and try again'}
		# 	else:
		# 		return {'19' : 'API error'}
		# except:
		# 	return {'19' : 'API error'}
	else:
		return {'8' : 'User is not Permitted to Perform the Operation'}

def main_facebook(user_id, user_status, username, message_count, task_id, task_start_time, keywords, condition_set_id, org_id, agency_id, project_id, start_date, end_date):
	
	message_count = int(message_count)
	def post_table(post, db, user_id, user_status, username, counter, keyword_counter, keywords, u_id, p_id, s_id):
		post_id = post['id']
		
		post_datetime = post['created_time']
		print(post_datetime)
		try:
			msg = post['message']
		except:
			msg = 'None'
		try:
			likes_dict = graph.get_connections(post['id'],'likes')
		except facebook.GraphAPIError as e:
			if e.code == 4:
				return {'5' : 'Request Limit Exceed. Please wait for 60 minutes and try again'}
			else:
				return {'19' : 'API error'}

		likes = len(likes_dict['data'])

		is_filter_met = keyword_mapping(keywords, msg)
		if is_filter_met == 1:
			keyword_counter += 1
		if keyword_counter >= message_count:
			return {'2' : 'Fetching Completed'}
		if counter >= 50 and keyword_counter == 0:
			return {'6' : "Threshold Exceeded for Keyword Matching"}

		# if (parser.parse(created_datetime_var) < parser.parse(post_datetime)) :
		post_ret = db.posts.update_one({'post_id':post_id,
			'u_id':u_id,
			'p_id':p_id,
			's_id':s_id,
			}, {'$set':{'is_updated':'1',
						'task_start_time':task_start_time,
						'user_status':user_status,
						'created_datetime':post_datetime,
						'post':msg,
						'post_likes':likes,
						'page_id':'None',
						'image_url':'None',
						'share_count':'None',
						'action_link':'None',
						'post_username':'None',
						'user_id':user_id,
						'username':username,
						'task_id':task_id,
						'org_id':org_id,
						'agency_id':agency_id,
						'project_id':project_id,
						'condition_set_id':condition_set_id,
						'is_filter_met':is_filter_met}}, upsert=True)
		
		print('Post ingested, total message count : ', counter)
		if counter >= message_count:
			return 'Complete'


	def comments_table(post, graph, db, user_id, user_status, username, counter, keyword_counter, keywords, u_id, p_id, s_id):
		""" Here you might want to do something with each post. E.g. grab the
		post's message (post['message']) or the post's picture (post['picture']).
		In this implementation we just print the post's created time.
		"""
		comments = graph.get_connections(id=post['id'], connection_name='comments', limit=100)
		
		for comment in comments['data']:
			com_msg = comment['message']
			com_id = comment['id']
			com_time = comment['created_time']
			try:
				com_likes_dict = graph.get_connections(com_id,'likes')
			except facebook.GraphAPIError as e:
				if e.code == 4:
					return {'5' : 'Request Limit Exceed. Please wait for 60 minutes and try again'}
				else:
					return {'19' : 'API error'}
			com_likes = len(com_likes_dict['data'])
			
			is_filter_met = keyword_mapping(keywords, com_msg)
			if is_filter_met == 1:
				keyword_counter += 1
			if keyword_counter >= message_count:
				return {'2' : 'Fetching Completed'}
			if counter >= 50 and keyword_counter == 0:
				return {'6' : "Threshold Exceeded for Keyword Matching"}
			# if (parser.parse(created_datetime_var) < parser.parse(com_time)) :
			db.comments.update_one({'comment_id':com_id,
				'u_id':u_id,
				'p_id':p_id,
				's_id':s_id,
				}, {'$set':{'is_updated':'1',
								'task_start_time':task_start_time,
								'user_status':user_status,
								'post_id':post['id'],
								'comment':com_msg,
								'created_datetime':com_time,
								'comment_likes':com_likes,
								'comment_username':'None',
								'username':username,
								'react_love':'None',
								'react_wow':'None',
								'react_haha':'None',
								'react_angry':'None',
								'react_sad':'None',
								'react_thankful':'None',
								'user_id':user_id,
								'task_id':task_id,
								'org_id':org_id,
								'agency_id':agency_id,
								'project_id':project_id,
								'condition_set_id':condition_set_id,
								'is_filter_met':is_filter_met}}, upsert=True)
			counter += 1
			print('Comment ingested, total message count :', counter)
			# if counter >= message_count:
			# 	return 'Complete'
			db.posts_comments.update_one({'comment_id':com_id,
				'u_id':u_id,
				'p_id':p_id,
				's_id':s_id,
				}, {'$set':{'is_updated':'1',
								'task_start_time':task_start_time,
								'user_status':user_status,
								'post_id':post['id'],
								'sentiment':'None',
								'user_id':user_id,
								'username':username,
								'task_id':task_id,
								'org_id':org_id,
								'agency_id':agency_id,
								'project_id':project_id,
								'condition_set_id':condition_set_id,
								'is_filter_met':is_filter_met}}, upsert=True)
			counter += 1
			print('Post-Comment ingested, total message count : ', counter)
			# if counter >= message_count:
			# 	return 'Complete'


	# try:
	# client = MongoClient("mongodb://dbstaging:N1Sj1woLdPhvH6mb3GUxT7420AYdzkLJ75DEkeUYsh3vVkmpjixipMI3IAdDT3BtiQyn3m4pz4q5CJ1dyOeztg==@dbstaging.mongo.cosmos.azure.com:10255/?ssl=true&replicaSet=globaldb&retrywrites=false&maxIdleTimeMS=120000&appName=@dbstaging@") #host uri
	# db = client.test    #Select the database
	# db.authenticate(name="dbstaging",password='N1Sj1woLdPhvH6mb3GUxT7420AYdzkLJ75DEkeUYsh3vVkmpjixipMI3IAdDT3BtiQyn3m4pz4q5CJ1dyOeztg==')

	usermongo = quote_plus('social')
	passwd = quote_plus('Mango92Enj1')
	dbname = quote_plus('test')
	client=MongoClient("mongodb+srv://"+usermongo+":"+passwd+"@intuaition-3.5n9rv.mongodb.net/"+dbname+"?retryWrites=true&w=majority")
	db = client.psa

	database = 'db_analysisrelated'
	host = 'db-reporting.mysql.database.azure.com'
	password = 'Gc96@dh3'
	user = 'reportingadmin@db-reporting.mysql.database.azure.com'

	engine_args = {'ssl':{'fake_flag_to_enable_tls': False}}
	engine = create_engine('mysql+pymysql://{}:{}@{}/{}'.format(user,password,host,database), connect_args=engine_args)

	con = engine.connect()

	user_meta = pd.read_sql('select * from partition_meta_users', con)
	project_meta = pd.read_sql('select * from partition_meta_projects', con)
	screenname_meta = pd.read_sql('select * from partition_meta_screennames where source="facebook"', con)

	user_meta = user_meta[user_meta['user_id']==int(user_id)]
	if user_meta.empty:
		return {'55' : 'User ID ' +user_id+ ' not present in user meta table'}
	else:
		user_meta = user_meta[user_meta['org_id']==int(org_id)]
		if user_meta.empty:
			return {'55' : 'Org ID ' +org_id+ ' not present in user meta table'}
		else:
			user_meta = user_meta[user_meta['agency_id']==int(agency_id)]
			if user_meta.empty:
				return {'55' : 'Agency ID ' +agency_id+ ' not present in user meta table'}

	project_meta = project_meta[project_meta['project_id']==int(project_id)]
	if project_meta.empty:
		return {'55' : 'Project ID ' +project_id+ ' not present in project meta table'}
	else:
		project_meta = project_meta[project_meta['task_id']==task_id]
		if project_meta.empty:
			return {'55' : 'Task ID ' +task_id+ ' not present in project meta table'}

	screenname_meta = screenname_meta[screenname_meta['screen_name']==username]
	if screenname_meta.empty:
		return {'55' : 'Screen Name ' +username+ ' not present in screenname meta table'}


	u_id = int(user_meta['u_id'].values[0])
	p_id = int(project_meta['p_id'].values[0])
	s_id = int(screenname_meta['s_id'].values[0])


	df_creds = pd.read_csv('../credentials.csv')
	try:
		access_token = df_creds[df_creds['SNO']==1]['access_token'].values[0]
		graph = facebook.GraphAPI(access_token, version='3.1')
	except:
		access_token = df_creds[df_creds['SNO']==2]['access_token'].values[0]
		graph = facebook.GraphAPI(access_token, version='3.1')
	# access_token = "EAAFIt3SFZCd8BAF9x26o5RivKl432hD7m5uQoHSvbniretuBBZCRX6NkDRlYgZAyUO3cztp0nN7HzwWAMza32bTp4mPTBhUTJEMsZASbuYDXrG2Sc9gi8OFUUeGTDEjU8gEUJQLRer13ZApNYtLhqqViluVyDnRZBQfhgePaRH4FqQGZAqeCTPdBl3cZB5N6cD5u7KXmDeNbfAZDZD"
	# user = "unicefmexico"

	# graph = facebook.GraphAPI(access_token, version='3.1')
	# while True:
	# try:
	print('username : ', username)
	profile = graph.get_object(username)
	# except facebook.GraphAPIError as e:
	# 	if e.code == 4:
	# 		return {'5' : 'Request Limit Exceed. Please wait for 60 minutes and try again'}
		# else:
		# 	return {'19' : 'API error'}

			# 	break
		# except facebook.GraphAPIError:
		# 	return 'Wrong Username'
		# except:
			# return 'API ran succesfully3'
			# 	print('Waiting for request limit to reset...')
			# 	time.sleep(20)
			# 	continue

	# try:
	global counter
	counter = 0
	keyword_counter = 0
	start_date_timestamp = datetime.timestamp(datetime.strptime(start_date,'%Y-%m-%d %H:%M'))
	end_date_timestamp = datetime.timestamp(datetime.strptime(end_date,'%Y-%m-%d %H:%M'))
	posts = graph.get_connections(profile["id"], "posts", since=start_date_timestamp,until=end_date_timestamp)
	# except facebook.GraphAPIError as e:
	# 	if e.code == 4:
	# 		return {'5' : 'Request Limit Exceed. Please wait for 60 minutes and try again'}
		# else:
		# 	return {'19' : 'API error'}

	# Wrap this block in a while loop so we can keep paginating requests until
	# finished.
	created_datetime_var_posts = '2004-02-04T00:00:00+0000'
	created_datetime_var_comments = '2004-02-04T00:00:00+0000'
	
	while True:
		try:
			# Perform some action on each post in the collection we receive from
			# Facebook.
			print('Fetching posts')
			# postlist = [post_table(post=post, db=db, user_id=user_id, user_status=user_status, username=username, counter=counter, keyword_counter=keyword_counter, keywords=keywords, u_id=u_id, p_id=p_id, s_id=s_id) for post in posts["data"]]
			for post in posts['data']:
				post_retval = post_table(post=post, db=db, user_id=user_id, user_status=user_status, username=username, counter=counter, keyword_counter=keyword_counter, keywords=keywords, u_id=u_id, p_id=p_id, s_id=s_id)
				counter += 1
				if post_retval=='Complete':
					print('postexhaust')
					return {'2' : 'Fetching Completed'}
			
			# comlist = [comments_table(post=post, graph=graph, db=db, user_id=user_id, user_status=user_status, username=username, counter=counter, keyword_counter=keyword_counter, keywords=keywords, u_id=u_id, p_id=p_id, s_id=s_id) for post in posts["data"]]
				print('Fetching comments')
				com_retval = comments_table(post=post, graph=graph, db=db, user_id=user_id, user_status=user_status, username=username, counter=counter, keyword_counter=keyword_counter, keywords=keywords, u_id=u_id, p_id=p_id, s_id=s_id)
				if com_retval == 'Complete':
					print('comexhaust')
					return {'2' : 'Fetching Completed'}
			# Attempt to make a request to the next page of data, if it exists.
			try:
				posts = requests.get(posts["paging"]["next"]).json()
			except:
				return {'2' : 'Fetching Completed'}
			# print(posts)
		except facebook.GraphAPIError as e:
			if e.code == 4:
				return {'5' : 'Request Limit Exceed. Please wait for 60 minutes and try again'}
			else:
				return {'19' : 'API error'}
			# except:
				# When there are no more pages (['paging']['next']), break from the
				# loop and end the script.
				# print('except')
				# return {'2' : 'Fetching Completed'}
			# except:
			# 	created_datetime_var_posts = str(db.posts.find({"$and":[{'user_id':user_id}, {'username':username}]}).sort([('created_datetime',-1)]).limit(1)) 
			# 	created_datetime_var_comments = str(db.comments.find({"$and":[{'user_id':user_id}, {'username':username}]}).sort([('created_datetime',-1)]).limit(1)) 
			# 	continue
	# except pymongo.errors.ExecutionTimeout as e:
	# 	return {'48' : 'Query Timed Out'}
	# except:
	# 	return {'19' : 'API error'}
# print(main_facebook(4, 0, '', '', 'InstitutoDanoneMexico'))
