from django.contrib import admin
from .models import User, Recipe, Ingredient, RecipeStep, RecipeIngredient, Tag, RecipeTag, Message, FavoriteRecipe, Review, Friend, RecipeReview

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'date_of_birth', 'rating', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'cooking_time', 'is_verified', 'publication_date')
    search_fields = ('title', 'user__username')
    list_filter = ('is_verified',)
    ordering = ('-publication_date',)

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'kcal_per_100g')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(RecipeStep)
class RecipeStepAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'step_number')
    search_fields = ('recipe__title',)
    ordering = ('recipe', 'step_number')

@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'quantity_in_grams')
    search_fields = ('recipe__title', 'ingredient__name')
    ordering = ('recipe',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(RecipeTag)
class RecipeTagAdmin(admin.ModelAdmin):
    list_display = ('tag', 'recipe')
    search_fields = ('tag__name', 'recipe__title')
    ordering = ('tag', 'recipe')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'timestamp')
    search_fields = ('sender__username', 'recipient__username')
    ordering = ('-timestamp',)

@admin.register(FavoriteRecipe)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__title')
    ordering = ('user',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'rating', 'title', 'date_written')
    search_fields = ('user__username', 'title')
    ordering = ('-date_written',)

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('requester', 'accepter')
    search_fields = ('requester__username', 'accepter__username')
    ordering = ('requester',)

@admin.register(RecipeReview)
class RecipeReviewAdmin(admin.ModelAdmin):
    list_display = ('review', 'recipe')
    search_fields = ('review__title', 'recipe__title')
    ordering = ('review',)
