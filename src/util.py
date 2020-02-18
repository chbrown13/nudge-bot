import datetime
import os
import re

import yaml

PROJECT = 'team-project'
DEADLINES = yaml.safe_load(open('deadlines.yml'))

def get_time(seconds):
    # Translate activity time to more readable format
    if seconds < 0:
        print('ERROR')
        return None
    elif seconds < 60:
        return '%d secs' % (int(seconds))
    elif seconds < 3600:
        return '%d mins' % (int(round(seconds/60.0)))
    elif seconds < 86400:
        return '%.d hrs' % (int(round(seconds/3600.0)))
    return '%d days' % (int(round(seconds/86400)))

def _get_deadlines():
    deadlines = DEADLINES[PROJECT]
    milestones = [re.sub(r'start|deadline|name|intermediate', '', k) for k in deadlines.keys()]
    tasks = {m: {'start': None, 'end': None, 'name': None, 'str_start': None, 'str_end': None, 'reqs': None} for m in milestones}
    for d in deadlines:
        milestone = re.sub(r'start|deadline|name|intermediate', '', d)
        if d.endswith('start'):   
            try:
                start = datetime.datetime.strptime(deadlines[d], '%A, %B %d')
            except ValueError:
                start = datetime.datetime.strptime(deadlines[d], '%A %B %d')
            start = datetime.datetime(2020, start.month, start.day)
            tasks[milestone]['start'] = start
            tasks[milestone]['str_start'] = deadlines[d]
        elif d.endswith('deadline'):
            end = datetime.datetime.strptime(deadlines[d], '%A, %B %d at %I:%M%p')
            end = datetime.datetime(2020, end.month, end.day, end.hour, end.minute)
            tasks[milestone]['end'] = end
            tasks[milestone]['str_end'] = deadlines[d]
        elif d.endswith('name'):
            tasks[milestone]['name'] = deadlines[d]
        tasks[milestone]['reqs'] = _get_requirements(milestone)
    return tasks

def _get_requirements(task):
    key = task.lower() + '-checklist'
    if key in DEADLINES:
        # return ['[' + n['name'] + '](https://pages.github.ncsu.edu/engr-csc326-staff/326-course-page' + n['link'] + ')' for n in DEADLINES[key]]
        return [n['name'] for n in DEADLINES[key]]


def get_tasks(date):
    current = {}
    soonest = datetime.timedelta(100000)
    tasks = _get_deadlines()
    for t in tasks.keys():
        end = tasks[t]['end']
        start = tasks[t]['start']
        if (start is None or start < date):
            if end is not None and end > date and end - date < soonest: #TODO: research on time to complete tasks
                current = tasks[t]
                soonest = end - date
    return current

def _bots_yml(file):
    config = yaml.safe_load(open(file))
    if config:
        if 'contribution-kinds' in config:
            if 'projects' not in config['contribution-kinds']:
                return False
        if 'allow-bots' in config:
            if type(config['allow-bots']) == bool:
                return config['allow-bots']
            elif type(config['allow-bots']) == dict:
                if 'name' in config['allow-bots'] and 'nudge-bot' in config['allow-bots']['name']:
                    return True
                elif 'type' in config['allow-bots'] and 'research' in config['allow-bots']['type']:
                    return True
    return False

def bots(path):
    bots_allowed = True
    for root, dirs, files in os.walk('../'):
        if 'bots.yml' in files:
            bots_allowed = _bots_yml(os.path.join(root, 'bots.yml'))
    return bots_allowed
