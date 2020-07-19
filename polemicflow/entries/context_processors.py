from django.http import HttpRequest

from .forms import SearchForm


def search(request: HttpRequest) -> dict:
    return {"search_form": SearchForm()}
