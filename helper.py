local_worker = 0
local_assignment = 0

"""
Cookie Management:
workerID -> ID of worker, should never change
assignID -> ID of assignment
mturk -> azure (always)
assignment_finished -> str, set finished when submit_data/ called
demographics_finished -> str, true if demographics are done
"""


def make_cookie(worker_id: str,
                assignment_id: str,
                response):
    response.set_cookie('workerID', worker_id)
    response.set_cookie('assignID', assignment_id)
    response.set_cookie('mturk', "azure")
    response.set_cookie('assignment_finished', "False")
    return response


def check_new_user(request) -> dict:
    if request.cookies.get('mturk') == 'azure':
        if request.cookies.get('workerID') != "":
            return {'worker_id': request.cookies.get('workerID')}
    else:
        return None


def get_assignment(user, request):
    if request.cookies.get('assignment_finished') == 'True':
        global local_assignment
        local_assignment += 1
        user['assignment_id'] = f"assignment{local_assignment}"
    else:
        user['assignment_id'] = request.cookies.get('assignID')
    return user


def make_new_user():
    global local_worker
    global local_assignment
    local_worker += 1
    local_assignment += 1
    return {'worker_id': f"worker{local_worker}",
            "assignment_id": f"assignment{local_assignment}"}