from rest_framework import serializers
from .models import *

class AdvertiseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertise
        fields = ["name","icon"]



class ActiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Active
        fields = "__all__"