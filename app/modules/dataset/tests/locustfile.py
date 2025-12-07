from random import random
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
            
class DatasetViewRelatedUser(HttpUser):
    """
    Simula usuarios visitando la vista del dataset.
    Al cargar esta página, el backend ejecuta 'get_related_datasets'.
    """
    wait_time = between(2, 5)
    host = get_host_for_locust_testing()

    test_dois = [
        "10.1234/spurs-ring-winners", 
        "10.1234/east-regular-season-champs",
        "10.1234/west-regular-season-champs",
        "10.1234/playoffs-conference-champs",
        "10.1234/Pau-Gasol-playoffs-teams",
        "10.1234/Michael-Jordan-teams",
    ]

    @task
    def view_dataset_page(self):
        doi = random.choice(self.test_dois)
        
        with self.client.get(f"/doi/{doi}/", catch_response=True) as response:
            
            if response.status_code == 200:
                if "Related Datasets" in response.text:
                    response.success()
                else:
                    response.failure(f"El dataset {doi} cargó pero no veo la sección Related Datasets")
            
            elif response.status_code == 404:
                response.failure(f"DOI no encontrado: {doi} (Revisa la lista test_dois)")
            
            else:
                response.failure(f"Error cargando dataset {doi}: {response.status_code}")
