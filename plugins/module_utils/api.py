import httpx
from json import JSONDecodeError

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.niceshops.freshdesk.plugins.module_utils.helper import \
    debug_output


class Session:
    def __init__(self, module: AnsibleModule):
        self.m = module
        self.s = self.start()

    def start(self):
        return httpx.Client(
            base_url=f"https://{self.m.params['instance']}.freshdesk.com/api/v2",
            auth=httpx.BasicAuth(username=self.m.params['api_key'], password='X'),
            verify=True,
        )

    def get(self, sub_url: str) -> dict:
        debug_output(
            module=self.m,
            msg=f"REQUEST: GET | URL: {self.s.base_url}{sub_url}"
        )

        return self._get_data(
            self.s.get(sub_url)
        )

    def post(self, sub_url: str, data: dict) -> dict:
        debug_output(
            module=self.m,
            msg=f"REQUEST: POST | "
                f"URL: {self.s.base_url}{sub_url} | "
                f"DATA: {data}"
        )

        return self._get_data(
            self.s.post(url=sub_url, json=data, headers={'Content-Type': 'application/json'})
        )

    def put(self, sub_url: str, data: dict) -> dict:
        debug_output(
            module=self.m,
            msg=f"REQUEST: PUT | "
                f"URL: {self.s.base_url}{sub_url} | "
                f"DATA: {data}"
        )

        return self._get_data(
            self.s.put(url=sub_url, json=data, headers={'Content-Type': 'application/json'})
        )

    def _get_data(self, response: httpx.Response) -> dict:
        if response.status_code not in [200, 201]:
            if response.status_code == 401:
                self.m.fail_json('Authentication failed!')

            else:
                self.m.fail_json(f"Got invalid response: '{response}'")

        try:
            return response.json()

        except JSONDecodeError:
            return {}

    def close(self):
        self.s.close()
