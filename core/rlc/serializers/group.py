from rest_framework import serializers

from core.models import Group


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = "__all__"


class GroupCreateSerializer(GroupSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context["request"]
        attrs["from_rlc"] = request.user.rlc
        return attrs


class GroupNameSerializer(GroupSerializer):
    class Meta:
        model = Group
        fields = ["name", "id"]