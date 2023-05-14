import json
import time
import requests

ACCESS_TOKEN = "mOD3VhRDOf3qtqvnVQkl"
def multipage_request(url, err_msg):
	res = []
	page = 1
	while True:
		# print(page)
		r = requests.get(f'{url}?private_token={ACCESS_TOKEN}&page={page}&per_page=100')
		if r.status_code != 200:
			print(error(err_msg))
			exit(1)
		res += json.loads(r.text)
		if len(json.loads(r.text)) < 100:
			break
		page += 1
	return res

def ok(str):
	return f'\033[1m\033[92m{str}\033[0m\033[0m'
def warning(str):
	return f'\033[1m\033[93m{str}\033[0m\033[0m'
def error(str):
	return f'\033[1m\033[91m{str}\033[0m\033[0m'


print("**** Runing checks ****")
print("Waiting for GitLab to start responding...")

run = True
num = 0
while run:
	if num == 20:
		print("GitLab failed to start, exiting...")
		exit(1)

	try:
		response = requests.get("http://127.0.0.1/-/health")
		if response.status_code == 200:
			run = False
		else:
			print(f'GitLab responded with {response.status_code}, waiting 30 seconds...')
			num += 1
			time.sleep(30)
			pass
	except:
		print("GitLab not responding yet, waiting 30 seconds...")
		num += 1
		time.sleep(30)
		pass

print("GitLab is responding, running checks...")

print("**** Health check ****")
r = requests.get("http://127.0.0.1/-/health")
if r.status_code != 200:
	print(error("Gitlab /-/health check failed"))
	exit(1)
print(ok("OK"))

print("**** Readiness checks ****")
r = requests.get("http://127.0.0.1/-/readiness?all=1")
if r.status_code != 200:
	print(error("Gitlab /-/readiness check failed"))
	exit(1)
status = json.loads(r.text)
fail = False
if status["status"] != "ok":
	fail = True
for check in status.values():
	if isinstance(check, list):
		if check[0]["status"] != "ok":
			fail = True

if fail:
	print(error("Gitlab /-/readiness check failed"))
	print("Response: ", status)
	exit(1)
print(ok("OK"))

print("**** Other checks ****")

print("Number of projects: ", end='')
projects = multipage_request('http://localhost/api/v4/projects', 'Gitlab /api/v4/projects check failed')
if len(projects) <= 300:
	print(error("Too few projects, something is wrong"))
	exit(1)
print(ok(len(projects)))

print("Number of users: ", end='')
users = multipage_request('http://localhost/api/v4/users', 'Gitlab /api/v4/users check failed')
if len(users) < 130:
	print(error("Too few users, something is wrong"))
	exit(1)
print(ok(len(users)))

print("Creating group... ", end='')
r = requests.post(f'http://localhost/api/v4/groups?private_token={ACCESS_TOKEN}',
		  json={'name': 'backup', 'path': 'backup'})
if r.status_code != 201:
	print(error("Failed to create group"))
	print("Response: ", r.text)
	exit(1)
print(ok("OK"))
id = json.loads(r.text)["id"]

print("Creating project... ", end='')
r = requests.post(f'http://localhost/api/v4/projects?private_token={ACCESS_TOKEN}',
		  json={"name": "backup", "namespace_id": id})
if r.status_code != 201:
	print(error("Failed to create project"))
	print("Response: ", r.text)
	exit(1)
print(ok("OK"))

project = json.loads(r.text)

print("Checking issues... ", end='')
r = requests.get(f'http://localhost/api/v4/projects/{project["id"]}/issues?private_token={ACCESS_TOKEN}')
if r.status_code != 200:
	print(error("Failed to get issues"))
	exit(1)
if len(json.loads(r.text)) != 0:
	print(error("Issues not empty"))
	exit(1)

print(ok("OK"))

print("Creating issue... ", end='')
r = requests.post(f'http://localhost/api/v4/projects/{project["id"]}/issues?private_token={ACCESS_TOKEN}',
		  json={"title": "test issue", "description": "test issue"})
if r.status_code != 201:
	print(error("Failed to create issue"))
	print("Response: ", r.text)
	exit(1)
print(ok("OK"))
