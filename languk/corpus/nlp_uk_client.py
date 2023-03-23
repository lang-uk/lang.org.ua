from typing import Union, List, Dict, Optional
from urllib.parse import urljoin

import requests


class NlpUkApiException(Exception):
    pass


class NlpUkClient:
    def __init__(self, base_url: str) -> None:
        self.session = requests.Session()
        self.base_url = base_url

    def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        json: Optional[Dict] = None,
    ) -> requests.models.Response:
        full_url: str = urljoin(self.base_url, url)
        headers = {"Content-Type": "application/json"}
        response = self.session.request(
            method=method, url=full_url, params=params, data=data, json=json, headers=headers
        )

        if response.status_code >= 400:
            raise NlpUkApiException(f"Failed with status {response.status_code}: {response.text}")

        return response

    def batch(self, texts: List[str]) -> List[Dict[str, Union[List, str]]]:
        response = self._request(method="POST", url="/batch", json={"texts": [text for text in texts if text.strip()]})

        resp_iterator = iter(response.json())
        res: List[Dict[str, Union[List, str]]] = []

        for text in texts:
            if text.strip():
                res.append(next(resp_iterator))
            else:
                res.append({"cleanText": "", "tokens": [], "lemmas": [], "sentences": []})

        return res
