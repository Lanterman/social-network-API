from rest_framework.pagination import PageNumberPagination


class PaginationPublished(PageNumberPagination):
    page_size = 5
