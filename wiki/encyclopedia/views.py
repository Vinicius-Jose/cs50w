from django.shortcuts import render, redirect

from . import util
from markdown2 import Markdown
from random import randint


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def entry(request, title: str):
    entry = util.get_entry(title)
    if entry:
        markdown = Markdown()
        entry = markdown.convert(entry)
    return render(
        request,
        "encyclopedia/wiki_page.html",
        {"title": title, "entry_content": entry},
    )


def edit(request, title: str):
    if request.method == "POST":
        save(request)
        title = request.POST.get("entry_title")
        return redirect("entry", title=title)
    entry = util.get_entry(title)
    return render(
        request,
        "encyclopedia/edit_create_entry.html",
        {"title": title, "entry_content": entry, "is_edit": True},
    )


def search(request):
    query = request.GET.get("q")
    entry = util.get_entry(query)
    if entry:
        return redirect("entry", title=query)
    found_entries = []
    for entry in util.list_entries():
        if query.lower() in entry.lower():
            found_entries.append(entry)
    return render(request, "encyclopedia/search.html", {"entries": found_entries})


def add(request):
    if request.method == "POST":
        title = request.POST.get("entry_title")
        if util.get_entry(title):
            return render(
                request,
                "encyclopedia/error_page_already_exists.html",
                {"title": title},
            )
        save(request)
        return redirect("entry", title=title)

    return render(
        request,
        "encyclopedia/edit_create_entry.html",
        {"title": "", "entry_content": "", "is_edit": False},
    )


def save(request):
    title = request.POST.get("entry_title")
    content = request.POST.get("entry_content")
    util.save_entry(title, content)


def random(request):
    list_entry = util.list_entries()
    title = list_entry[randint(0, len(list_entry) - 1)]
    return redirect("entry", title=title)
