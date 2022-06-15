from django.contrib.auth import get_user_model

import factory

from sharing_configs.models import SharingConfigsConfig
from testapp.models import Theme


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f"user-{n}")
    password = factory.PostGenerationMethodCall("set_password", "password")

    class Meta:
        model = get_user_model()


class StaffUserFactory(UserFactory):
    is_staff = True


class SuperUserFactory(StaffUserFactory):
    is_superuser = True


class SharingConfigsConfigFactory(factory.django.DjangoModelFactory):
    api_endpoint = factory.Faker("url")
    api_key = "12345"
    label = factory.Faker("word")

    class Meta:
        model = SharingConfigsConfig


class ThemeFactory(factory.django.DjangoModelFactory):
    name = factory.Faker("word")
    primary = factory.Faker("word")
    secondary = factory.Faker("word")
    accent = factory.Faker("word")
    primary_fg = factory.Faker("word")

    class Meta:
        model = Theme
