from rest_framework.response import Response
from rest_framework import serializers
from rbac import models

from django.forms import Form
from django.forms import fields
from django.forms import widgets
from django.core.exceptions import ValidationError



class MuneSerializer(serializers.Serializer):
    name = serializers.CharField()

class GroupSerializer(serializers.Serializer):
    name = serializers.CharField()


class PermissionSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.CharField()
    code = serializers.CharField()
    # menu_gp = serializers.CharField(source='menu_gp.name')
    group = serializers.CharField(source='group.name')

class PteamPermissionSerializer(serializers.Serializer):
    name = serializers.CharField()
    permissions = serializers.SerializerMethodField()

    def get_permissions(self,row):
        permissions_obj_li=row.permissions.all()
        ret=''
        for item in permissions_obj_li:
            ret+=str(item.name)+' '
        return ret

class UserSerializer(serializers.Serializer):
    name = serializers.CharField()
    username = serializers.CharField()
    password = serializers.CharField()
    token = serializers.CharField()
    pteamper = serializers.CharField(source='pteamper.name')
    pteam = serializers.CharField(source='pteam.name')

class PteamSerializer(serializers.Serializer):
    name = serializers.CharField()
    groupname = serializers.CharField()


class HostSerializer(serializers.Serializer):
    hostname = serializers.CharField()
    ecsname = serializers.CharField()
    eth1_network = serializers.CharField()
    eth0_network = serializers.CharField()
    createtime = serializers.CharField()
    expirytime = serializers.CharField()
    state = serializers.CharField(source='get_state_display')


