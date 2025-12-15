from locust import HttpUser, TaskSet, task
from datetime import datetime, timedelta, timezone

from core.environment.host import get_host_for_locust_testing


class ExploreBehavior(TaskSet):
    
    @task
    def filter_by_date_and_query(self):
        """Simula una búsqueda con consulta y rango de fechas (ej: últimos 30 días)"""
        
        end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        
        payload = {
            "query": "Test Dataset", 
            "sorting": "newest",
            "publication_type": "any",
            "start_date": start_date,
            "end_date": end_date
        }
        
        response = self.client.post(
            "/explore",
            json=payload,
            name="/explore [POST] - Filter Dates & Query"
        )

        if response.status_code != 200 and response.status_code != 400:
            print(f"Explore POST filter failed: {response.status_code}")

    @task
    def filter_by_publication_and_sorting(self):
        """Simula una búsqueda por tipo de publicación y ordenamiento"""
        
        payload = {
            "query": "",
            "sorting": "oldest",
            "publication_type": "player", 
            "start_date": "",
            "end_date": ""
        }
        
        response = self.client.post(
            "/explore",
            json=payload,
            name="/explore [POST] - Filter Type & Sort"
        )
        
        if response.status_code != 200:
            print(f"Explore POST filter failed: {response.status_code}")
        
    @task
    def load_explore_page(self):
        """Simula la carga inicial de la página /explore (GET)"""
        response = self.client.get(
            "/explore", 
            name="/explore [GET] - Load Page"
        )

        if response.status_code != 200:
            print(f"Explore GET failed: {response.status_code}")

    @task
    def filter_by_extra_field_query(self):
        """Simula una búsqueda por una palabra clave que solo está en extra_fields"""
        
        payload = {
            "query": "Steals", 
            "sorting": "newest",
            "publication_type": "any",
            "start_date": "",
            "end_date": ""
        }
        
        response = self.client.post(
            "/explore",
            json=payload,
            name="/explore [POST] - Filter Extra Fields"
        )

        if response.status_code != 200:
            print(f"Explore POST filter failed: {response.status_code}")


class ExploreUser(HttpUser):
    tasks = [ExploreBehavior]
    min_wait = 5000
    max_wait = 9000
    host = get_host_for_locust_testing()