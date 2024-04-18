from ansible.module_utils.basic import AnsibleModule


def debug_output(module: AnsibleModule, msg: str):
    if 'debug' in module.params and module.params['debug']:
        module.warn(msg)


def get_multiple_pages(session, path: str) -> list:
    max_pages = 100
    page = 1
    data = []

    while page < max_pages:
        page_data = session.get(f"{path}?page={page}")
        data.extend(page_data)

        if len(page_data) < 30:
            break

        page += 1

    return data
