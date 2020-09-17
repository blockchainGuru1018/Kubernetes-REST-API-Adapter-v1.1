import requests


def serialize_subscription(subscription):
    return {
        "id": subscription.id,
        "customer": subscription.customer,
        "start_date": subscription.start_date,
        "end_date": subscription.end_date,
        "term_subscription": subscription.term_subscription,
        "service_type": subscription.service_type,
        "subscription": subscription.subscription,
        "server_name_prefix": subscription.server_name_prefix,
        "package": subscription.package,
        "trunk_service_provider": subscription.trunk_service_provider,
        "extra_call_record_package": subscription.extra_call_record_package,
        "demo": subscription.demo,
        "extra_duration_package": subscription.extra_duration_package,
    }


def serialize_subscriptionupdaet(subscription):
    return {
        "id": subscription.subscription,
        "customer": subscription.customer,
        "start_date": subscription.start_date,
        "end_date": subscription.end_date,
        "term_subscription": subscription.term_subscription,
        "service_type": subscription.service_type,
        "subscription": subscription.subscription,
        "server_name_prefix": subscription.server_name_prefix,
        "package": subscription.package,
        "trunk_service_provider": subscription.trunk_service_provider,
        "extra_call_record_package": subscription.extra_call_record_package,
        "demo": subscription.demo,
        "extra_duration_package": subscription.extra_duration_package,
    }


def server_active(server_id, server_type):
    payload = "{\r\n    \"state\": 1,\r\n    \"server_id\": \"" + server_id + "\",\r\n    \"server_type\": \"" + server_type + "\"\r\n}"
    headers = {'Content-type': 'application/json'}
    url = 'https://byp.karel.cloud/byp/updateserverstate/'
    r = requests.post(url, data=payload, headers=headers, verify=False)


def server_inactive(server_id, server_type):
    payload = "{\r\n    \"state\": 2,\r\n    \"server_id\": \"" + server_id + "\",\r\n    \"server_type\": \"" + server_type + "\"\r\n}"
    headers = {'Content-type': 'application/json'}
    url = 'https://byp.karel.cloud/byp/updateserverstate/'
    r = requests.post(url, data=payload, headers=headers, verify=False)


def server_starting(server_id, server_type):
    payload = "{\r\n    \"state\": 3,\r\n    \"server_id\": \"" + server_id + "\",\r\n    \"server_type\": \"" + server_type + "\"\r\n}"
    headers = {'Content-type': 'application/json'}
    url = 'https://byp.karel.cloud/byp/updateserverstate/'
    r = requests.post(url, data=payload, headers=headers, verify=False)


def server_stopping(server_id, server_type):
    payload = "{\r\n    \"state\": 4,\r\n    \"server_id\": \"" + server_id + "\",\r\n    \"server_type\": \"" + server_type + "\"\r\n}"
    headers = {'Content-type': 'application/json'}
    url = 'https://byp.karel.cloud/byp/updateserverstate/'
    r = requests.post(url, data=payload, headers=headers, verify=False)
