import requests
import json

GITHUB_TOKEN = "*********************"  # Add your personal access token
REPO = "manishkumar1991/MonitorYourInfraHealth"  # Replace with your repository name (e.g., 'octocat/hello-world')
PR_NUMBER = 170  # Replace with the pull request number
workflow_run_id = 12783706314
temp_array =[]


def hit_api(url):
    headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to get response. Status code: {response.status_code}, Error: {response.text}")


# get the check runs url for a specific workflow run
url = f"https://api.github.com/repos/{REPO}/actions/runs/{workflow_run_id}/jobs"
result = hit_api(url)
check_run_url = result.get('jobs')[0].get('check_run_url')

# get the annotations for a specific check run
url = check_run_url + "/annotations"
annotate_result = hit_api(url)
for item in annotate_result:
    if "Found" in item.get('message'):
        temp_array.append(item)
# after filtering re assigning the temp_array to annotate_result  
annotate_result = temp_array
#Refine the annotations Results to be displayed
refined_string=""
for each in annotate_result:
    refined_string += f"| {each.get('path')} | File | {each.get('annotation_level')} | Secret Key Exposed {each.get('message')} line number : {each.get('start_line')} | Rotate your exposed secret key | \r\n"

print(refined_string)
# Print the annotations as comment to github PR
#  fetch the comment to be updated from the PR
url = f"https://api.github.com/repos/{REPO}/issues/{PR_NUMBER}/comments" 
result = hit_api(url)
comments = result
if comments:
    temp_array = []
    for each in comments:
        if "Pipeline Validations Result" in each.get('body'):
            b = {'comment_body': each.get('body'), 'comment_id': each.get('id')}
            temp_array.append(b)
    last_comment = temp_array[-1]
 #update comment to the PR
body = last_comment.get('comment_body') + "\r\n" + refined_string
url = f"https://api.github.com/repos/{REPO}/issues/comments/{last_comment.get('comment_id')}"

response = requests.patch(url, headers={"Authorization": f"Bearer {GITHUB_TOKEN}","Accept": "application/vnd.github+json"}, data=json.dumps({"body": body}))
