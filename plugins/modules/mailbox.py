#!/usr/bin/python3

from urllib.parse import quote

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.niceshops.freshdesk.plugins.module_utils.api import Session
from ansible_collections.niceshops.freshdesk.plugins.module_utils.helper import \
    debug_output, get_multiple_pages

# pylint: disable=R0912,R0915


def run_module():
    module_args = dict(
        name=dict(type='str', required=False, description='Using product-name if non is provided'),
        mail=dict(type='str', required=True),
        group=dict(type='str', required=True),
        product=dict(type='str', required=True),
        active=dict(type='bool', required=False, default=True),
        product_primary_mail=dict(type='bool', required=False, default=None),
        mailbox_type=dict(
            type='str', required=False,
            default='freshdesk_mailbox', choices=['freshdesk_mailbox', 'custom_mailbox'],
        ),
        api_key=dict(type='str', required=True, no_log=True),
        instance=dict(type='str', required=True),
        debug=dict(type='bool', required=False, default=False),
    )

    result = dict(
        changed=False,
        diff={
            'before': {},
            'after': {},
        }
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
    )

    if module.params['name'] is None:
        module.params['name'] = module.params['product']

    fd = Session(module=module)

    existing_groups = get_multiple_pages(session=fd, path='groups')
    existing_products = get_multiple_pages(session=fd, path='products')
    found_group, found_product = False, False

    for grp in existing_groups:
        if grp['name'] == module.params['group']:
            module.params['group'] = grp
            found_group = True
            break

    if not found_group:
        module.fail_json(f"Provided group '{module.params['group']}' was not found!")

    for prod in existing_products:
        if prod['name'] == module.params['product']:
            module.params['product'] = prod
            found_product = True
            break

    if not found_product:
        module.fail_json(f"Provided product '{module.params['product']}' was not found!")

    existing_mailbox = fd.get(
        f"email/mailboxes?support_email={quote(module.params['mail'])}"
    )

    if existing_mailbox is None or len(existing_mailbox) == 0:
        if module.params['product_primary_mail'] is None:
            module.params['product_primary_mail'] = False

        debug_output(module=module, msg='CREATING')
        result['changed'] = True
        result['diff']['after'] = {
            'name': module.params['name'],
            'mail': module.params['mail'],
            'active': module.params['active'],
            'product_primary_mail': module.params['product_primary_mail'],
            'group_name': module.params['group']['name'],
            'group_id': module.params['group']['id'],
            'product_name': module.params['product']['name'],
            'product_id': module.params['product']['id'],
        }

        if not module.check_mode:
            fd.post(
                sub_url='email/mailboxes',
                data=dict(
                    name=module.params['name'],
                    support_email=module.params['mail'],
                    group_id=module.params['group']['id'],
                    product_id=module.params['product']['id'],
                    default_reply_email=module.params['product_primary_mail'],
                    mailbox_type=module.params['mailbox_type'],
                )
            )

    else:
        debug_output(module=module, msg='CHECKING FOR CHANGES')
        existing_mailbox = existing_mailbox[0]
        existing_mailbox['group'], existing_mailbox['product'] = None, None

        if existing_mailbox['group_id'] != module.params['group']['id']:
            for grp in existing_groups:
                if grp['id'] == existing_mailbox['group_id']:
                    existing_mailbox['group'] = grp['name']
                    break

        else:
            existing_mailbox['group'] = module.params['group']['name']

        if existing_mailbox['product_id'] != module.params['product']['id']:
            for prod in existing_products:
                if prod['id'] == existing_mailbox['product_id']:
                    existing_mailbox['product'] = prod['name']
                    break

        else:
            existing_mailbox['product'] = module.params['product']['name']

        result['diff']['before'] = {
            'name': existing_mailbox['name'],
            'mail': existing_mailbox['support_email'],
            'mailbox': existing_mailbox['freshdesk_mailbox']['forward_email'],
            'active': existing_mailbox['active'],
            'product_primary_mail': existing_mailbox['default_reply_email'],
            'group_name': existing_mailbox['group'],
            'group_id': existing_mailbox['group_id'],
            'product_name': existing_mailbox['product'],
            'product_id': existing_mailbox['product_id'],
        }

        if module.params['product_primary_mail'] is None:
            module.params['product_primary_mail'] = result['diff']['before']['product_primary_mail']

        result['diff']['after'] = {
            'name': module.params['name'],
            'mail': module.params['mail'],
            'mailbox': result['diff']['before']['mailbox'],
            'active': module.params['active'],
            'product_primary_mail': module.params['product_primary_mail'],
            'group_name': module.params['group']['name'],
            'group_id': module.params['group']['id'],
            'product_name': module.params['product']['name'],
            'product_id': module.params['product']['id'],
        }

        for key in result['diff']['after']:
            if key != 'active':  # cannot be changed using the API
                if result['diff']['before'][key] != result['diff']['after'][key]:
                    result['changed'] = True

            elif result['diff']['before'][key] != result['diff']['after'][key]:
                module.warn(f"Mailbox '{module.params['mail']}' is not active - you need to activate it manually using the WEB-UI!")

        if result['changed']:
            debug_output(module=module, msg='UPDATING')
            if not module.check_mode:
                fd.put(
                    sub_url=f"email/mailboxes/{existing_mailbox['id']}",
                    data=dict(
                        name=module.params['name'],
                        support_email=module.params['mail'],
                        group_id=module.params['group']['id'],
                        product_id=module.params['product']['id'],
                        default_reply_email=module.params['product_primary_mail'],
                        mailbox_type=module.params['mailbox_type'],
                    )
                )

    fd.s.close()
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
