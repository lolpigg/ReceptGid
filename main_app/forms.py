from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import *


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']
        labels = {
            'username': 'Имя пользователя',
            'password': 'Пароль',
        }

class UploadSQLFileForm(forms.Form):
    sql_file = forms.FileField()
    labels = {
        'sql_file': 'Файл БД с расширением .sql'
    }
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'description', 'photo', 'date_of_birth')
        labels = {
            'username': 'Имя пользователя',
            'email': 'Электронная почта',
            'password1': 'Пароль',
            'password2': 'Подтверждение пароля',
            'description': 'Описание',
            'photo': 'Фото',
            'date_of_birth': 'Дата рождения'
        }


class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = [
            'title', 'header', 'cooking_time', 'description', 'photo',
            'servings', 'kcal_per_100g',
            'protein_per_100g', 'fat_per_100g',
            'carbohydrates_per_100g'
        ]
        labels = {
            'title': 'Название рецепта',
            'user': 'Пользователь',
            'header': 'Заголовок',
            'cooking_time': 'Время приготовления (мин)',
            'ingredients_list': 'Список ингредиентов',
            'description': 'Описание',
            'photo': 'Фото',
            'servings': 'Количество порций',
            'kcal_per_100g': 'Калории на 100 г',
            'protein_per_100g': 'Белки на 100 г',
            'fat_per_100g': 'Жиры на 100 г',
            'carbohydrates_per_100g': 'Углеводы на 100 г'
        }


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = ['name', 'kcal_per_100g',
                  'protein_per_100g', 'fat_per_100g',
                  'carbohydrates_per_100g']
        labels = {
            'name': 'Название ингредиента',
            'kcal_per_100g': 'Калории на 100 г',
            'protein_per_100g': 'Белки на 100 г',
            'fat_per_100g': 'Жиры на 100 г',
            'carbohydrates_per_100g': 'Углеводы на 100 г'
        }


class RecipeStepForm(forms.ModelForm):
    class Meta:
        model = RecipeStep
        fields = ['step_number', 'photo', 'description']
        labels = {
            'step_number': 'Номер шага',
            'photo': 'Фото шага',
            'description': 'Описание шага'
        }


class RecipeIngredientForm(forms.ModelForm):
    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity_in_grams']
        labels = {
            'ingredient': 'Ингредиент',
            'quantity_in_grams': 'Количество в граммах'
        }

class RecipeDeleteForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['deletion_reason']
        labels = {
            'deletion_reason': 'Причина удаления'
        }

class RecipeTagHiddenForm(forms.ModelForm):
    class Meta:
        model = RecipeTag
        fields = ['tag']
        labels = {
            'tag': 'Выберите тег'
        }

class UserChangeProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['description', 'photo']
        labels = {
            'description': 'Описание',
            'photo': 'Фото пользователя',

        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'description']
        labels = {
            'name': 'Название тега',
            'description': 'Описание тега'
        }

class UserRoleChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['role']
        widgets = {
            'role': forms.Select(choices=[('USER', 'USER'), ('ADMIN', 'ADMIN'), ('MODER', 'MODER')]),
        }
        labels = {
            'role': 'Роль пользователя'
        }

class UserDeletionForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['deletion_reason']
        labels = {
            'deletion_reason': 'Причина удаления'
        }


class RecipeTagForm(forms.ModelForm):
    class Meta:
        model = RecipeTag
        fields = ['tag', 'recipe']
        labels = {
            'tag': 'Тег',
            'recipe': 'Рецепт'
        }


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['sender', 'recipient', 'text']
        labels = {
            'sender': 'Отправитель',
            'recipient': 'Получатель',
            'text': 'Сообщение'
        }


class FavoriteRecipeForm(forms.ModelForm):
    class Meta:
        model = FavoriteRecipe
        fields = ['recipe', 'user']
        labels = {
            'recipe': 'Рецепт',
            'user': 'Пользователь'
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['user', 'rating', 'title', 'text']
        labels = {
            'user': 'Пользователь',
            'rating': 'Оценка',
            'title': 'Заголовок отзыва',
            'text': 'Текст отзыва'
        }


class FriendForm(forms.ModelForm):
    class Meta:
        model = Friend
        fields = ['requester', 'accepter']
        labels = {
            'requester': "Запрашивающий",
            "accepter": "Принимающий"
        }


class RecipeReviewForm(forms.ModelForm):
    class Meta:
        model = RecipeReview
        fields = ['review', 'recipe']
        labels = {
            "review": "Отзыв",
            "recipe": "Рецепт"
        }
