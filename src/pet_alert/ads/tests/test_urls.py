from http import HTTPStatus

from django.urls import reverse

from .fixtures import BaseTestCaseWithFixtures


class AdsUrlsTests(BaseTestCaseWithFixtures):
    def test_ads_pages_unauthorized_user(self):
        """Guest user gets expected status codes on ads pages."""
        status_urls_map = {
            HTTPStatus.OK: [
                reverse("ads:index"),
                reverse("ads:add_found"),
                reverse("ads:add_lost"),
                reverse("ads:add_success"),
                reverse("ads:add_success_reg"),
                reverse("ads:lost"),
                reverse("ads:lost_map"),
                reverse(
                    "ads:lost_detail", kwargs={"ad_id": self.lost_open_active_ad.id}
                ),
                reverse(
                    "ads:found_detail", kwargs={"ad_id": self.found_open_active_ad.id}
                ),
                reverse("ads:found_map"),
            ],
            HTTPStatus.FOUND: [
                reverse("ads:profile"),
                reverse("ads:my_ads"),
                reverse("ads:my_ads_inactive"),
                reverse("ads:get_contact_information"),
                reverse("ads:close_ad"),
                reverse("ads:open_ad"),
                reverse("ads:get_dialog"),
                reverse("ads:create_dialog"),
                reverse("ads:messages"),
                reverse("ads:messages_chat", kwargs={"dialog_id": self.dialog.id}),
            ],
            HTTPStatus.NOT_FOUND: [
                "/aboba",
                reverse(
                    "ads:lost_detail", kwargs={"ad_id": self.lost_closed_active_ad.id}
                ),
                reverse(
                    "ads:found_detail", kwargs={"ad_id": self.found_closed_active_ad.id}
                ),
                reverse(
                    "ads:lost_detail", kwargs={"ad_id": self.lost_open_inactive_ad.id}
                ),
                reverse(
                    "ads:found_detail", kwargs={"ad_id": self.found_open_inactive_ad.id}
                ),
                reverse(
                    "ads:lost_detail", kwargs={"ad_id": self.lost_closed_inactive_ad.id}
                ),
                reverse(
                    "ads:found_detail",
                    kwargs={"ad_id": self.found_closed_inactive_ad.id},
                ),
            ],
        }

        for status_code, list_of_urls in status_urls_map.items():
            for url in list_of_urls:
                with self.subTest(url=url):
                    response = self.guest_client.get(url)
                    self.assertEqual(response.status_code, status_code)

    def test_ads_pages_authorized_user(self):
        """Authorized user gets expected status codes on ads pages."""
        status_urls_map = {
            HTTPStatus.OK: [
                reverse("ads:index"),
                reverse("ads:add_found"),
                reverse("ads:add_lost"),
                reverse("ads:add_success"),
                reverse("ads:add_success_reg"),
                reverse("ads:lost"),
                reverse("ads:lost_map"),
                reverse(
                    "ads:lost_detail", kwargs={"ad_id": self.lost_open_active_ad.id}
                ),
                reverse(
                    "ads:found_detail", kwargs={"ad_id": self.found_open_active_ad.id}
                ),
                reverse("ads:found_map"),
                reverse("ads:profile"),
                reverse("ads:my_ads"),
                reverse("ads:my_ads_inactive"),
                reverse(
                    "ads:lost_detail", kwargs={"ad_id": self.lost_closed_active_ad.id}
                ),
                reverse(
                    "ads:found_detail", kwargs={"ad_id": self.found_closed_active_ad.id}
                ),
                reverse(
                    "ads:lost_detail", kwargs={"ad_id": self.lost_open_inactive_ad.id}
                ),
                reverse(
                    "ads:found_detail", kwargs={"ad_id": self.found_open_inactive_ad.id}
                ),
                reverse(
                    "ads:lost_detail", kwargs={"ad_id": self.lost_closed_inactive_ad.id}
                ),
                reverse(
                    "ads:found_detail",
                    kwargs={"ad_id": self.found_closed_inactive_ad.id},
                ),
                reverse("ads:messages"),
                reverse("ads:messages_chat", kwargs={"dialog_id": self.dialog.id}),
            ],
            HTTPStatus.NOT_FOUND: ["/aboba"],
            HTTPStatus.METHOD_NOT_ALLOWED: [
                reverse("ads:get_contact_information"),
                reverse("ads:close_ad"),
                reverse("ads:open_ad"),
                reverse("ads:get_dialog"),
                reverse("ads:create_dialog"),
                reverse("ads:coords"),
            ],
        }

        for status_code, list_of_urls in status_urls_map.items():
            for url in list_of_urls:
                with self.subTest(url=url):
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, status_code)

    def test_urls_uses_correct_templates(self):
        """Ads urls uses correct templates."""
        url_template_map = {
            reverse("ads:index"): "ads/index.html",
            reverse("ads:add_found"): "ads/add_found.html",
            reverse("ads:add_lost"): "ads/add_lost.html",
            reverse("ads:add_success"): "ads/add_success.html",
            reverse("ads:add_success_reg"): "ads/add_success_reg.html",
            reverse("ads:lost"): "ads/lost.html",
            reverse("ads:lost_map"): "ads/map.html",
            reverse(
                "ads:lost_detail", kwargs={"ad_id": self.lost_open_active_ad.id}
            ): "ads/ad_detail.html",
            reverse(
                "ads:found_detail", kwargs={"ad_id": self.found_open_active_ad.id}
            ): "ads/ad_detail.html",
            reverse("ads:found_map"): "ads/map.html",
            reverse("ads:profile"): "ads/profile.html",
            reverse("ads:my_ads"): "ads/my_ads.html",
            reverse("ads:my_ads_inactive"): "ads/my_ads.html",
            reverse("ads:messages"): "ads/messages/messages_list.html",
            reverse(
                "ads:messages_chat", kwargs={"dialog_id": self.dialog.id}
            ): "ads/messages/messages_chat.html",
        }

        for url, template in url_template_map.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_not_found_page_correct_template(self):
        """Page with 404 error returns correct template."""
        response = self.guest_client.get("/non-exists-page")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")
