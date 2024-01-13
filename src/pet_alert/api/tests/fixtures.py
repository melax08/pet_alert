import shutil
import tempfile
from decimal import Decimal

from ads.models import AnimalType, Found, Lost
from ads.signals import post_save_advertisement
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.signals import post_save
from django.utils.crypto import get_random_string
from rest_framework.test import APIClient, APITestCase, override_settings
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

SMALL_GIF = (
    b"\x47\x49\x46\x38\x39\x61\x02\x00"
    b"\x01\x00\x80\x00\x00\x00\x00\x00"
    b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
    b"\x00\x00\x00\x2C\x00\x00\x00\x00"
    b"\x02\x00\x01\x00\x00\x02\x02\x0C"
    b"\x0A\x00\x3B"
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class BaseApiTestCaseWithFixtures(APITestCase):
    AUTH_TOKEN_PREFIX = "Bearer"
    DEFAULT_FORMAT = "json"
    FILES_FORMAT = "multipart"

    @staticmethod
    def generate_image():
        """Generates a small image with random name that can be sent in
        multipart POST requests."""
        uploaded = SimpleUploadedFile(
            name=f"{get_random_string(length=20)}.gif",
            content=SMALL_GIF,
            content_type="image/gif",
        )
        return uploaded

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        post_save.disconnect(post_save_advertisement, sender=Lost)
        post_save.disconnect(post_save_advertisement, sender=Found)
        cls.user_author = User.objects.create_user(email="author@example.com")
        cls.user_admin = User.objects.create_superuser(
            email="admin@example.com", password="123123"
        )
        cls.user_another = User.objects.create_user(email="another@example.com")
        cls.user_author_token = RefreshToken.for_user(cls.user_author).access_token
        cls.user_admin_token = RefreshToken.for_user(cls.user_admin).access_token
        cls.user_another_token = RefreshToken.for_user(cls.user_another).access_token

        cls.animal_type = AnimalType.objects.create(
            name="Animal",
            slug="animal",
            icon=cls.generate_image(),
            default_image=cls.generate_image(),
        )

        cls.lost_open_active_ad = Lost.objects.create(
            address="Санкт-Петербург, территория Петропавловская крепость, 3Д",
            latitude=Decimal(59),
            longitude=Decimal(30),
            image=cls.generate_image(),
            description="Test lost description",
            age="5 years",
            active=True,
            open=True,
            pet_name="Barsik",
            type=cls.animal_type,
            author=cls.user_author,
        )

        cls.found_open_active_ad = Found.objects.create(
            address="Санкт-Петербург, территория Петропавловская крепость, 3Д",
            latitude=Decimal(59),
            longitude=Decimal(30),
            image=cls.generate_image(),
            description="Test found description",
            age="6 years",
            active=True,
            open=True,
            condition="OK",
            type=cls.animal_type,
            author=cls.user_author,
        )

        cls.lost_closed_active_ad = Lost.objects.create(
            description="Test lost closed description",
            type=cls.animal_type,
            author=cls.user_author,
            image=cls.generate_image(),
            active=True,
            open=False,
        )

        cls.found_closed_active_ad = Found.objects.create(
            description="Test found closed description",
            type=cls.animal_type,
            author=cls.user_author,
            image=cls.generate_image(),
            condition="OK",
            active=True,
            open=False,
        )

        cls.lost_open_inactive_ad = Lost.objects.create(
            description="Test lost inactive description",
            type=cls.animal_type,
            author=cls.user_author,
            image=cls.generate_image(),
            active=False,
            open=True,
        )

        cls.found_open_inactive_ad = Found.objects.create(
            description="Test found inactive description",
            type=cls.animal_type,
            author=cls.user_author,
            condition="OK",
            image=cls.generate_image(),
            active=False,
            open=True,
        )

        cls.lost_closed_inactive_ad = Lost.objects.create(
            description="Test lost inactive closed description",
            type=cls.animal_type,
            author=cls.user_author,
            image=cls.generate_image(),
            active=False,
            open=False,
        )

        cls.found_closed_inactive_ad = Found.objects.create(
            description="Test found inactive closed description",
            type=cls.animal_type,
            author=cls.user_author,
            condition="OK",
            image=cls.generate_image(),
            active=False,
            open=False,
        )

    def setUp(self):
        self.guest_client = APIClient()
        self.author_client = APIClient()
        self.admin_client = APIClient()
        self.another_client = APIClient()

        self.author_client.credentials(
            HTTP_AUTHORIZATION=f"{self.AUTH_TOKEN_PREFIX} " f"{self.user_author_token}"
        )
        self.admin_client.credentials(
            HTTP_AUTHORIZATION=f"{self.AUTH_TOKEN_PREFIX} " f"{self.user_admin_token}"
        )
        self.another_client.credentials(
            HTTP_AUTHORIZATION=f"{self.AUTH_TOKEN_PREFIX} " f"{self.user_another_token}"
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
