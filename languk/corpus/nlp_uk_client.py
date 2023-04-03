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
        """
        Make request to NLP-UK API
        :param method: HTTP method
        :param url: relative url
        :param params: params
        :param data: data
        :param json: json
        :return: response
        """
        full_url: str = urljoin(self.base_url, url)
        headers = {"Content-Type": "application/json"}
        response = self.session.request(
            method=method, url=full_url, params=params, data=data, json=json, headers=headers
        )

        if response.status_code >= 400:
            raise NlpUkApiException(f"Failed with status {response.status_code}: {response.text}")

        return response

    def batch(self, texts: List[str]) -> List[Dict[str, Union[List, str]]]:
        """
        Batch request to NLP-UK API
        :param texts: list of texts
        :return: list of dicts with keys: cleanText, tokens, lemmas, sentences
        """
        filtered_texts: List[str] = [text for text in texts if text.strip()]

        if filtered_texts:
            response = self._request(method="POST", url="/batch", json={"texts": filtered_texts})

            resp_iterator = iter(response.json())
        else:
            resp_iterator = iter([])

        res: List[Dict[str, Union[List, str]]] = []

        for text in texts:
            if text.strip():
                res.append(next(resp_iterator))
            else:
                res.append({"cleanText": "", "tokens": [], "lemmas": [], "sentences": []})

        return res
