from django.core.paginator import Paginator


class EnterprisePaginationMixin:
    """
    Conservative pagination defaults for large enterprise tables.

    Use with Django ListView:
        class ProductListView(EnterprisePaginationMixin, ListView):
            model = Product

    The mixin caps every requested page size at 1000 rows, even if a child
    class or query parameter asks for more.
    """

    paginate_by = 1000
    max_paginate_by = 1000
    page_size_query_param = "page_size"
    paginator_class = Paginator

    def get_paginate_by(self, queryset):
        requested = getattr(self, "paginate_by", self.max_paginate_by) or self.max_paginate_by

        if self.page_size_query_param:
            raw_page_size = self.request.GET.get(self.page_size_query_param)
            if raw_page_size:
                try:
                    requested = int(raw_page_size)
                except (TypeError, ValueError):
                    requested = self.paginate_by

        return min(max(int(requested), 1), self.max_paginate_by)

    def get_paginator(self, queryset, per_page, *args, **kwargs):
        per_page = min(max(int(per_page or self.paginate_by), 1), self.max_paginate_by)
        return self.paginator_class(queryset, per_page, *args, **kwargs)
