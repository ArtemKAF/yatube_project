from django.core.paginator import Paginator


def create_pagination(objects, obj_on_page, page):
    return Paginator(objects, obj_on_page).get_page(page)


def get_author_name(author):
    if author.get_full_name():
        return author.get_full_name()
    return author.get_username()
