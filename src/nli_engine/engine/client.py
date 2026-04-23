from nli_engine.client._generated.authoring_client import ApiClient, Configuration


def build_client(base_url: str = "http://localhost:8080") -> ApiClient:
    return ApiClient(Configuration(host=base_url))
