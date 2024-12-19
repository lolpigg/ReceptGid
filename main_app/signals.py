from django.db import models, transaction
from .models import *
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=RecipeIngredient)
def update_recipe_nutrition(sender, instance, created, **kwargs):
    if created:
        recipe = instance.recipe
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)

        total_kcal = 0
        total_protein = 0
        total_fat = 0
        total_carbohydrates = 0
        total_quantity = 0

        for recipe_ingredient in ingredients:
            ingredient = recipe_ingredient.ingredient
            quantity = recipe_ingredient.quantity_in_grams

            total_kcal += ingredient.kcal_per_100g * (quantity / 100)
            total_protein += ingredient.protein_per_100g * (quantity / 100)
            total_fat += ingredient.fat_per_100g * (quantity / 100)
            total_carbohydrates += ingredient.carbohydrates_per_100g * (quantity / 100)
            total_quantity += quantity

        if total_quantity > 0:
            recipe.kcal_per_100g = round(total_kcal / (total_quantity / 100), 1)
            recipe.protein_per_100g = round(total_protein / (total_quantity / 100), 1)
            recipe.fat_per_100g = round(total_fat / (total_quantity / 100), 1)
            recipe.carbohydrates_per_100g = round(total_carbohydrates / (total_quantity / 100), 1)

            # Сохраняем обновленный рецепт
            recipe.save()
