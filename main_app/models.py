from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='user_photos/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    rating = models.FloatField(default=0.0)
    deletion_reason = models.TextField(blank=True, null=True)
    role = models.TextField(default="USER")
    def __str__(self):
        return self.username

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    header = models.CharField(max_length=255)
    cooking_time = models.PositiveIntegerField()
    description = models.TextField()
    photo = models.ImageField(upload_to='recipe_photos/')
    rating = models.FloatField(default=0.0)
    deletion_reason = models.TextField(default=None, blank=True, null=True)
    servings = models.PositiveIntegerField()
    is_verified = models.BooleanField(default=False)
    publication_date = models.DateTimeField(auto_now_add=True)
    kcal_per_100g = models.PositiveIntegerField()
    protein_per_100g = models.FloatField()
    fat_per_100g = models.FloatField()
    carbohydrates_per_100g = models.FloatField()
    def __str__(self):
        return self.title

class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    kcal_per_100g = models.PositiveIntegerField()
    protein_per_100g = models.FloatField()
    fat_per_100g = models.FloatField()
    carbohydrates_per_100g = models.FloatField()
    def __str__(self):
        return self.name

class RecipeStep(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    step_number = models.PositiveIntegerField()
    photo = models.ImageField(upload_to='recipe_steps_photos/', null=True, blank=True)
    description = models.TextField()

class RecipeIngredient(models.Model):
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    quantity_in_grams = models.PositiveIntegerField()

class Tag(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    def __str__(self):
        return self.name

class RecipeTag(models.Model):
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class FavoriteRecipe(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # Оценка от 1 до 5
    title = models.CharField(max_length=255)
    text = models.TextField()
    date_written = models.DateTimeField(auto_now_add=True)
    deletion_reason = models.TextField(default='', null=True, blank=True)
    def __str__(self):
        return self.title

class Friend(models.Model):
    requester = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    accepter = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)

class RecipeReview(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
