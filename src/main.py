import datetime
import json
import os
import pprint
import re
import requests
import yaml
from util import bots, get_time, get_tasks


projects = {}
headers= {
    "content-type": "application/json",
    "Accept": "application/vnd.github.inertia-preview+json",
    "Time-Zone": "America/New_York",
    "Authorization": 'token {}'.format(os.environ['NCSU_GITHUBTOKEN'])
}
ORG = "csc510-fall2019" #  "cscdevops-spring2020" 

staff = ["cjparnin","smirhos","ffahid","yshi26","dcbrow10"]           
# board_info = {
#     "name":"Team Project", 
#     "body":"Hi Team, it looks like you haven't made any recent updates to your team project repository. To improve the quality of your code and productivity of your team, consider using the GitHub Projects feature to create tasks and track their progress on your work for the final project."
# }
board_info = {
    "name": "Milestone1",
    "body": "CSC 519 DevOps Project Milestone1",
}
FIRST_NOTE = "You can use cards to keep track of upcoming project tasks, current work in progress, and items you've completed for the CSC326 final project. Move this card to ***Done*** after you've read this message."
TASK_NOTE = "Hi. The bot noticed there has not been activity on **{task}**. The deadline for this milestone is ***{date}***."
ISSUE_NOTE = "Issue #{number}"
PULL_NOTE = "Pull Request #{number}"
# COLUMNS = ["To Do", "In Progress", "Done"]
COLUMNS = ['Tasks', 'In-Progress', 'Review', 'Completed']

def add_project(name):
    project = requests.post('https://api.github.ncsu.edu/repos/{org}/{repo}/projects'
        .format(org=ORG, repo=name), 
        data=json.dumps(board_info), headers=headers).json()
    for col in COLUMNS:
        column = requests.post(project['columns_url'], data=json.dumps({"name":col}), headers=headers).json()
        if col == "To Do":
            card_url = column['cards_url']
    card = requests.post(card_url, data=json.dumps({"note":FIRST_NOTE}), headers=headers).json()
    if 'error' not in card.keys():
        return project

def nudge_projects(repo):
    name = repo['name']
    projects[name] = {}
    project_list = requests.get('https://api.github.ncsu.edu/repos/{org}/{repo}/projects'
        .format(org=ORG,repo=name), headers=headers).json()
    if len(project_list) == 0: # No project board
        add_project(name)
        return
    else:
        for p in project_list:
            if p['name'] == board_info['name']:
                columns = requests.get(p['columns_url'], headers=headers).json()
                for col in columns:
                    if col['name'] == COLUMNS[0]:
                        todo = col
                        break
                break
        now = datetime.datetime(2019,11,19,11,45,00) # datetime.datetime.now()
        task = get_tasks(now)
        print(task)
        if (task):
            note = TASK_NOTE.replace('{task}', task['name']).replace('{date}', task['str_end'])
            card = requests.post(todo['cards_url'], data=json.dumps({"note":note}), headers=headers).json()
            print(card)
        # TODO: create cards for activity (open PRs, issues, etc.)
        # activity = get_activity(repo)
        # for item in activity:
        #     if item.get('pull_request'):
        #         note = PULL_NOTE.replace('{number}', str(item['number'])) # , "content_id":item['number'], "content_type":'Issue'
        #         pr_card = requests.post(todo['cards_url'], data=json.dumps({"note":note}), headers=headers).json()
        #         print(pr_card)
        #     else:
        #         note = ISSUE_NOTE.replace('{number}', str(item['number'])) # , "content_id":item['number'], "content_type":'PullRequest'
        #         iss_card = requests.post(todo['cards_url'], data=json.dumps({"note":note}), headers=headers).json()
        #         print(iss_card)



   # print(project)

def get_activity(repo):
    
    issues = requests.get('https://api.github.ncsu.edu/repos/{org}/{repo}/issues'
            .format(org=ORG,repo=repo['name']), headers=headers).json()
    for iss in issues:
        if iss['created_at']:
            return issues

def main():
    # if not bots('.'):
    #     return None

    response = requests.get('https://api.github.ncsu.edu/orgs/{org}/repos'.format(org=ORG), headers=headers).json()
    for repo in response:
        if repo['name'] in ['iTrust2-v6', 'CSC510-TEST']: #TODO remove later
            nudge_projects(repo)
    
if __name__ == "__main__":
    main()