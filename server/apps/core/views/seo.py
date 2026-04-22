from django.http import HttpRequest, HttpResponse
from django.template.loader import render_to_string
from django.urls import reverse

from server.apps.ads.models import Advertisement


def robots_txt(request: HttpRequest) -> HttpResponse:
    context = {
        "sitemap_url": request.build_absolute_uri(reverse("sitemap")),
    }
    content = render_to_string("core/robots.txt", context)
    return HttpResponse(content, content_type="text/plain; charset=utf-8")


def sitemap_xml(request: HttpRequest) -> HttpResponse:
    static_urls = [
        {
            "location": request.build_absolute_uri(reverse("ads:index")),
            "changefreq": "daily",
            "priority": "1.0",
            "lastmod": None,
        },
        {
            "location": request.build_absolute_uri(reverse("ads:advertisement_list")),
            "changefreq": "hourly",
            "priority": "0.9",
            "lastmod": None,
        },
        {
            "location": request.build_absolute_uri(reverse("ads:advertisement_map")),
            "changefreq": "hourly",
            "priority": "0.8",
            "lastmod": None,
        },
    ]

    advertisement_urls = [
        {
            "location": request.build_absolute_uri(
                reverse("ads:advertisement_detail", kwargs={"ad_id": advertisement.id})
            ),
            "changefreq": "daily",
            "priority": "0.8",
            "lastmod": advertisement.updated_at,
        }
        for advertisement in Advertisement.objects.filter(active=True, open=True)
    ]

    content = render_to_string(
        "core/sitemap.xml",
        {"urls": [*static_urls, *advertisement_urls]},
    )
    return HttpResponse(content, content_type="application/xml; charset=utf-8")
