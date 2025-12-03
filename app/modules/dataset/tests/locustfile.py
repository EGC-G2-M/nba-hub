from locust import HttpUser, TaskSet, task, between

from core.environment.host import get_host_for_locust_testing
from core.locust.common import get_csrf_token

class DatasetBehavior(TaskSet):
    def on_start(self):
        self.dataset()

    @task
    def dataset(self):
        response = self.client.get("/dataset/upload")
        get_csrf_token(response)


class DatasetUser(HttpUser):
    tasks = [DatasetBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()

class DatasetDownloadUser(HttpUser):
    wait_time = between(1, 3)
    host = get_host_for_locust_testing()

    @task
    def download_dataset(self):
        dataset_id = 1
        response = self.client.get(f"/dataset/download/{dataset_id}")
        if response.status_code == 200:
            print(f"Dataset {dataset_id} descargado correctamente.")
        else:
            print(f"Error al descargar dataset {dataset_id}: {response.status_code}")

class TrendingDatasetsUser(HttpUser):
    @task
    def fetch_trending_datasets(self):
        self.client.get("/dataset/trending")
