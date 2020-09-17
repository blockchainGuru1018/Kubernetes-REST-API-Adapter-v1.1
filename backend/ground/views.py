from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.utils import json
import requests
import time
import uuid
import random
import socket
import struct

from .serializers import SubscriptionCreateSerializer, ServerStatusSerializer, ChangeServerSerializer, \
    UpdateServiceSerializer, GetbrokenSubscriptionsSerializer
from .models import Subscription, Server, ServerType, IpgServer, WebcmServer
from common.serializers import serialize_subscription, server_active, server_inactive, server_starting, server_stopping

gloval_IpgServer_server_id = global_clusterip = global_ip_address = global_port = global_WebcmServer_server_id = needed_id = 0


class SubscriptionCreateView(GenericAPIView):
    serializer_class = SubscriptionCreateSerializer

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            subscriptions = serializer.data.get('subscriptions')
            subscription_list = []
            subscription_ids = []
            if subscriptions:
                for subscription in subscriptions:
                    customer = subscription['customer']
                    # print('=====================================')
                    # print(customer)
                    # print('=====================================')

                    start_date = subscription['start_date']
                    end_date = subscription['end_date']
                    term_subscription = subscription['term_subscription']
                    service_type = subscription['service_type']
                    subscription_date = subscription['subscription']
                    service_datas = subscription['service_data']
                    if service_datas:
                        subscription_a = Subscription(
                            customer=customer,
                            start_date=start_date,
                            end_date=end_date,
                            term_subscription=term_subscription,
                            service_type=service_type,
                            subscription=subscription_date,
                            state="Initializing",
                            server_name_prefix=str(service_datas['server_name_prefix']),
                            package=str(service_datas['package']),
                            trunk_service_provider=str(service_datas['trunk_service_provider']),
                            extra_call_record_package=str(service_datas['extra_call_record_package']),
                            demo=str(service_datas['demo']),
                            extra_duration_package=str(service_datas['extra_duration_package']),
                            exp20_dss_module_ip1141=str(service_datas['exp20_dss_module_ip1141']),
                            exp40_dss_module_ip136_ip138=str(service_datas['exp40_dss_module_ip136_ip138']),
                            ip1111_poe_no_adapter=str(service_datas['ip1111_poe_no_adapter']),
                            ip1131_poe_gigabit_no_adapter=str(service_datas['ip1131_poe_gigabit_no_adapter']),
                            ip1141_poe_no_adapter=str(service_datas['ip1141_poe_no_adapter']),
                            ip1141_ip131_ip132_adapter=str(service_datas['ip1141_ip131_ip132_adapter']),
                            ip1181_ip136_ip138_adapter=str(service_datas['ip1181_ip136_ip138_adapter']),
                            ip1211_w_adapter=str(service_datas['ip1211_w_adapter']),
                            ip1211_poe_no_adapter=str(service_datas['ip1211_poe_no_adapter']),
                            ip1211_ip1211p_ip1111_ip1131_adapter=str(service_datas['ip1211_ip1211p_ip1111_ip1131_adapter']),
                            ip131_poe_no_adapter=str(service_datas['ip131_poe_no_adapter']),
                            ip132_gigabit_no_adapter=str(service_datas['ip132_gigabit_no_adapter']),
                            ip136_poe_no_adapter=str(service_datas['ip136_poe_no_adapter']),
                            ip138_poe_no_adapter=str(service_datas['ip138_poe_no_adapter']),
                            karel_mobile=str(service_datas['karel_mobile']),
                            vp128=str(service_datas['vp128']),
                            yt510=str(service_datas['yt510']),
                            yt520=str(service_datas['yt520']),
                            yt530=str(service_datas['yt530'])
                        )
                        subscription_a.save()
                        subscription_ids.append(subscription_a.id)
                        # print('=====================================')
                        # print(subscription_a.id)
                        # print('=====================================')
                        servers = service_datas['servers']
                        Servers = []
                        if servers:
                            for server in servers:
                                server = Server(
                                    server_type=ServerType.objects.get(name=server),
                                    action='Stop',
                                    subscription=subscription_a,
                                    idstr='d-' + uuid.uuid4().hex[:8]
                                )
                                server.save()
                                ip = "192.168.28."
                                ip += ".".join(map(str, (random.randint(50, 55)for _ in range(1))))
                                # ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
                                if server.server_type.name == "IpgServer":
                                    ipg = IpgServer()
                                    ipg.server = server
                                    ipg.external_ip = ip
                                    ipg.internal_ip = ip
                                    ipg.save()
                                elif server.server_type.name == "WebcmServer":
                                    webcm = WebcmServer()
                                    webcm.server = server
                                    webcm.internal_ip = ip
                                    webcm.save()
                                Servers.append(server.server_type.name)
                        subscription_list.append({
                            **serialize_subscription(subscription_a),
                            "servers": Servers
                        })
            return Response(
                {
                    "result": True,
                    "Message": "Service Created successfully and Server Created Request sent to BYP"
                },
                status=status.HTTP_200_OK
            )

        finally:
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
                        url = 'http://byp.karel.cloud/byp/getbrokensubscriptions/'
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
                    payload = "{\n\t\"apiVersion\": \"v1\",\n\t\"kind\": \"Service\",\n\t\"metadata\": {\n\t\t\"name\": \"karel-service-" + str(server_id) + "\",\n\t\t\"labels\": {\n\t\t\t\"app\": \"karel-deployment-" + str(server_id) + "\"\n\t\t}\n\t},\n\t\"spec\": {\n\t\t\"selector\": {\n\t\t\t\"app\": \"karel-deployment-" + str(server_id) + "\"\n\t\t},\n\t\t\"type\": \"NodePort\",\n\t\t\"ports\": [\n\t\t\t{\n\t\t\t\t\"port\": 3000,\n\t\t\t\t\"targetPort\": 3000,\n\t\t\t\t\"nodePort\": null\n\t\t\t}\n\t\t]\n\t}\n}"
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
                        url = 'http://byp.karel.cloud/byp/getbrokensubscriptions/'
                        r = requests.get(url, data=payload, headers=headers, verify=False)
                        return Response(
                            {
                                "result": False,
                                "msg": "Service created faild",
                                "status_code": status_code,
                                "reason": reason,
                            },
                            status=status.HTTP_200_OK
                        )

                    # Create Ingress
                    payload = "{\n\t\"apiVersion\": \"networking.k8s.io/v1beta1\",\n\t\"kind\": \"Ingress\",\n\t\"metadata\": {\n\t\t\"name\": \"karel-ingress-" + str(server_id) + "\",\n\t\t\"annotations\": {\n\t\t\t\"nginx.ingress.kubernetes.io/rewrite-target\": \"/\",\n\t\t\t\"kubernetes.io/ingress.class\": \"nginx\"\n\t\t}\n\t},\n\t\"spec\": {\n\t\t\"rules\": [\n\t\t\t{\n\t\t\t\t\"host\": \"www.kareldeployment.com\",\n\t\t\t\t\"http\": {\n\t\t\t\t\t\"paths\": [\n\t\t\t\t\t\t{\n\t\t\t\t\t\t\t\"path\": \"/" + str(server_id) + "\",\n\t\t\t\t\t\t\t\"backend\": {\n\t\t\t\t\t\t\t\t\"serviceName\": \"karel-service-" + str(server_id) + "\",\n\t\t\t\t\t\t\t\t\"servicePort\": 3000\n\t\t\t\t\t\t\t}\n\t\t\t\t\t\t}\n\t\t\t\t\t]\n\t\t\t\t}\n\t\t\t}\n\t\t]\n\t}\n}"
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
                        url = 'http://byp.karel.cloud/byp/getbrokensubscriptions/'
                        r = requests.get(url, data=payload, headers=headers, verify=False)
                        return Response(
                            {
                                "result": False,
                                "msg": "Ingress created faild",
                                "status_code": status_code,
                                "reason": reason,
                                "text": text
                            },
                            status=status.HTTP_200_OK
                        )
                    else:
                        IpgServer_server_id = WebcmServer_server_id = server_id

                    payload = "{\n\t\"subscription\": \"" + str(server_object.subscription.subscription) + "\",\n\t\"service\": \"Ipg\",\n\t\"servers\": {\n\t\t\"IpgServer\": {\n\t\t\t\"cpu\": \"cpu\",\n\t\t\t\"ram\": \"ram\",\n\t\t\t\"disc\": \"disc\",\n\t\t\t\"widea_address\": \"www.kareldeployment.com:32370/" + str(IpgServer_server_id) + "\",\n\t\t\t\"local_ip\": \"" + str(clusterip) + "\",\n\t\t\t\"internal_ip\": \"" + str(ip_address) + ":" + str(port) + "\",\n\t\t\t\"external_ip\": \"" + str(ip_address) + ":" + str(port) + "\",\n\t\t\t\"server_name\": \"karel-deployment-" + str(IpgServer_server_id) + "\",\n\t\t\t\"server_id\": \"" + str(IpgServer_server_id) + "\",\n\t\t\t\"state\": \"1\",\n\t\t\t\"fqdn\": \"www.kareldeployment.com:32370/" + str(IpgServer_server_id) + "\"\n\t\t},\n\t\t\"WebcmServer\": {\n\t\t\t\"address\": \"www.kareldeployment.com:32370/" + str(WebcmServer_server_id) + "\",\n\t\t\t\"local_ip\": \"" + str(clusterip) + "\",\n\t\t\t\"internal_ip\": \"" + str(ip_address) + ":" + str(port) + "\",\n\t\t\t\"server_name\": \"karel-deployment-" + str(WebcmServer_server_id) + "\",\n\t\t\t\"server_id\": \"" + str(WebcmServer_server_id) + "\",\n\t\t\t\"state\": \"1\",\n\t\t\t\"fqdn\": \"www.kareldeployment.com:32370/" + str(WebcmServer_server_id) + "\"\n\t\t}\n\t}\n}"
                    # payload = "{\n        \"subscription\": \"" + str(server_object.subscription_id.subscription) + "\",\n        \"service\": \"Ipg\",\n        \"servers\": {\n                \"IpgServer\": {\n                        \"cpu\": \"1\",\n                        \"ram\": \"600Mi\",\n                        \"disc\": \"2Gi\",\n                        \"widea_address\": \"www.kareldeployment.com:32370/" + str(IpgServer_server_id) + "\",\n                        \"local_ip\": \"" + str(clusterip) + "\",\n                        \"internal_ip\": \"" + str(ip_address) + ":" + str(port) + "\",\n                        \"external_ip\": \"" + str(ip_address) + ":" + str(port) + "\",\n                        \"server_name\": \"karel-deployment-" + str(IpgServer_server_id) + "\",\n                        \"server_id\": \"" + str(IpgServer_server_id) + "\",\n                        \"state\": \"1\",\n                        \"fqdn\": \"www.kareldeployment.com:32370/" + str(IpgServer_server_id) + "\"\n                },\n                \"WebcmServer\": {\n                        \"address\": \"www.kareldeployment.com:32370/" + str(WebcmServer_server_id) + "\",\n                        \"local_ip\": \"" + str(clusterip) + "\",\n                        \"internal_ip\": \"" + str(ip_address) + ":" + str(port) + "\",\n                        \"server_name\": \"karel-deployment-" + str(WebcmServer_server_id) + "\",\n                        \"server_id\": \"" + str(WebcmServer_server_id) + "\",\n                        \"state\": \"1\",\n                        \"fqdn\": \"www.kareldeployment.com:32370/" + str(WebcmServer_server_id) + "\"\n                }\n        }\n}"
                    headers = {'Content-type': 'application/json'}
                    url = 'https://byp.karel.cloud/byp/updateservicedetail/'
                    r = requests.post(url, data=payload, headers=headers, verify=False)


class SubscriptionDeleteView(GenericAPIView):

    def delete(self, request, pk):
        is_subscription = Subscription.objects.filter(subscription=pk).exists()
        if is_subscription:
            Subscription.objects.filter(subscription=pk).delete()
            return Response(
                {
                    "result": True,
                    "errorMsg": "Removed successfully."
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "result": False,
                    "errorMsg": "Invalid subscription."
                },
                status=status.HTTP_200_OK
            )


class SubscriptionDetailView(GenericAPIView):

    def get(self, request, pk):
        try:
            subscription = Subscription.objects.get(id=pk)
            return Response(
                {
                    "result": True,
                    "subscription": {
                        **serialize_subscription(subscription)
                    }

                },
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "result": False,
                    "errorMsg": "Invalid subscription."
                },
                status=status.HTTP_200_OK
            )


class ControlServerView(GenericAPIView):
    serializer_class = ServerStatusSerializer

    def post(self, request):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            server_ids = serializer.data.get('server_ids')
            action = serializer.data.get('action')
            server_type = serializer.data.get('server_type')
            for server_id in server_ids:
                try:
                    server = Server.objects.get(idstr=server_id)
                    server.action = action
                    server.server_type = ServerType.objects.get(name=server_type)
                    server.save()

                except ObjectDoesNotExist:
                    return Response(
                        {
                            "result": False,
                            "Bad Operation": "Can't find matched server with server_ids"
                        },
                        status=status.HTTP_200_OK
                    )

            return Response(
                {
                    "result": True,
                    "subscriptions": {
                        "msg": "server status changed successfully."
                    }
                },
                status=status.HTTP_200_OK
            )

        finally:
            for server_id in server_ids:
                server = Server.objects.get(idstr=server_id)
                server_type = server.server_type.name
                action = server.action

                if action == 'Stop':

                    # Request Stop server to Cluster
                    payload = "{\r\n    \"apiVersion\": \"apps/v1\",\r\n    \"kind\": \"Deployment\",\r\n    \"metadata\": {\r\n        \"name\": \"karel-deployment-" + server_id + "\"\r\n    },\r\n    \"spec\": {\r\n        \"selector\": {\r\n            \"matchLabels\": {\r\n                \"app\": \"karel-deployment-" + server_id + "\"\r\n            }\r\n        },\r\n        \"replicas\": 0,\r\n        \"template\": {\r\n            \"metadata\": {\r\n                \"labels\": {\r\n                    \"app\": \"karel-deployment-" + server_id + "\"\r\n                }\r\n            },\r\n            \"spec\": {\r\n                \"containers\": [\r\n                    {\r\n                        \"name\": \"karel-deployment-" + server_id + "\",\r\n                        \"image\": \"leonerath/website\",\r\n                        \"imagePullPolicy\": \"Always\",\r\n                        \"ports\": [\r\n                            {\r\n                                \"containerPort\": 3000\r\n                            }\r\n                        ],\r\n                        \"resources\": {\r\n                            \"limits\": {\r\n                                \"memory\": \"600Mi\",\r\n                                \"cpu\": 1\r\n                            },\r\n                            \"requests\": {\r\n                                \"memory\": \"300Mi\", \"cpu\": \"500m\"\r\n                            }\r\n                        },\r\n                        \"volumeMounts\": [\r\n                            {\r\n                                \"name\": \"karel-master-data\",\r\n                                \"mountPath\": \"/data\"\r\n                            }\r\n                        ]\r\n                    }\r\n                ],\r\n                \"volumes\": [\r\n                    {\r\n                        \"name\": \"karel-master-data\",\r\n                        \"persistentVolumeClaim\": {\r\n                            \"claimName\": \"master-claim-" + server_id + "\"\r\n                        }\r\n                    }\r\n                ]\r\n            }\r\n        }\r\n    }\r\n}"
                    headers = {'Content-type': 'application/json',
                               'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
                    url = 'https://192.168.28.60:6443/apis/apps/v1/namespaces/kube-karel-cloud/deployments/karel-deployment-' + str(server_id) + '/'
                    r = requests.put(url, data=payload, headers=headers, verify=False)
                    status_code = r.status_code

                    if status_code == 200:
                        # change server status
                        server_stopping(server_id, server_type)

                        # Check server state
                        headers = {'Content-type': 'application/json',
                                   'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
                        url = 'https://192.168.28.60:6443/apis/apps/v1/namespaces/kube-karel-cloud/deployments/karel-deployment-' + str(server_id) + '/'
                        r = requests.get(url, headers=headers, verify=False)
                        text = json.loads(r.text)
                        status_code = r.status_code

                        if status_code == 200:
                            # parse response from cluster
                            if not text['status'] != 'Failure':
                                if text['status']['availableReplicas']:
                                    active = text['status']['availableReplicas']
                                    if active == 1:
                                        server_active(server_id, server_type)
                                else:
                                    inactive = text['status']['unavailableReplicas']
                                    replicas = text['spec']['replicas']
                                    if replicas == 0 or inactive == 1:
                                        server_inactive(server_id, server_type)
                            else:
                                server_inactive(server_id, server_type)
                        else:
                            # inactive to byp
                            server_inactive(server_id, server_type)
                    else:
                        # inactive to byp
                        server_inactive(server_id, server_type)

                elif action == 'Start':

                    # Request Start server to Cluster
                    payload = "{\r\n    \"apiVersion\": \"apps/v1\",\r\n    \"kind\": \"Deployment\",\r\n    \"metadata\": {\r\n        \"name\": \"karel-deployment-" + server_id + "\"\r\n    },\r\n    \"spec\": {\r\n        \"selector\": {\r\n            \"matchLabels\": {\r\n                \"app\": \"karel-deployment-" + server_id + "\"\r\n            }\r\n        },\r\n        \"replicas\": 1,\r\n        \"template\": {\r\n            \"metadata\": {\r\n                \"labels\": {\r\n                    \"app\": \"karel-deployment-" + server_id + "\"\r\n                }\r\n            },\r\n            \"spec\": {\r\n                \"containers\": [\r\n                    {\r\n                        \"name\": \"karel-deployment-" + server_id + "\",\r\n                        \"image\": \"leonerath/website\",\r\n                        \"imagePullPolicy\": \"Always\",\r\n                        \"ports\": [\r\n                            {\r\n                                \"containerPort\": 3000\r\n                            }\r\n                        ],\r\n                        \"resources\": {\r\n                            \"limits\": {\"memory\": \"600Mi\",\r\n                                        \"cpu\": 1\r\n                                        },\r\n                            \"requests\": {\r\n                                \"memory\": \"300Mi\",\r\n                                \"cpu\": \"500m\"\r\n                            }\r\n                        },\r\n                        \"volumeMounts\": [\r\n                            {\r\n                                \"name\": \"karel-master-data\",\r\n                                \"mountPath\": \"/data\"\r\n                            }\r\n                        ]\r\n                    }\r\n                ],\r\n                \"volumes\": [\r\n                    {\r\n                        \"name\": \"karel-master-data\",\r\n                        \"persistentVolumeClaim\": {\r\n                            \"claimName\": \"master-claim-" + server_id + "\"\r\n                        }\r\n                    }\r\n                ]\r\n            }\r\n        }\r\n    }\r\n}"
                    headers = {'Content-type': 'application/json',
                               'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
                    url = 'https://192.168.28.60:6443/apis/apps/v1/namespaces/kube-karel-cloud/deployments/karel-deployment-' + str(server_id) + '/'
                    r = requests.put(url, data=payload, headers=headers, verify=False)
                    status_code = r.status_code

                    if status_code == 200:
                        # change server status
                        server_starting(server_id, server_type)

                        # Check server state
                        headers = {'Content-type': 'application/json',
                                   'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
                        url = 'https://192.168.28.60:6443/apis/apps/v1/namespaces/kube-karel-cloud/deployments/karel-deployment-' + str(server_id) + '/'
                        r = requests.get(url, headers=headers, verify=False)
                        text = json.loads(r.text)
                        status_code = r.status_code

                        if status_code == 200:
                            # parse response from cluster
                            if not text['status'] != 'Failure':
                                if text['status']['availableReplicas']:
                                    active = text['status']['availableReplicas']
                                    if active == 1:
                                        server_active(server_id, server_type)
                                else:
                                    inactive = text['status']['unavailableReplicas']
                                    replicas = text['spec']['replicas']
                                    if replicas == 0 or inactive == 1:
                                        server_inactive(server_id, server_type)
                        else:
                            # inactive to byp
                            server_inactive(server_id, server_type)
                    else:
                        # inactive to byp
                        server_inactive(server_id, server_type)

                elif action == 'Restart':

                    # Request Stop server to Cluster
                    payload = "{\r\n    \"apiVersion\": \"apps/v1\",\r\n    \"kind\": \"Deployment\",\r\n    \"metadata\": {\r\n        \"name\": \"karel-deployment-" + server_id + "\"\r\n    },\r\n    \"spec\": {\r\n        \"selector\": {\r\n            \"matchLabels\": {\r\n                \"app\": \"karel-deployment-" + server_id + "\"\r\n            }\r\n        },\r\n        \"replicas\": 0,\r\n        \"template\": {\r\n            \"metadata\": {\r\n                \"labels\": {\r\n                    \"app\": \"karel-deployment-" + server_id + "\"\r\n                }\r\n            },\r\n            \"spec\": {\r\n                \"containers\": [\r\n                    {\r\n                        \"name\": \"karel-deployment-" + server_id + "\",\r\n                        \"image\": \"leonerath/website\",\r\n                        \"imagePullPolicy\": \"Always\",\r\n                        \"ports\": [\r\n                            {\r\n                                \"containerPort\": 3000\r\n                            }\r\n                        ],\r\n                        \"resources\": {\r\n                            \"limits\": {\r\n                                \"memory\": \"600Mi\",\r\n                                \"cpu\": 1\r\n                            },\r\n                            \"requests\": {\r\n                                \"memory\": \"300Mi\", \"cpu\": \"500m\"\r\n                            }\r\n                        },\r\n                        \"volumeMounts\": [\r\n                            {\r\n                                \"name\": \"karel-master-data\",\r\n                                \"mountPath\": \"/data\"\r\n                            }\r\n                        ]\r\n                    }\r\n                ],\r\n                \"volumes\": [\r\n                    {\r\n                        \"name\": \"karel-master-data\",\r\n                        \"persistentVolumeClaim\": {\r\n                            \"claimName\": \"master-claim-" + server_id + "\"\r\n                        }\r\n                    }\r\n                ]\r\n            }\r\n        }\r\n    }\r\n}"
                    headers = {'Content-type': 'application/json',
                               'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
                    url = 'https://192.168.28.60:6443/apis/apps/v1/namespaces/kube-karel-cloud/deployments/karel-deployment-' + str(server_id) + '/'
                    r = requests.put(url, data=payload, headers=headers, verify=False)
                    status_code = r.status_code

                    if status_code == 200:
                        # change server status
                        server_stopping(server_id, server_type)

                        # Check server state
                        headers = {'Content-type': 'application/json',
                                   'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
                        url = 'https://192.168.28.60:6443/apis/apps/v1/namespaces/kube-karel-cloud/deployments/karel-deployment-' + str(server_id) + '/'
                        r = requests.get(url, headers=headers, verify=False)
                        text = json.loads(r.text)
                        status_code = r.status_code

                        if status_code == 200:
                            # parse response from cluster
                            if not text['status'] != 'Failure':
                                if text['status']['availableReplicas']:
                                    active = text['status']['availableReplicas']
                                    if active == 1:
                                        server_active(server_id, server_type)
                                else:
                                    inactive = text['status']['unavailableReplicas']
                                    replicas = text['spec']['replicas']
                                    if replicas == 0 or inactive == 1:
                                        server_inactive(server_id, server_type)
                        else:
                            # inactive to byp
                            server_inactive(server_id, server_type)
                    else:
                        # inactive to byp
                        server_inactive(server_id, server_type)

                    # Request Start server to Cluster
                    payload = "{\r\n    \"apiVersion\": \"apps/v1\",\r\n    \"kind\": \"Deployment\",\r\n    \"metadata\": {\r\n        \"name\": \"karel-deployment-" + server_id + "\"\r\n    },\r\n    \"spec\": {\r\n        \"selector\": {\r\n            \"matchLabels\": {\r\n                \"app\": \"karel-deployment-" + server_id + "\"\r\n            }\r\n        },\r\n        \"replicas\": 1,\r\n        \"template\": {\r\n            \"metadata\": {\r\n                \"labels\": {\r\n                    \"app\": \"karel-deployment-" + server_id + "\"\r\n                }\r\n            },\r\n            \"spec\": {\r\n                \"containers\": [\r\n                    {\r\n                        \"name\": \"karel-deployment-" + server_id + "\",\r\n                        \"image\": \"leonerath/website\",\r\n                        \"imagePullPolicy\": \"Always\",\r\n                        \"ports\": [\r\n                            {\r\n                                \"containerPort\": 3000\r\n                            }\r\n                        ],\r\n                        \"resources\": {\r\n                            \"limits\": {\"memory\": \"600Mi\",\r\n                                        \"cpu\": 1\r\n                                        },\r\n                            \"requests\": {\r\n                                \"memory\": \"300Mi\",\r\n                                \"cpu\": \"500m\"\r\n                            }\r\n                        },\r\n                        \"volumeMounts\": [\r\n                            {\r\n                                \"name\": \"karel-master-data\",\r\n                                \"mountPath\": \"/data\"\r\n                            }\r\n                        ]\r\n                    }\r\n                ],\r\n                \"volumes\": [\r\n                    {\r\n                        \"name\": \"karel-master-data\",\r\n                        \"persistentVolumeClaim\": {\r\n                            \"claimName\": \"master-claim-" + server_id + "\"\r\n                        }\r\n                    }\r\n                ]\r\n            }\r\n        }\r\n    }\r\n}"
                    headers = {'Content-type': 'application/json',
                               'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
                    url = 'https://192.168.28.60:6443/apis/apps/v1/namespaces/kube-karel-cloud/deployments/karel-deployment-' + str(server_id) + '/'
                    r = requests.put(url, data=payload, headers=headers, verify=False)
                    status_code = r.status_code

                    if status_code == 200:
                        # change server status
                        server_starting(server_id, server_type)

                        # Check server state
                        headers = {'Content-type': 'application/json',
                                   'authorization': 'bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IiJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImRlZmF1bHQtdG9rZW4tMmM4dnMiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZGVmYXVsdCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50LnVpZCI6ImI2ZDMwOTdlLTk1MjYtNDQwZi05MTdkLTRkYmExMmYwM2JlNyIsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDpkZWZhdWx0OmRlZmF1bHQifQ.WuCzioQAqzUkeVH-NwjRPZk1usasVfCc3MS9W7sKVF7hYefmCM4PP1dGfIxeA9qVwDrg5Tmm9hzzqKTWym1sbUzlxvYUi0jac-cjWD9k8_g3IF7bW00b7w2jjJ3k5f0ogZyy4aGr0HLhJswencfElE-yOqTtB6AxWc-SReJ2Diq_M-LepUK5iEi9x7JXigBZ2JPa-PpYvDyG6167s9JJdklzHSNQIKV1i81qYyrkmSCqEbnerOU8EzaphCfibOsyyrJxqI_nbB-zoUscsbb8SPMnUozy6NonvOaO-8EZfQ_lyeLmB6KNMUwUFVLxHNUaFZs-R1LYztM8A5HVeD6dkw'}
                        url = 'https://192.168.28.60:6443/apis/apps/v1/namespaces/kube-karel-cloud/deployments/karel-deployment-' + str(server_id) + '/'
                        r = requests.get(url, headers=headers, verify=False)
                        text = json.loads(r.text)
                        status_code = r.status_code

                        if status_code == 200:
                            # parse response from cluster
                            if not text['status'] != 'Failure':
                                if text['status']['availableReplicas']:
                                    active = text['status']['availableReplicas']
                                    if active == 1:
                                        server_active(server_id, server_type)
                                else:
                                    inactive = text['status']['unavailableReplicas']
                                    replicas = text['spec']['replicas']
                                    if replicas == 0 or inactive == 1:
                                        server_inactive(server_id, server_type)
                        else:
                            # inactive to byp
                            server_inactive(server_id, server_type)
                    else:
                        # inactive to byp
                        server_inactive(server_id, server_type)


class UpdateServiceDetail(GenericAPIView):
    serializer_class = UpdateServiceSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subscription = serializer.validated_data['subscription']
        print(subscription.id)
        subscription_list = []

        servers = request.data.get('servers')
        ipgserver_input = servers['IpgServer']
        ipgserver_object_id = Server.objects.filter(subscription=subscription).values_list('id', flat=True)[0]
        ipgserver = IpgServer.objects.get(server=ipgserver_object_id)
        ipgserver.cpu = ipgserver_input['cpu']
        ipgserver.ram = ipgserver_input['ram']
        ipgserver.disc = ipgserver_input['disc']
        ipgserver.widea_address = ipgserver_input['widea_address']
        ipgserver.local_ip = ipgserver_input['local_ip']
        ipgserver.internal_ip = ipgserver_input['internal_ip']
        ipgserver.external_ip = ipgserver_input['external_ip']
        ipgserver.server_name = ipgserver_input['server_name']
        ipgserver.state = ipgserver_input['state']
        ipgserver.fqdn = ipgserver_input['fqdn']
        ipgserver.save()

        webcmServer_input = servers['WebcmServer']
        webcmserver_object_id = Server.objects.filter(subscription=subscription).values_list('id', flat=True)[1]
        webcmserver = WebcmServer.objects.get(server=webcmserver_object_id)
        webcmserver.address = webcmServer_input['address']
        webcmserver.local_ip = webcmServer_input['local_ip']
        webcmserver.internal_ip = webcmServer_input['internal_ip']
        webcmserver.server_name = webcmServer_input['server_name']
        webcmserver.state = webcmServer_input['state']
        webcmserver.fqdn = webcmServer_input['fqdn']
        webcmserver.save()

        return Response(
            {
                "result": True,
                "subscription": subscription.subscription,
                "service": "Ipg",
                "servers": {
                    "IpgServer": {
                        "cpu": ipgserver.cpu,
                        "ram": ipgserver.ram,
                        "disc": ipgserver.disc,
                        "widea_address": ipgserver.widea_address,
                        "local_ip": ipgserver.local_ip,
                        "internal_ip": ipgserver.internal_ip,
                        "external_ip": ipgserver.external_ip,
                        "server_name": ipgserver.server_name,
                        "server_id": ipgserver.server.id,
                        "state": ipgserver.state,
                        "fqdn": ipgserver.fqdn,
                    },
                    "WebcmServer": {
                        "address": webcmserver.address,
                        "local_ip": webcmserver.local_ip,
                        "internal_ip": webcmserver.internal_ip,
                        "server_name": webcmserver.server_name,
                        "server_id": webcmserver.server.id,
                        "state": webcmserver.state,
                        "fqdn": webcmserver.fqdn,
                    }
                }

            },
            status=status.HTTP_200_OK
        )


class ChangeServerView(GenericAPIView):
    serializer_class = ChangeServerSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        server = serializer.validated_data['server']
        server.status = serializer.data.get('status')
        server.server_type = serializer.validated_data['server_type']
        server.save()

        return Response(
            {
                "result": True,
                "subscriptions": {
                    "status": server.status,
                    "server_id": server.id,
                    "server_type": server.server_type.name,
                }
            },
            status=status.HTTP_200_OK
        )


class GetBrokenSubscriptionsView(GenericAPIView):
    serializer_class = GetbrokenSubscriptionsSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        subscriptions = serializer.data.get('subscriptions')
        subscription_list = []
        if subscriptions:
            for subscription in subscriptions:
                subscription_a = Subscription(
                    customer=subscription['customer'],
                    start_date=subscription['start_date'],
                    end_date=subscription['end_date'],
                    term_subscription=subscription['term_subscription'],
                    service_type=subscription['service_type'],
                    subscription=subscription['subscription'],
                    server_name_prefix=subscription['server_name_prefix'],
                    package=subscription['package'],
                    trunk_service_provider=subscription['trunk_service_provider'],
                    extra_call_record_package=subscription['extra_call_record_package'],
                    demo=subscription['demo'],
                    extra_duration_package=subscription['extra_duration_package'],
                    state="Initializing"
                )
                subscription_a.save()
                servers = subscription['servers']
                Servers = []
                if servers:
                    for server in servers:
                        server = Server(
                            server_type=ServerType.objects.get(name=server),
                            action='Stop',
                            subscription=subscription_a
                        )
                        server.save()
                        if server.server_type.name == "IpgServer":
                            ipg = IpgServer()
                            ipg.server = server
                            ipg.save()
                        elif server.server_type.name == "WebcmServer":
                            webcm = WebcmServer()
                            webcm.server = server
                            webcm.save()
                        Servers.append(server.server_type.name)
                subscription_list.append({
                    **serialize_subscription(subscription_a),
                    "servers": Servers
                })

        return Response(
            {
                "result": True,
                "subscriptions": subscription_list

            },
            status=status.HTTP_200_OK
        )


class EverySoOften(GenericAPIView):

    def post(self, request):
        while True:
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
            time.sleep(30)

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
                time.sleep(2)
            except ObjectDoesNotExist:
                pass
        return True


class Initialized(GenericAPIView):

    def post(self, request):
        while True:
            payload = "{\n        \"subscription\": \"" + str(needed_id) + "\",\n        \"service\": \"Ipg\",\n        \"servers\": {\n                \"IpgServer\": {\n                        \"cpu\": \"1\",\n                        \"ram\": \"600Mi\",\n                        \"disc\": \"2Gi\",\n                        \"widea_address\": \"www.kareldeployment.com:32370/" + str(gloval_IpgServer_server_id) + "\",\n                        \"local_ip\": \"" + str(global_clusterip) + "\",\n                        \"internal_ip\": \"" + str(global_ip_address) + ":" + str(global_port) + "\",\n                        \"external_ip\": \"" + str(global_ip_address) + ":" + str(global_port) + "\",\n                        \"server_name\": \"karel-deployment-" + str(gloval_IpgServer_server_id) + "\",\n                        \"server_id\": \"" + str(gloval_IpgServer_server_id) + "\",\n                        \"state\": \"1\",\n                        \"fqdn\": \"www.kareldeployment.com:32370/" + str(gloval_IpgServer_server_id) + "\"\n                },\n                \"WebcmServer\": {\n                        \"address\": \"www.kareldeployment.com:32370/" + str(global_WebcmServer_server_id) + "\",\n                        \"local_ip\": \"" + str(global_clusterip) + "\",\n                        \"internal_ip\": \"" + str(global_ip_address) + ":" + str(global_port) + "\",\n                        \"server_name\": \"karel-deployment-" + str(global_WebcmServer_server_id) + "\",\n                        \"server_id\": \"" + str(global_WebcmServer_server_id) + "\",\n                        \"state\": \"1\",\n                        \"fqdn\": \"www.kareldeployment.com:32370/" + str(global_WebcmServer_server_id) + "\"\n                }\n        }\n}"
            headers = {'Content-type': 'application/json'}
            url = 'https://byp.karel.cloud/byp/updateservicedetail/'
            r = requests.post(url, data=payload, headers=headers, verify=False)
            time.sleep(1)
        return True
