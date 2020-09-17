from rest_framework import status
from background_task import background
from logging import getLogger
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
import requests
from rest_framework.utils import json
import time
from .models import Server
from common.serializers import server_active, server_inactive


from .models import Subscription, Server, ServerType, IpgServer, WebcmServer
from common.serializers import serialize_subscription, server_active, server_inactive, server_starting, server_stopping
logger = getLogger(__name__)


@background(schedule=1)
def demo_task():
    servers = Server.objects.filter(status='Active')
    for server in servers:
        server_id = server.idstr
        server_type = server.server_type.name
        # Check server state
        headers = {'Content-type': 'application/json',
                   'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
        url = 'https://192.168.28.60:6443/apis/apps/v1/namespaces/kube-karel-cloud/deployments/karel-deployment-' + str(server_id) + '/'
        r = requests.get(url, headers=headers, verify=False)
        text = json.loads(r.text)
        status_code = r.status_code

        if status_code == 200:
            # parse response from cluster
            try:
                active = text['status']['availableReplicas']
                if active == 1:
                    server_active(server_id, server_type)
            except:
                inactive = text['status']['unavailableReplicas']
                replicas = text['spec']['replicas']
                if replicas == 0 or inactive == 1:
                    server_inactive(server_id, server_type)
        else:
            # inactive to byp
            server_inactive(server_id, server_type)

    try:
        servers = Server.onjects.filter(status='Inactive')
        for server in servers:
            server_id = server.idstr
            server_type = server.server_type.name
            # Check server state
            headers = {'Content-type': 'application/json',
                       'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
            url = 'https://192.168.28.60:6443/apis/apps/v1/namespaces/kube-karel-cloud/deployments/karel-deployment-' + str(server_id) + '/'
            r = requests.get(url, headers=headers, verify=False)
            text = json.loads(r.text)
            status_code = r.status_code

            if status_code == 200:
                # parse response from cluster
                try:
                    active = text['status']['availableReplicas']
                    if active == 1:
                        server_active(server_id, server_type)
                except:
                    inactive = text['status']['unavailableReplicas']
                    replicas = text['spec']['replicas']
                    if replicas == 0 or inactive == 1:
                        server_inactive(server_id, server_type)
            else:
                # inactive to byp
                server_inactive(server_id, server_type)
        time.sleep(120)
    except ObjectDoesNotExist:
        pass


def subscription_task(subscription_ids):
    for subscription_id in subscription_ids:
        server_idstrs = Server.objects.filter(subscription_id=subscription_id).values_list('idstr', flat=True)
        for server_id in server_idstrs:
            print('=====================================')
            print(server_id)
            print('=====================================')
            server_object = Server.objects.get(idstr=server_id)
            # server_object.subscription = Subscription.objects.get(id=server_object.subscription)
            if server_object.server_type.name == 'IpgServer':
                ipg_server = IpgServer.objects.get(server=server_object.id)
                ip_address = ipg_server.internal_ip
            else:
                webcm_server = WebcmServer.objects.get(server=server_object)
                ip_address = webcm_server.internal_ip

            # Create PVC
            payload = "\r\n\r\n{\"kind\": \"PersistentVolumeClaim\", \"apiVersion\": \"v1\", \"metadata\": {\"name\": \"master-claim-" + str(
                server_id) + "\", \"annotations\": {\"volume.beta.kubernetes.io/storage-class\": \"thin-disk\"}}, \"spec\": {\"accessModes\": [\"ReadWriteOnce\"], \"resources\": {\"requests\": {\"storage\": \"2Gi\"}}}}"
            headers = {'Content-type': 'application/json',
                       'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
            url = 'https://192.168.28.60:6443/api/v1/namespaces/kube-karel-cloud/persistentvolumeclaims'
            r = requests.post(url, data=payload, headers=headers, verify=False)
            print("new method", server_id, payload)
            status_code = r.status_code
            reason = r.reason
            text = r.text
            if status_code != 201:
                payload = {
                    "subscriptions":
                        {
                            "customer": server_object.subscription.customer,
                            "start_date": server_object.subscription.start_date,
                            "end_date": server_object.subscription.end_date,
                            "term_subscription": server_object.subscription.term_subscription,
                            "service_type": server_object.subscription.service_type,
                            "subscription": server_object.subscription.subscription,
                            "service_data": {
                                "server_name_prefix": server_object.subscription.server_name_prefix,
                                "package": server_object.subscription.package,
                                "trunk_service_provider": server_object.subscription.trunk_service_provider,
                                "extra_call_record_package": server_object.subscription.extra_call_record_package,
                                "demo": server_object.subscription.demo,
                                "extra_duration_package": server_object.subscription.extra_duration_package,
                                "exp20_dss_module_ip1141": server_object.exp20_dss_module_ip1141,
                                "exp40_dss_module_ip136_ip138": server_object.exp40_dss_module_ip136_ip138,
                                "ip1111_poe_no_adapter": server_object.ip1111_poe_no_adapter,
                                "ip1131_poe_gigabit_no_adapter": server_object.ip1131_poe_gigabit_no_adapter,
                                "ip1141_poe_no_adapter": server_object.ip1141_poe_no_adapter,
                                "ip1141_ip131_ip132_adapter": server_object.ip1141_ip131_ip132_adapter,
                                "ip1181_ip136_ip138_adapter": server_object.ip1181_ip136_ip138_adapter,
                                "ip1211_w_adapter": server_object.ip1211_w_adapter,
                                "ip1211_poe_no_adapter": server_object.ip1211_poe_no_adapter,
                                "ip1211_ip1211p_ip1111_ip1131_adapter": server_object.ip1211_ip1211p_ip1111_ip1131_adapter,
                                "ip131_poe_no_adapter": server_object.ip131_poe_no_adapter,
                                "ip132_gigabit_no_adapter": server_object.ip132_gigabit_no_adapter,
                                "ip136_poe_no_adapter": server_object.ip136_poe_no_adapter,
                                "ip138_poe_no_adapter": server_object.ip138_poe_no_adapter,
                                "karel_mobile": server_object.karel_mobile,
                                "vp128": server_object.vp128,
                                "yt510": server_object.yt510,
                                "yt520": server_object.yt520,
                                "yt530": server_object.yt530,
                                "servers": ["IpgServer", "WebcmServer"]
                            },
                        }
                }
                headers = {'Content-type': 'application/json'}
                url = 'https://byp.karel.cloud/byp/getbrokensubscriptions/'
                r = requests.get(url, data=payload, headers=headers, verify=False)
                return Response(
                    {
                        "result": False,
                        "msg": "PVC created failed",
                        "status_code": status_code,
                        "reason": reason,
                        "text": text
                    },
                    status=status.HTTP_200_OK
                )

            # Create Deployment
            payload = "{\n\t\"apiVersion\": \"apps/v1\",\n\t\"kind\": \"Deployment\",\n\t\"metadata\": {\n\t\t\"name\": \"karel-deployment-" + str(
                server_id) + "\"\n\t},\n\t\"spec\": {\n\t\t\"selector\": {\n\t\t\t\"matchLabels\": {\n\t\t\t\t\"app\": \"karel-deployment-" + str(
                server_id) + "\"\n\t\t\t}\n\t\t},\n\t\t\"replicas\": 1,\n\t\t\"template\": {\n\t\t\t\"metadata\": {\n\t\t\t\t\"labels\": {\n\t\t\t\t\t\"app\": \"karel-deployment-" + str(
                server_id) + "\"\n\t\t\t\t}\n\t\t\t},\n\t\t\t\"spec\": {\n\t\t\t\t\"containers\": [\n\t\t\t\t\t{\n\t\t\t\t\t\t\"name\": \"karel-deployment-" + str(
                server_id) + "\",\n\t\t\t\t\t\t\"image\": \"leonerath/website\",\n\t\t\t\t\t\t\"imagePullPolicy\": \"Always\",\n\t\t\t\t\t\t\"ports\": [\n\t\t\t\t\t\t\t{\n\t\t\t\t\t\t\t\t\"containerPort\": 3000\n\t\t\t\t\t\t\t}\n\t\t\t\t\t\t],\n\t\t\t\t\t\t\"resources\": {\n\t\t\t\t\t\t\t\"limits\": {\n\t\t\t\t\t\t\t\t\"memory\": \"600Mi\",\n\t\t\t\t\t\t\t\t\"cpu\": 1\n\t\t\t\t\t\t\t},\n\t\t\t\t\t\t\t\"requests\": {\n\t\t\t\t\t\t\t\t\"memory\": \"300Mi\",\n\t\t\t\t\t\t\t\t\"cpu\": \"500m\"\n\t\t\t\t\t\t\t}\n\t\t\t\t\t\t},\n\t\t\t\t\t\t\"volumeMounts\": [\n\t\t\t\t\t\t\t{\n\t\t\t\t\t\t\t\t\"name\": \"karel-master-" + str(
                server_id) + "\",\n\t\t\t\t\t\t\t\t\"mountPath\": \"/data\"\n\t\t\t\t\t\t\t}\n\t\t\t\t\t\t]\n\t\t\t\t\t}\n\t\t\t\t],\n\t\t\t\t\"volumes\": [\n\t\t\t\t\t{\n\t\t\t\t\t\t\"name\": \"karel-master-" + str(
                server_id) + "\",\n\t\t\t\t\t\t\"persistentVolumeClaim\": {\n\t\t\t\t\t\t\t\"claimName\": \"master-claim-" + str(
                server_id) + "\"\n\t\t\t\t\t\t}\n\t\t\t\t\t}\n\t\t\t\t]\n\t\t\t}\n\t\t}\n\t}\n}"
            headers = {'Content-type': 'application/json',
                       'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
            url = 'https://192.168.28.60:6443/apis/apps/v1/namespaces/kube-karel-cloud/deployments'
            r = requests.post(url, data=payload, headers=headers, verify=False)
            print("new method", server_id, payload)
            status_code = r.status_code
            reason = r.reason
            text = r.text
            if r.status_code != 201:
                payload = {
                    "subscriptions":
                        {
                            "customer": server_object.subscription.customer,
                            "start_date": server_object.subscription.start_date,
                            "end_date": server_object.subscription.end_date,
                            "term_subscription": server_object.subscription.term_subscription,
                            "service_type": server_object.subscription.service_type,
                            "subscription": server_object.subscription.subscription,
                            "service_data": {
                                "server_name_prefix": server_object.subscription.server_name_prefix,
                                "package": server_object.subscription.package,
                                "trunk_service_provider": server_object.subscription.trunk_service_provider,
                                "extra_call_record_package": server_object.subscription.extra_call_record_package,
                                "demo": server_object.subscription.demo,
                                "extra_duration_package": server_object.subscription.extra_duration_package,
                                "exp20_dss_module_ip1141": server_object.exp20_dss_module_ip1141,
                                "exp40_dss_module_ip136_ip138": server_object.exp40_dss_module_ip136_ip138,
                                "ip1111_poe_no_adapter": server_object.ip1111_poe_no_adapter,
                                "ip1131_poe_gigabit_no_adapter": server_object.ip1131_poe_gigabit_no_adapter,
                                "ip1141_poe_no_adapter": server_object.ip1141_poe_no_adapter,
                                "ip1141_ip131_ip132_adapter": server_object.ip1141_ip131_ip132_adapter,
                                "ip1181_ip136_ip138_adapter": server_object.ip1181_ip136_ip138_adapter,
                                "ip1211_w_adapter": server_object.ip1211_w_adapter,
                                "ip1211_poe_no_adapter": server_object.ip1211_poe_no_adapter,
                                "ip1211_ip1211p_ip1111_ip1131_adapter": server_object.ip1211_ip1211p_ip1111_ip1131_adapter,
                                "ip131_poe_no_adapter": server_object.ip131_poe_no_adapter,
                                "ip132_gigabit_no_adapter": server_object.ip132_gigabit_no_adapter,
                                "ip136_poe_no_adapter": server_object.ip136_poe_no_adapter,
                                "ip138_poe_no_adapter": server_object.ip138_poe_no_adapter,
                                "karel_mobile": server_object.karel_mobile,
                                "vp128": server_object.vp128,
                                "yt510": server_object.yt510,
                                "yt520": server_object.yt520,
                                "yt530": server_object.yt530,
                                "servers": ["IpgServer", "WebcmServer"]
                            },
                        }
                }
                headers = {'Content-type': 'application/json'}
                url = 'https://byp.karel.cloud/byp/getbrokensubscriptions/'
                r = requests.get(url, data=payload, headers=headers, verify=False)
                return Response(
                    {
                        "result": False,
                        "msg": "Deployment created failed",
                        "status_code": status_code,
                        "reason": reason,
                        "text": text
                    },
                    status=status.HTTP_200_OK
                )

            # Create Service
            payload = "{\n\t\"apiVersion\": \"v1\",\n\t\"kind\": \"Service\",\n\t\"metadata\": {\n\t\t\"name\": \"karel-service-" + str(
                server_id) + "\",\n\t\t\"labels\": {\n\t\t\t\"app\": \"karel-deployment-" + str(
                server_id) + "\"\n\t\t}\n\t},\n\t\"spec\": {\n\t\t\"selector\": {\n\t\t\t\"app\": \"karel-deployment-" + str(
                server_id) + "\"\n\t\t},\n\t\t\"type\": \"NodePort\",\n\t\t\"ports\": [\n\t\t\t{\n\t\t\t\t\"port\": 3000,\n\t\t\t\t\"targetPort\": 3000,\n\t\t\t\t\"nodePort\": null\n\t\t\t}\n\t\t]\n\t}\n}"
            headers = {'Content-type': 'application/json',
                       'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
            url = 'https://192.168.28.60:6443/api/v1/namespaces/kube-karel-cloud/services'
            r = requests.post(url, data=payload, headers=headers, verify=False)
            print("new method", server_id, payload)
            status_code = r.status_code
            reason = r.reason
            text = json.loads(r.text)
            port = text['spec']['ports'][0]['nodePort']
            clusterip = text['spec']['clusterIP']
            if r.status_code != 201:
                payload = {
                    "subscriptions":
                        {
                            "customer": server_object.subscription.customer,
                            "start_date": server_object.subscription.start_date,
                            "end_date": server_object.subscription.end_date,
                            "term_subscription": server_object.subscription.term_subscription,
                            "service_type": server_object.subscription.service_type,
                            "subscription": server_object.subscription.subscription,
                            "service_data": {
                                "server_name_prefix": server_object.subscription.server_name_prefix,
                                "package": server_object.subscription.package,
                                "trunk_service_provider": server_object.subscription.trunk_service_provider,
                                "extra_call_record_package": server_object.subscription.extra_call_record_package,
                                "demo": server_object.subscription.demo,
                                "extra_duration_package": server_object.subscription.extra_duration_package,
                                "exp20_dss_module_ip1141": server_object.exp20_dss_module_ip1141,
                                "exp40_dss_module_ip136_ip138": server_object.exp40_dss_module_ip136_ip138,
                                "ip1111_poe_no_adapter": server_object.ip1111_poe_no_adapter,
                                "ip1131_poe_gigabit_no_adapter": server_object.ip1131_poe_gigabit_no_adapter,
                                "ip1141_poe_no_adapter": server_object.ip1141_poe_no_adapter,
                                "ip1141_ip131_ip132_adapter": server_object.ip1141_ip131_ip132_adapter,
                                "ip1181_ip136_ip138_adapter": server_object.ip1181_ip136_ip138_adapter,
                                "ip1211_w_adapter": server_object.ip1211_w_adapter,
                                "ip1211_poe_no_adapter": server_object.ip1211_poe_no_adapter,
                                "ip1211_ip1211p_ip1111_ip1131_adapter": server_object.ip1211_ip1211p_ip1111_ip1131_adapter,
                                "ip131_poe_no_adapter": server_object.ip131_poe_no_adapter,
                                "ip132_gigabit_no_adapter": server_object.ip132_gigabit_no_adapter,
                                "ip136_poe_no_adapter": server_object.ip136_poe_no_adapter,
                                "ip138_poe_no_adapter": server_object.ip138_poe_no_adapter,
                                "karel_mobile": server_object.karel_mobile,
                                "vp128": server_object.vp128,
                                "yt510": server_object.yt510,
                                "yt520": server_object.yt520,
                                "yt530": server_object.yt530,
                                "servers": ["IpgServer", "WebcmServer"]
                            },
                        }
                }
                headers = {'Content-type': 'application/json'}
                url = 'https://byp.karel.cloud/byp/getbrokensubscriptions/'
                r = requests.get(url, data=payload, headers=headers, verify=False)
                return Response(
                    {
                        "result": False,
                        "msg": "Service created failed",
                        "status_code": status_code,
                        "reason": reason,
                    },
                    status=status.HTTP_200_OK
                )

            # Create Ingress
            payload = "{\n\t\"apiVersion\": \"networking.k8s.io/v1beta1\",\n\t\"kind\": \"Ingress\",\n\t\"metadata\": {\n\t\t\"name\": \"karel-ingress-" + str(
                server_id) + "\",\n\t\t\"annotations\": {\n\t\t\t\"nginx.ingress.kubernetes.io/rewrite-target\": \"/\",\n\t\t\t\"kubernetes.io/ingress.class\": \"nginx\"\n\t\t}\n\t},\n\t\"spec\": {\n\t\t\"rules\": [\n\t\t\t{\n\t\t\t\t\"host\": \"www.kareldeployment.com\",\n\t\t\t\t\"http\": {\n\t\t\t\t\t\"paths\": [\n\t\t\t\t\t\t{\n\t\t\t\t\t\t\t\"path\": \"/" + str(
                server_id) + "\",\n\t\t\t\t\t\t\t\"backend\": {\n\t\t\t\t\t\t\t\t\"serviceName\": \"karel-service-" + str(
                server_id) + "\",\n\t\t\t\t\t\t\t\t\"servicePort\": 3000\n\t\t\t\t\t\t\t}\n\t\t\t\t\t\t}\n\t\t\t\t\t]\n\t\t\t\t}\n\t\t\t}\n\t\t]\n\t}\n}"
            headers = {'Content-type': 'application/json',
                       'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
            url = 'https://192.168.28.60:6443/apis/networking.k8s.io/v1beta1/namespaces/kube-karel-cloud/ingresses'
            r = requests.post(url, data=payload, headers=headers, verify=False)
            print("new method", server_id, payload)
            status_code = r.status_code
            reason = r.reason
            text = r.text
            if r.status_code != 201:
                payload = {
                    "subscriptions":
                        {
                            "customer": server_object.subscription.customer,
                            "start_date": server_object.subscription.start_date,
                            "end_date": server_object.subscription.end_date,
                            "term_subscription": server_object.subscription.term_subscription,
                            "service_type": server_object.subscription.service_type,
                            "subscription": server_object.subscription.subscription,
                            "service_data": {
                                "server_name_prefix": server_object.subscription.server_name_prefix,
                                "package": server_object.subscription.package,
                                "trunk_service_provider": server_object.subscription.trunk_service_provider,
                                "extra_call_record_package": server_object.subscription.extra_call_record_package,
                                "demo": server_object.subscription.demo,
                                "extra_duration_package": server_object.subscription.extra_duration_package,
                                "exp20_dss_module_ip1141": server_object.exp20_dss_module_ip1141,
                                "exp40_dss_module_ip136_ip138": server_object.exp40_dss_module_ip136_ip138,
                                "ip1111_poe_no_adapter": server_object.ip1111_poe_no_adapter,
                                "ip1131_poe_gigabit_no_adapter": server_object.ip1131_poe_gigabit_no_adapter,
                                "ip1141_poe_no_adapter": server_object.ip1141_poe_no_adapter,
                                "ip1141_ip131_ip132_adapter": server_object.ip1141_ip131_ip132_adapter,
                                "ip1181_ip136_ip138_adapter": server_object.ip1181_ip136_ip138_adapter,
                                "ip1211_w_adapter": server_object.ip1211_w_adapter,
                                "ip1211_poe_no_adapter": server_object.ip1211_poe_no_adapter,
                                "ip1211_ip1211p_ip1111_ip1131_adapter": server_object.ip1211_ip1211p_ip1111_ip1131_adapter,
                                "ip131_poe_no_adapter": server_object.ip131_poe_no_adapter,
                                "ip132_gigabit_no_adapter": server_object.ip132_gigabit_no_adapter,
                                "ip136_poe_no_adapter": server_object.ip136_poe_no_adapter,
                                "ip138_poe_no_adapter": server_object.ip138_poe_no_adapter,
                                "karel_mobile": server_object.karel_mobile,
                                "vp128": server_object.vp128,
                                "yt510": server_object.yt510,
                                "yt520": server_object.yt520,
                                "yt530": server_object.yt530,
                                "servers": ["IpgServer", "WebcmServer"]
                            },
                        }
                }
                headers = {'Content-type': 'application/json'}
                url = 'https://byp.karel.cloud/byp/getbrokensubscriptions/'
                r = requests.get(url, data=payload, headers=headers, verify=False)
                return Response(
                    {
                        "result": False,
                        "msg": "Ingress created failed",
                        "status_code": status_code,
                        "reason": reason,
                        "text": text
                    },
                    status=status.HTTP_200_OK
                )
            else:
                IpgServer_server_id = WebcmServer_server_id = server_id

            payload = "{\n\t\"subscription\": \"" + str(
                server_object.subscription.subscription) + "\",\n\t\"service\": \"Ipg\",\n\t\"servers\": {\n\t\t\"IpgServer\": {\n\t\t\t\"cpu\": \"1\",\n\t\t\t\"ram\": \"600Mi\",\n\t\t\t\"disc\": \"2Gi\",\n\t\t\t\"widea_address\": \"www.kareldeployment.com:32370/" + str(
                IpgServer_server_id) + "\",\n\t\t\t\"local_ip\": \"" + str(
                clusterip) + "\",\n\t\t\t\"internal_ip\": \"" + str(ip_address) + ":" + str(
                port) + "\",\n\t\t\t\"external_ip\": \"" + str(ip_address) + ":" + str(
                port) + "\",\n\t\t\t\"server_name\": \"karel-deployment-" + str(
                IpgServer_server_id) + "\",\n\t\t\t\"server_id\": \"" + str(
                IpgServer_server_id) + "\",\n\t\t\t\"state\": \"1\",\n\t\t\t\"fqdn\": \"www.kareldeployment.com:32370/" + str(
                IpgServer_server_id) + "\"\n\t\t},\n\t\t\"WebcmServer\": {\n\t\t\t\"address\": \"www.kareldeployment.com:32370/" + str(
                WebcmServer_server_id) + "\",\n\t\t\t\"local_ip\": \"" + str(
                clusterip) + "\",\n\t\t\t\"internal_ip\": \"" + str(ip_address) + ":" + str(
                port) + "\",\n\t\t\t\"server_name\": \"karel-deployment-" + str(
                WebcmServer_server_id) + "\",\n\t\t\t\"server_id\": \"" + str(
                WebcmServer_server_id) + "\",\n\t\t\t\"state\": \"1\",\n\t\t\t\"fqdn\": \"www.kareldeployment.com:32370/" + str(
                WebcmServer_server_id) + "\"\n\t\t}\n\t}\n}"
            # payload = "{\n        \"subscription\": \"" + str(server_object.subscription_id.subscription) + "\",\n        \"service\": \"Ipg\",\n        \"servers\": {\n                \"IpgServer\": {\n                        \"cpu\": \"1\",\n                        \"ram\": \"600Mi\",\n                        \"disc\": \"2Gi\",\n                        \"widea_address\": \"www.kareldeployment.com:32370/" + str(IpgServer_server_id) + "\",\n                        \"local_ip\": \"" + str(clusterip) + "\",\n                        \"internal_ip\": \"" + str(ip_address) + ":" + str(port) + "\",\n                        \"external_ip\": \"" + str(ip_address) + ":" + str(port) + "\",\n                        \"server_name\": \"karel-deployment-" + str(IpgServer_server_id) + "\",\n                        \"server_id\": \"" + str(IpgServer_server_id) + "\",\n                        \"state\": \"1\",\n                        \"fqdn\": \"www.kareldeployment.com:32370/" + str(IpgServer_server_id) + "\"\n                },\n                \"WebcmServer\": {\n                        \"address\": \"www.kareldeployment.com:32370/" + str(WebcmServer_server_id) + "\",\n                        \"local_ip\": \"" + str(clusterip) + "\",\n                        \"internal_ip\": \"" + str(ip_address) + ":" + str(port) + "\",\n                        \"server_name\": \"karel-deployment-" + str(WebcmServer_server_id) + "\",\n                        \"server_id\": \"" + str(WebcmServer_server_id) + "\",\n                        \"state\": \"1\",\n                        \"fqdn\": \"www.kareldeployment.com:32370/" + str(WebcmServer_server_id) + "\"\n                }\n        }\n}"
            headers = {'Content-type': 'application/json'}
            url = 'https://byp.karel.cloud/byp/updateservicedetail/'
            r = requests.post(url, data=payload, headers=headers, verify=False)
