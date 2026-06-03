from django.core.paginator import Paginator


def paginate_queryset(request, queryset, per_page):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def get_query_prefix(request):
    params = request.GET.copy()
    params.pop("page", None)
    encoded_params = params.urlencode()
    return f"{encoded_params}&" if encoded_params else ""
