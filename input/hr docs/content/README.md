# Dim Kava — Content Files
# How to use these files in the Django project

## What's in this folder

| File | What it is | Used in |
|---|---|---|
| `onboarding_training_plan.yaml` | Full 3-month onboarding programme: modules, steps, content | `apps/onboarding/` — seed data for modules and steps |
| `onboarding_quizzes.yaml` | All 9 quizzes (3 days → 3 months + behavioural) with all questions | `apps/courses/` — quiz lessons inside onboarding modules |
| `sops_and_standards.yaml` | Daily/weekly/monthly checklists, service standards, job description, qualification levels | `apps/knowledge_base/` — published articles |
| `initial_data.json` | Django fixture — KB sections, roles, badges, missions, onboarding program | `fixtures/initial_data.json` — loaded with `loaddata` |

---

## How to load into the project

### 1. Django fixture (quick start)
```bash
python manage.py loaddata fixtures/initial_data.json
```
This creates:
- 4 knowledge base sections
- 6 article stubs (content loaded separately)
- 1 department + 1 role
- 1 onboarding programme
- 7 gamification badges
- 3 gamification missions

### 2. Article content
The articles in `initial_data.json` have stub content.
To load the real content, create a management command:

```python
# apps/knowledge_base/management/commands/load_article_content.py
import yaml
from django.core.management.base import BaseCommand
from apps.knowledge_base.models import Article

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('content/sops_and_standards.yaml') as f:
            data = yaml.safe_load(f)
        for article_data in data['articles']:
            Article.objects.filter(slug=article_data['slug']).update(
                content=article_data['content']
            )
        self.stdout.write("Article content loaded.")
```

### 3. Onboarding modules and steps
Create a management command to load `onboarding_training_plan.yaml`:

```python
# apps/onboarding/management/commands/load_onboarding.py
import yaml
from django.core.management.base import BaseCommand
from apps.onboarding.models import OnboardingProgram, OnboardingModule, OnboardingStep

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('content/onboarding_training_plan.yaml') as f:
            data = yaml.safe_load(f)

        program, _ = OnboardingProgram.objects.get_or_create(
            slug=data['program']['slug'],
            defaults={
                'title': data['program']['title'],
                'description': data['program']['description'],
                'estimated_days': data['program']['estimated_days'],
            }
        )

        for module_data in data['modules']:
            module, _ = OnboardingModule.objects.get_or_create(
                slug=module_data['slug'],
                program=program,
                defaults={
                    'title': module_data['title'],
                    'order': module_data['order'],
                    'estimated_minutes': module_data['estimated_minutes'],
                    'description': module_data['description'],
                }
            )
            for step_data in module_data.get('steps', []):
                OnboardingStep.objects.get_or_create(
                    module=module,
                    order=step_data['order'],
                    defaults={
                        'title': step_data['title'],
                        'content': step_data['content'],
                    }
                )

        self.stdout.write(f"Loaded {len(data['modules'])} modules.")
```

### 4. Quizzes
Load `onboarding_quizzes.yaml` similarly — create Lesson objects with `lesson_type='quiz'`
and TestQuestion objects for each question.

Questions with `type: open` → store as text input (employee writes an answer,
manager reviews manually or it triggers a self-assessment flow).

Questions with `type: rating` → render as a star/number rating widget.

---

## Quiz passing scores

| Quiz | Passing Score | Notes |
|---|---|---|
| Day 3 | 70% | First check, low pressure |
| Week 1 | 70% | Coffee and drink knowledge |
| Week 2 | 70% | Milk, Caotina, Delonghi |
| Week 3 | 70% | Specialty, Blaser range |
| Month 1 | 75% | Full operations |
| Shop Seller | 80% | Must pass before solo work |
| Month 2 | 75% | Equipment expertise |
| Month 3 | 80% | Expert + mentoring |
| Behavioural | No score | HR review only |

---

## Gamification mapping

| Event | Points | Badge |
|---|---|---|
| Complete any onboarding lesson | +10 | — |
| Pass any quiz ≥ 70% | +20 | — |
| Pass any quiz ≥ 90% | +20 + badge | QUIZ_MASTER |
| Complete Day 1 module | +30 | ONBOARDING_DAY1 |
| Pass Week 1 quiz | +30 | QUIZ_WEEK1_PASSED |
| Pass Shop Seller quiz | +50 | SHOP_SELLER_CERTIFIED |
| Complete Month 1 | +200 | ONBOARDING_MONTH1 |
| Complete full 3-month onboarding | +500 | ONBOARDING_COMPLETE |
| Coffee specialist quiz | — | COFFEE_SPECIALIST |

---

## Content language (EN/KA/RU)

Default language is **English (`en`)**.

Seed loaders now support multilingual keys for content models:
- flat keys: `title_en`, `title_ka`, `title_ru`
- and the same for `description_*`, `content_*`
- for quizzes: `text_en/text_ka/text_ru`, `options_en/options_ka/options_ru`

Backward compatibility:
- old single-language keys (`title`, `description`, `content`, `text`, `options`) still work;
- they are treated as English source values.

Auto-draft mode:
- loaders support `--auto-translate-draft` to populate missing `ka/ru` fields with
  draft placeholders from EN.
- HR should review and replace draft values before publishing.
