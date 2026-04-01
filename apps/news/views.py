"""News views."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from .models import NewsPost


class NewsListView(LoginRequiredMixin, ListView):
    model = NewsPost
    template_name = 'news/list.html'
    context_object_name = 'news'

    def get_queryset(self):
        return NewsPost.objects.all()


class NewsDetailView(LoginRequiredMixin, DetailView):
    model = NewsPost
    template_name = 'news/detail.html'
    context_object_name = 'news_post'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['news_title'] = self.object.localized_title
        context['news_date'] = self.object.published_at.strftime('%b %d, %Y')
        return context
