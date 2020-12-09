from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    render
)

from core.models import (
    Store
)

from products.models import (
    Product,
    ContentItem
)

from core.decorators import (
    product_is_published,
    customer_has_access
)


@customer_has_access
@login_required
def course_home(request, product_slug):
    """

    :param request:
    :param product_slug:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    course = get_object_or_404(
        Product, store=store, product_type="course", slug=product_slug)

    return render(request, "courses/contents.html", {
        "store": store,
        "course": course
    })


@customer_has_access
@login_required
def course_content_item(request, product_slug, content_uuid):
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    course = get_object_or_404(
        Product, store=store, product_type="course", slug=product_slug)
    content_item = get_object_or_404(ContentItem, product=course, uuid=content_uuid)

    template_switcher = {
        "section": "courses/video.html",
        "text": "courses/text.html",
        "link": "courses/link.html",
        "file": "courses/file.html",
        "video": "courses/video.html"
    }

    return render(request, template_switcher[content_item.content_type], {
        "store": store,
        "course": course,
        "content_item": content_item
    })


def course_preview(request, product_slug):
    """

    :param request:
    :param product_slug:
    :return:
    """
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    course = get_object_or_404(
        Product, store=store, product_type="course", slug=product_slug)

    print(course.sections)

    return render(request, "courses/preview.html", {
        "store": store,
        "course": course,
        "preview": True
    })


def content_preview(request, product_slug, content_uuid):
    store = get_object_or_404(Store, store_slug=request.META["subdomain"])
    course = get_object_or_404(
        Product, store=store, product_type="course", slug=product_slug)
    content_item = get_object_or_404(ContentItem, product=course, uuid=content_uuid)

    template_switcher = {
        "section": "courses/video.html",
        "text": "courses/text.html",
        "link": "courses/link.html",
        "file": "courses/file.html",
        "video": "courses/video.html"
    }

    return render(request, template_switcher[content_item.content_type], {
        "store": store,
        "course": course,
        "content_item": content_item,
        "preview": True
    })