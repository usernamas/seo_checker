from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.template import loader
from django.http import Http404
from django.urls import reverse
from django.views import generic
from django.utils import timezone
from django.http import JsonResponse

import requests
import json

from bs4 import BeautifulSoup
from tkinter import *

from  .forms import SubmitUrlForm
from .models import Rule, Message
from .crawler import Crawler
from .scraper import Scraper

class IndexView(generic.ListView):
    template_name = 'checkup/index.html'
    context_object_name = 'latest_website_list'

    def get(self, request, *args, **kwargs):
        form = SubmitUrlForm()
        context = {
            'title': 'Submit URL',
            'form': form
        }
        return render(request, 'checkup/index.html', context)

    def post(self, request):
        form = SubmitUrlForm(request.POST)
        if(form.is_valid()):
            rules = Rule.objects.all()
            rules_and_messages = Rule.objects.all().prefetch_related('rule_name')
            final = {rule.name: dict(dict({el['status']: el for el in rule.rule_name.filter(name=rule).values()}, **{'priority': rule.priority}), **{'category': rule.category}) for rule in rules_and_messages}#{rule.name: dict({el['status']: el for el in rule.rule_name.filter(name=rule).values()}, **{'priority': rule.priority}) for rule in rules_and_messages}#{rule.name: {el['status']: dict(el, **{'priority': rule.priority}) for el in rule.rule_name.filter(name=rule).values()} for rule in rules_and_messages}
            crawler = Crawler(form.cleaned_data.get('url'), final)
            result = crawler.crawl(1)
            #crawler = Scraper(form.cleaned_data.get('url'))
            #result = crawler.scrap()
            context = {
                'url': form.cleaned_data.get('url'),
                'seo_result': result,
                'descriptions': rules,
                'desc': final
            }
        else:
            form = SubmitUrlForm(request.POST)
            context = {
                'title': 'Submit URL',
                'form': form
            }
            return render(request, 'checkup/index.html', context)
        return render(request, 'checkup/seo_check.html', context)
        #return render(request, 'checkup/scrap.html', context)

    def broken_links(request):
        if request.is_ajax():
            #print(request.GET['url'])
            rules = Rule.objects.all()
            rules_and_messages = Rule.objects.all().prefetch_related('rule_name')
            final = {rule.name: dict(dict({el['status']: el for el in rule.rule_name.filter(name=rule).values()}, **{'priority': rule.priority}), **{'category': rule.category}) for rule in rules_and_messages}
            message = "Yes, AJAX!"
            crawler = Crawler(request.GET['url'], final)
            broken_links = crawler.check_broken_links(True)
            #print(crawler)
            #print(broken_links)
            #print(crawler.modal_data)
            #return render(request, 'checkup/dynamic_result.html', {'content': {'Broken Links': broken_links}, 'modal_data': crawler.modal_data})
            #row = render(request, 'checkup/dynamic_result.html', {'content': {'Broken Links': broken_links}})
            return JsonResponse({'response': broken_links, 'modal_data': crawler.modal_data})
            return render(request, 'checkup/update.html', {'context': 'bandeles'})
        else:
            message = "Not Ajax"

        return HttpResponse(message)

    def render_template(request):
        print(request.GET.keys())
        print(request.GET.values())
        return render(request, 'checkup/dynamic_result.html', {'content': {'Broken Links': request.GET['data']}})

    def keywords(request):
        if request.is_ajax():
            rules = Rule.objects.all()
            rules_and_messages = Rule.objects.all().prefetch_related('rule_name')
            final = {rule.name: dict(dict({el['status']: el for el in rule.rule_name.filter(name=rule).values()}, **{'priority': rule.priority}), **{'category': rule.category}) for rule in rules_and_messages}

            message = "Yes, AJAX!"

            crawler = Crawler(request.GET['url'], final)
            crawler.format_keyword_data(crawler.keyword_results())

            return JsonResponse(crawler.modal_keywords)
            return render(request, 'checkup/update.html', {'context': 'bandeles'})
        else:
            message = "Not Ajax"

        return HttpResponse(message)

class SeoView(generic.ListView):
    template_name = 'checkup/seo_check.html'
    context_object_name = 'context'

    def get(self, request, url="", *args, **kwargs):
        form = SubmitUrlForm(request.POST)
        context = {
            'title': 'Submit URL',
            'form': form
        }
        return render(request, 'checkup/seo_check.html', context)

    def post(self, request):
        self.context = request
        return render(self.request, 'checkup/seo_check.html', self.context)

