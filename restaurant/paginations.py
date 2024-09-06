from rest_framework.pagination import PageNumberPagination


class MenuPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "size"
