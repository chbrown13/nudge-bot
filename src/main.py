import datetime
import json
import os
import requests
from util import _get_time, project_health


projects = {}
headers= {
			"content-type": "application/json",
            "Accept": "application/vnd.github.inertia-preview+json",
            "Time-Zone": "America/New_York",
			"Authorization": 'token {}'.format(os.environ['NCSU_GITHUBTOKEN'])
		}
org = "csc510-fall2019"
staff = ["cjparnin","smirhos","ffahid","yshi26","dcbrow10"]
    

def get_slackers(repos):
    slackers = {}
    for r in repos:
        slackers['repo'] = None
        repo = r['name']
        collabs = requests.get('https://api.github.ncsu.edu/repos/{org}/{repo}/collaborators'
            .format(org=org,repo=repo), headers=headers).json()
        students = [c['login'] for c in collabs if c['login'] not in staff]
        print(repo)
        for s in students:
            commits = requests.get('https://api.github.ncsu.edu/repos/{org}/{repo}/commits?author={stud}&sort=committer-date'
                .format(org=org,repo=repo,stud=s), headers=headers).json()
            if len(commits) > 0:
                print('\t' + s + ': ' + str(len(commits)))
            else:
                print('\t' + s + ': 0')
            # if dev not in devs:
            #     devs.append(dev)
        # print(students)
        # print(devs)
            # date = c['commit']['committer']['date']
            # temp = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
            # if (slackers[dev] is None or temp > slackers[dev][0]):
            #     slackers[dev] = [temp, repo]
            # # date = c['commit']['commit']['author']['date']
            # # update = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
            # # if slackers[dev] is None or slackers[dev] < update:
            # #     slackers[dev] = update
    # now = datetime.datetime.utcnow()
    # for key in slackers.keys():
    #     print(key)
    #     print('\n\t'.join(slackers[key]))
        
            


def get_projects(repo):
    has_board = False
    has_columns = False
    has_cards = False
    updated_cards = False
    name = repo['name']
    projects[name] = {}
    project_list = requests.get('https://api.github.ncsu.edu/repos/{org}/{repo}/projects'
        .format(org=org,repo=name), headers=headers).json()
    if len(project_list) > 0:
        has_board = True
    for p in project_list:
        proj_id = p['id']
        proj = p['name']
        projects[name]['project'] = {proj: {}}
        columns = requests.get('https://api.github.ncsu.edu/projects/{id}/columns'
            .format(id=proj_id), headers=headers).json()
        if len(columns) > 0:
            has_columns = True
        for c in columns:
            col_id = c['id']
            col = c['name']
            projects[name]['project'][proj] = {col: []}
            cards = requests.get('https://api.github.ncsu.edu/projects/columns/{id}/cards'
                .format(id=col_id), headers=headers).json()
            if len(cards) > 0:
                has_cards = True
            for card in cards:
                updated = datetime.datetime.strptime(card['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
                now = datetime.datetime.utcnow()
                diff = (now - updated).total_seconds()
                if card['note'] is not None:
                    projects[name]['project'][proj][col].append((card['note'], _get_time(diff)))
                if diff < 86400:
                    updated_cards = True
        health = sum([has_board, has_columns, has_cards, updated_cards])
        if health == 4:
            project_health(repo, 'HIGH')
        elif health <= 1:
            project_health(repo, 'LOW')
        else:
            project_health(repo, 'MED')
        print('      ' + _get_time(diff) + ' ' + str(diff) + ' ' + str(health) + ' ' + str([has_board, has_columns, has_cards, updated_cards]))

    with open('projects.txt', 'w') as f:
        for k,v in projects.items():
            f.write(k + '\n')
            if type(v) == dict:
                for j,u in v.items(): # projects
                    f.write('* ' + j + '\n')
                    if type(u) == dict:
                        for i,t in u.items(): # columns
                            f.write('  + ' + i + '\n')
                            s = sorted(t, key=lambda x: x[1])
                            for d in s:
                                # print(d)
                                f.write('    - ' + d[0].encode('utf8').replace('\r\n', ' ').replace('\n','') + ': ' + str(d[1]) + '\n')
                    else:
                        f.write(u + '\n')
            else:
                f.write(v + '\n')
            
def get_updates(repo, user=None):
    name = repo['name']
    branches = requests.get('https://api.github.ncsu.edu/repos/{org}/{repo}/branches'
        .format(org=org,repo=name), headers=headers).json()
    updated = None
    latest_branch = ''
    for b in branches:
        branch = b['name']
        commit = requests.get('https://api.github.ncsu.edu/repos/{org}/{repo}/branches/{branch}'
            .format(org=org,repo=name,branch=branch), headers=headers).json()
        date = commit['commit']['commit']['author']['date']
        temp = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ')
        if updated is None or temp > updated:
            updated = temp
            latest_branch = branch
    now = datetime.datetime.utcnow()
    diff = (now - updated).total_seconds()
    projects[name]['update'] = [_get_time(diff), latest_branch]
    # with open('updated.txt', 'w') as f:
    #     for u in updates:
    #         f.write("{:9s} {time} ({branch})\n".format(u[0], time=_get_time(u[1]), branch=u[2]))



def main():
    response = requests.get('https://api.github.ncsu.edu/orgs/{org}/repos'.format(org=org), headers=headers).json()
    for repo in response:
        projects[repo['name']] = {'update': None, 'project': {}}
        get_updates(repo)
        get_projects(repo)
    print(projects)
# 
# get_slackers(response)
    
if __name__ == "__main__":
    main()