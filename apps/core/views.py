from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_course'] = {
            'slug': 'espresso-basics',
            'title': 'The Art of Espresso',
            'category': 'Espresso',
            'progress': 65,
            'image': 'https://images.unsplash.com/photo-1510972527921-ce03766a1cf1?q=80&w=800&auto=format&fit=crop',
        }
        context['courses'] = [
            {'slug': 'v60-brewing', 'title': 'V60 Precision Brewing', 'description': 'Learn the chemistry of pour-over and how to manipulate variables for clarity.', 'category': 'Brewing', 'progress': 20, 'image': 'https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?q=80&w=800&auto=format&fit=crop'},
            {'slug': 'coffee-origin', 'title': 'Coffee Origin & Processing', 'description': 'Explore how terroir and processing methods affect the final cup profile.', 'category': 'Chemistry', 'progress': 0, 'image': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?q=80&w=800&auto=format&fit=crop'},
        ]
        context['achievements'] = [
            {'title': 'First Extraction', 'icon': '☕', 'date': 'Mar 12, 2024'},
            {'title': '7 Day Streak', 'icon': '🔥', 'date': 'Mar 19, 2024'},
            {'title': 'V60 Master', 'icon': '🌪️', 'date': 'Mar 22, 2024'},
        ]
        return context
