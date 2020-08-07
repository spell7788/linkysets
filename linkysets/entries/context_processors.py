from django.http import HttpRequest

from linkysets.users.models import User

from .forms import SearchForm
from .models import EntrySet


def search(request: HttpRequest) -> dict:
    return {"search_form": SearchForm()}


RATING_LIST_LIMIT = 5


def ratings(request: HttpRequest) -> dict:
    top_authors_qs = User.objects.num_entrysets().filter(num_sets__gt=0)
    top_authors_qs = top_authors_qs.order_by("-num_sets")[:RATING_LIST_LIMIT]
    recent_entrysets_qs = EntrySet.objects.order_by("-created")[:RATING_LIST_LIMIT]
    return {
        "top_authors": top_authors_qs,
        "recent_entrysets": recent_entrysets_qs,
    }
