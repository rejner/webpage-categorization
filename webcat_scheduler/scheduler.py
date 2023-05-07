from flask_restful import Resource
from flask import current_app, request
from webcat.database import db
from webcat.models_extension import ScheduleEntry, Worker
import logging
import requests


def get_workers():
    return Worker.query.all()

def is_worker_alive(url):
    try:
        r = requests.get(url + '/ping')
        if r.status_code == 200:
            return True
        else:
            return False
    except:
        return False

def set_worker_as_dead(worker):
    worker.status = 'dead'
    db.session.commit()

def get_free_worker(type='gpu'):
    workers = Worker.query.filter_by(type=type, status='free').all()
    for worker in workers:
        if not is_worker_alive(worker.url):
            logging.info('Worker {} is dead'.format(worker.url))
            set_worker_as_dead(worker)
            continue
        # return first free worker
        return worker

    return None

def reserve_worker(worker):
    worker.status = 'busy'
    db.session.commit()

def release_worker(worker):
    worker.status = 'free'
    db.session.commit()

def create_schedule_entry(worker, file_path):
    schedule_entry = ScheduleEntry(
        worker_id=worker.id,
        file_path=file_path
    )
    db.session.add(schedule_entry)
    db.session.commit()

class WebCatScheduler(Resource):
    def __init__(self):
        super().__init__()
    
    def __del__(self):
        # close session
        db.session.close()

    def get(self):
        workers = get_workers()
        return {
            'workers': [worker.json_serialize() for worker in workers]
        }, 200

    def delete(self):
        args = request.get_json()
        worker_id = args['id']
        worker = Worker.query.get(worker_id)
        release_worker(worker)
        logging.info('Worker {} released'.format(worker.url))
        # close session
         
        return {
            'message': 'Worker released.'
        }, 200

    def post(self):
        args = request.get_json()
        type = args['type'] if 'type' in args else 'gpu'
        file_path = args['file_path'] if 'file_path' in args else 'interactive'
        try:
            worker = get_free_worker(type)
            reserve_worker(worker)
            create_schedule_entry(worker, file_path)
            logging.info('Worker {} reserved'.format(worker.url))
            return {
                'worker': worker.json_serialize()
            }, 200
        except:
            return {
                'error': 'No free worker available'
            }, 503
