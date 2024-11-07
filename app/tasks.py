from . import celery
from time import sleep

@celery.task
def example_task(data):
    # Simulate a long-running task
    print("Processing data:", data)
    sleep(10000)
    # Process data or perform some actions here
    return {"status": "Task completed", "data": data}