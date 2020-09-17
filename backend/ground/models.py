from django.db import models
from common.models import BaseModel


class ServerType(models.Model):
    class Meta:
        db_table = 'ServerType'
    name = models.CharField(blank=False, max_length=255)

    def __str__(self):
        return self.name


class Subscription(BaseModel):
    class Meta:
        db_table = 'subscription'
    customer = models.CharField(blank=False, max_length=255)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    term_subscription = models.CharField(blank=False, max_length=255)
    # service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE)
    service_type = models.CharField(blank=False, max_length=255, default="Ipg")
    subscription = models.CharField(blank=False, max_length=255)
    server_name_prefix = models.CharField(blank=False, max_length=255)
    package = models.CharField(blank=False, max_length=255)
    trunk_service_provider = models.CharField(blank=False, max_length=255)
    extra_call_record_package = models.CharField(blank=False, max_length=255)
    demo = models.CharField(blank=False, max_length=255)
    extra_duration_package = models.CharField(blank=False, max_length=255)
    exp20_dss_module_ip1141 = models.CharField(blank=False, max_length=255, default="0")
    exp40_dss_module_ip136_ip138 = models.CharField(blank=False, max_length=255, default="0")
    ip1111_poe_no_adapter = models.CharField(blank=False, max_length=255, default="0")
    ip1131_poe_gigabit_no_adapter = models.CharField(blank=False, max_length=255, default="0")
    ip1141_poe_no_adapter = models.CharField(blank=False, max_length=255, default="0")
    ip1141_ip131_ip132_adapter = models.CharField(blank=False, max_length=255, default="0")
    ip1181_ip136_ip138_adapter = models.CharField(blank=False, max_length=255, default="0")
    ip1211_w_adapter = models.CharField(blank=False, max_length=255, default="0")
    ip1211_poe_no_adapter = models.CharField(blank=False, max_length=255, default="0")
    ip1211_ip1211p_ip1111_ip1131_adapter = models.CharField(blank=False, max_length=255, default="0")
    ip131_poe_no_adapter = models.CharField(blank=False, max_length=255, default="0")
    ip132_gigabit_no_adapter = models.CharField(blank=False, max_length=255, default="0")
    ip136_poe_no_adapter = models.CharField(blank=False, max_length=255, default="0")
    ip138_poe_no_adapter = models.CharField(blank=False, max_length=255, default="0")
    karel_mobile = models.CharField(blank=False, max_length=255, default="0")
    vp128 = models.CharField(blank=False, max_length=255, default="0")
    yt510 = models.CharField(blank=False, max_length=255, default="0")
    yt520 = models.CharField(blank=False, max_length=255, default="0")
    yt530 = models.CharField(blank=False, max_length=255, default="0")
    state = models.CharField(null=True, max_length=255, default="Not Initialized ")


    def __str__(self):
        return self.pk


class Server(models.Model):
    class Meta:
        db_table = 'Server'
    action = models.CharField(blank=False, max_length=255, default="Stop")
    server_type = models.ForeignKey(ServerType, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE)
    status = models.CharField(blank=False, max_length=255, default="Active")
    idstr = models.CharField(blank=False, max_length=255, default="0")

    def __str__(self):
        return self.pk


class IpgServer(models.Model):
    class Meta:
        db_table = 'IpgServer'
    cpu = models.CharField(null=True, max_length=255)
    ram = models.CharField(null=True, max_length=255)
    disc = models.CharField(null=True, max_length=255)
    widea_address = models.CharField(null=True, max_length=255)
    local_ip = models.CharField(null=True, max_length=255)
    internal_ip = models.CharField(null=True, max_length=255)
    external_ip = models.CharField(null=True, max_length=255)
    server_name = models.CharField(null=True, max_length=255)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    state = models.IntegerField(null=True, default=1)
    fqdn = models.CharField(null=True, max_length=255)

    def __str__(self):
        return self.pk


class WebcmServer(models.Model):
    class Meta:
        db_table = 'WebcmServer'
    address = models.CharField(null=True, max_length=255)
    local_ip = models.CharField(null=True, max_length=255)
    internal_ip = models.CharField(null=True, max_length=255)
    server_name = models.CharField(null=True, max_length=255)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    state = models.IntegerField(null=True, default=1)
    fqdn = models.CharField(null=True, max_length=255)

    def __str__(self):
        return self.pk
