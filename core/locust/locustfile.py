from locust import HttpUser, task, between

class QuickstartUser(HttpUser):
#    wait_time = between(1, 2.5)
#
    @task
    def post_list(self):
        self.client.get("/blog/api/v1/post")
