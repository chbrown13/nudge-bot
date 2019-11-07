def _get_time(seconds):
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

def project_health(name, health):
    if health == 'LOW':
        color = 'red'
    elif health == 'MED':
        color = 'yellow'
    else:
        color = 'green'
    print(name)
    print('![img](https://badgen.net/badge/Project_Health/{level}/{color})\n'.format(level=health, color=color))
