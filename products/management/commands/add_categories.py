from django.core.management.base import BaseCommand
from products.models import Category
from pathlib import Path
import json, os


class Command(BaseCommand):
    help = "Adds predefined categories and subcategories to the database"

    def handle(self, *args, **kwargs):
        categories_json = open(Path(__file__).with_name("categories.json"), "r").read()
        categories = json.loads(categories_json)

        def create_category(name, parent=None):
            category, _ = Category.objects.create(name=name, parent=parent)
            return category

        def add_categories(category_dict, parent=None):
            for name, subcategories in category_dict.items():
                category = create_category(name, parent)

                if isinstance(subcategories, dict):
                    add_categories(subcategories, category)
                elif isinstance(subcategories, list):
                    for subcategory in subcategories:
                        create_category(subcategory, category)

        add_categories(categories)
        self.stdout.write(
            self.style.SUCCESS("Successfully added categories and subcategories.")
        )
