from locust import HttpUser, TaskSet, task
import os
import random

from core.environment.host import get_host_for_locust_testing


class FlamapyBehavior(TaskSet):
    def on_start(self):
        self.file_id = 1

    @task(3)
    def check_csv(self):
        response = self.client.get(f"/flamapy/check_csv/{self.file_id}")
        if response.status_code not in (200, 400):
            print(f"check_csv failed: {response.status_code} for file_id {self.file_id}")

    @task(2)
    def valid(self):
        response = self.client.get(f"/flamapy/valid/{self.file_id}")
        if response.status_code != 200:
            print(f"valid endpoint failed: {response.status_code} for file_id {self.file_id}")


class FlamapyUser(HttpUser):
    tasks = [FlamapyBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()
