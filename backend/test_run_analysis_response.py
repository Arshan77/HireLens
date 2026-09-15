import urllib.request
import urllib.parse
import json
import time

ts = int(time.time())
email = f"test_analysis_{ts}@example.com"
pwd = "Password123!"

# 1. Register
req1 = urllib.request.Request(
    'http://localhost:8001/api/v1/auth/register',
    data=json.dumps({'email': email, 'password': pwd}).encode(),
    headers={'Content-Type': 'application/json'}
)
res1 = urllib.request.urlopen(req1)

# 2. Login
req2 = urllib.request.Request(
    'http://localhost:8001/api/v1/auth/login',
    data=f'username={urllib.parse.quote(email)}&password={urllib.parse.quote(pwd)}'.encode(),
    headers={'Content-Type': 'application/x-www-form-urlencoded'}
)
res2 = urllib.request.urlopen(req2)
token = json.loads(res2.read())['access_token']

# 3. Upload Resume
boundary = '----WebKitBoundary12345'
pdf_text = "%PDF-1.4\nExperience: Senior Software Engineer (2020-2023). Skills: Python, FastAPI, PostgreSQL, Docker, AWS.\n%%EOF"
body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="resume.pdf"\r\n'
    f'Content-Type: application/pdf\r\n\r\n'
    f'{pdf_text}\r\n'
    f'--{boundary}--\r\n'
).encode('utf-8')

req3 = urllib.request.Request(
    'http://localhost:8001/api/v1/resumes/upload',
    data=body,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}', 'Authorization': f'Bearer {token}'}
)
res3 = urllib.request.urlopen(req3)

# 4. Get Resume ID
req_list = urllib.request.Request('http://localhost:8001/api/v1/resumes', headers={'Authorization': f'Bearer {token}'})
res_list = urllib.request.urlopen(req_list)
resumes = json.loads(res_list.read())
resume_id = resumes[0]['id']

# 5. Run Analysis
req4 = urllib.request.Request(
    'http://localhost:8001/api/v1/analysis/run',
    data=json.dumps({
        'resume_id': resume_id,
        'job_title': 'Senior Python Developer',
        'job_description_text': 'Seeking a Senior Python Developer with 3+ years experience in FastAPI, PostgreSQL, Docker, and AWS.'
    }).encode(),
    headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
)
res4 = urllib.request.urlopen(req4)
analysis_data = json.loads(res4.read())

print("--- ACTUAL BACKEND JSON RESPONSE ---")
print(json.dumps(analysis_data, indent=2))
