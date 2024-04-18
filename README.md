# Ansible Module - Freshdesk Mailbox

This Ansible module can be used to create basic FreshDesk mailboxes using [this API](https://developers.freshdesk.com/api/#create_email_mailbox).

Note: Not all API fields are implemented.

The product linked to it has to exist beforehand.

[Read the docs](https://developers.freshdesk.com/api/#getting-started) on how to get your API key.


**Install**:

`ansible-galaxy collection install git+https://github.com/NiceRath/ansible-module-freshdesk-mailbox.git`

**Use:**

```yaml
- name: "Freshdesk | Processing Mailbox"
  niceshopsorg.freshdesk.mailbox:
    instance: '<YOUR-INSTANCE>'  # https://<YOUR-INSTANCE>.freshdesk.com
    api_key: '<YOUR-KEY>'

    mail: 'test@niceshops.com'
    product: 'product_name'
    group: 'group_name'

    # optional
    name: 'test'  # default = product name
    active: true
    product_primary_mail: false  # API-key = default_reply_email
    mailbox_type: 'freshdesk_mailbox'
    debug: false
```
