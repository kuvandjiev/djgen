from celery.app import shared_task
from time import sleep


@shared_task
def sleep_and_print(sleep_time):
    print(f"Executing task sleep_and_print. Will sleep {sleep_time}...")
    sleep(sleep_time)
    print(f"{sleep_time} seconds passed")
    return sleep_time
