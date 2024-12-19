import csv
import os
import sqlite3
import datetime

from django.conf import settings
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views import View
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from main_app.forms import *


def user_or_mod(request):
    try:
        return request.user.role == "USER" or request.user.role == "MODER"
    except:
        return False



def adm(request):
    try:
        bool = request.user.role == "ADMIN"
        return bool
    except:
        return False


def mod(request):
    try:
        bool = request.user.role == "MODER"
        return bool
    except:
        return False


from django.db.models.signals import post_save
from django.dispatch import receiver




@login_required(login_url='login')
def edit_profile(request):
    user = request.user  # Получаем текущего пользователя
    if request.method == 'POST':
        form = UserChangeProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()  # Сохраняем изменения в профиле
            return redirect(reverse("user_profile", args=[request.user.id]))  # Перенаправляем на страницу профиля или другую страницу
    else:
        form = UserChangeProfileForm(instance=user)  # Заполняем форму данными пользователя

    return render(request, 'user/edit_profile.html', {'form': form, 'user': user})


@login_required(login_url='login')
def statistics(request):
    if adm(request):
        # Получение данных о пользователях по ролям
        roles_count = User.objects.values('role').annotate(count=models.Count('id'))
        roles = [role['role'] for role in roles_count]
        counts = [role['count'] for role in roles_count]

        # Создание графика для ролей
        plt.figure(figsize=(10, 5))
        plt.bar(roles, counts, color='skyblue')

        # Настройка фона и текста
        plt.gca().set_facecolor('black')  # Черный фон для графика
        plt.title('Количество пользователей по ролям', color='blue')  # Синий текст заголовка
        plt.xlabel('Роли', color='blue')  # Синий текст оси X
        plt.ylabel('Количество пользователей', color='blue')  # Синий текст оси Y
        plt.tick_params(axis='both', colors='blue')  # Синий текст меток осей

        # Сохранение графика в буфер
        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor='black')  # Указание черного фона при сохранении
        plt.close()
        buf.seek(0)
        graph_roles = base64.b64encode(buf.read()).decode('utf-8')

        # Получение данных о рецептах по пользователям
        recipes_count = Recipe.objects.values('user__username').annotate(count=models.Count('id'))
        usernames = [recipe['user__username'] for recipe in recipes_count]
        recipe_counts = [recipe['count'] for recipe in recipes_count]

        # Создание графика для рецептов
        plt.figure(figsize=(10, 5))
        plt.bar(usernames, recipe_counts, color='lightgreen')

        # Настройка фона и текста
        plt.gca().set_facecolor('black')  # Черный фон для графика
        plt.title('Количество опубликованных рецептов у пользователей', color='blue')  # Синий текст заголовка
        plt.xlabel('Пользователи', color='blue')  # Синий текст оси X
        plt.ylabel('Количество рецептов', color='blue')  # Синий текст оси Y
        plt.tick_params(axis='both', colors='blue')  # Синий текст меток осей

        # Сохранение графика в буфер
        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor='black')  # Указание черного фона при сохранении
        plt.close()
        buf.seek(0)
        graph_recipes = base64.b64encode(buf.read()).decode('utf-8')

        # Передача графиков в контекст для отображения на странице
        context = {
            'graph_roles': graph_roles,
            'graph_recipes': graph_recipes,
        }

        return render(request, 'admin/statistics.html', context)
    else:
        return redirect('page_404')


@login_required(login_url='login')
def favorite_recipe_list(request):
    if user_or_mod(request):
        current_user = request.user
        favorite_recipes = FavoriteRecipe.objects.filter(user=current_user).select_related('recipe')
        recipes = [favorite.recipe for favorite in favorite_recipes if
                   favorite.recipe.is_verified and favorite.recipe.deletion_reason == '']
        context = {'recipes': recipes}
        return render(request, 'user/favorite_recipes.html', context)
    else:
        return redirect('page_404')

@login_required(login_url='login')
def not_verified_recipes_list(request):
    if mod(request):
        recipes = Recipe.objects.filter(
            is_verified=False
        ).filter(
            Q(deletion_reason='') | Q(deletion_reason__isnull=True)
        ).order_by('-publication_date')
        context = {'recipes': recipes}
        return render(request, 'user/not_verified_recipes.html', context)
    else:
        return redirect('page_404')

@login_required(login_url='login')
def recipe_steps_list(request, recipe_id):
    if user_or_mod(request):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        steps = RecipeStep.objects.filter(recipe=recipe).order_by('step_number')
        context = {
            'recipe': recipe,
            'steps': steps
        }
        return render(request, 'user/recipe_steps.html', context)

@login_required(login_url='login')
def add_recipe_step(request, recipe_id):
    if user_or_mod(request):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if recipe.user.id != request.user.id or recipe.is_verified or recipe.deletion_reason != None and recipe.deletion_reason != '':
            redirect('page_404')
        if request.method == 'POST':
            form = RecipeStepForm(request.POST, request.FILES)
            if form.is_valid():
                recipe_step = form.save(commit=False)
                recipe_step.recipe = recipe
                recipe_step.save()
                return redirect('add_recipe_step', recipe_id=recipe.id)
        else:
            form = RecipeStepForm()

        return render(request, 'user/add_recipe_step.html', {'form': form, 'recipe': recipe})
    else:
        return redirect('page_404')

@login_required(login_url="login")
def add_or_delete_friend(request, id):
    if user_or_mod(request):
        try:
            accepter = User.objects.get(id=id)
            friend = Friend.objects.filter(requester=request.user, accepter=accepter)
            if friend.exists():
                friend.delete()
                return redirect(reverse("user_profile", args=[id]))
            Friend.objects.create(requester=request.user, accepter=accepter)
            return redirect(reverse("user_profile", args=[id]))
        except User.DoesNotExist:
            return redirect('page_404')
    else:
        return redirect('page_404')

@login_required(login_url="login")
def add_or_delete_favorite_recipe(request, id):
    if user_or_mod(request):
        try:
            recipe = Recipe.objects.get(id=id)
            favorite = FavoriteRecipe.objects.filter(recipe=recipe, user=request.user)
            if favorite.exists():
                favorite.delete()
                return redirect(reverse("recipe_detail", args=[id]))
            FavoriteRecipe.objects.create(recipe=recipe, user=request.user)
            return redirect(reverse("recipe_detail", args=[id]))
        except Recipe.DoesNotExist:
            return redirect('page_404')
    else:
        return redirect('page_404')


@login_required(login_url='login')
def accept_recipe(request, recipe_id, is_accept):
    if mod(request):
        recipe_delete_form = RecipeDeleteForm()
        if request.method == 'GET':
            is_accept = is_accept.lower() == 'true'
            recipe = get_object_or_404(Recipe, id=recipe_id)
            if (is_accept):
                recipe.is_verified = True
                recipe.deletion_reason = ''
                recipe.save()
                return redirect(reverse("recipe_detail", args=[recipe_id]))
            else:
                context = {
                    'recipe': recipe,
                    'form': recipe_delete_form
                }
                return render(request, 'user/delete_recipe.html', context)
        else:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            recipe_delete_form = RecipeDeleteForm(request.POST)
            if recipe_delete_form.is_valid():
                # Обработка успешной валидации
                recipe.deletion_reason = recipe_delete_form.cleaned_data['deletion_reason']
                recipe.save()
                return redirect(reverse("home"))
            else:
                print(recipe_delete_form.errors)  # Вывод ошибок
    else:
        return redirect('page_404')

@login_required(login_url="login")
def manage_ingredients(request, recipe_id):
    if user_or_mod(request):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if recipe.user.id != request.user.id or recipe.is_verified or recipe.deletion_reason != None and recipe.deletion_reason != '':
            redirect('page_404')
        if request.method == 'POST':
            # Обработка формы для создания нового ингредиента
            ingredient_form = IngredientForm(request.POST)
            recipe_ingredient_form = RecipeIngredientForm(request.POST)

            if ingredient_form.is_valid():
                ingredient_form.save()
                return redirect(reverse("manage_ingredients", args=[recipe_id]))
                # После создания нового ингредиента можно добавить его к рецепту
            if recipe_ingredient_form.is_valid():
                recipe_ingredient = recipe_ingredient_form.save(commit=False)
                recipe_ingredient.recipe = recipe
                recipe_ingredient.save()
                return redirect(reverse("manage_ingredients", args=[recipe_id]))

        else:
            ingredient_form = IngredientForm()
            recipe_ingredient_form = RecipeIngredientForm()

        context = {
            'recipe': recipe,
            'ingredient_form': ingredient_form,
            'recipe_ingredient_form': recipe_ingredient_form,
        }
        return render(request, 'user/manage_ingredients.html', context)

@login_required(login_url="login")
def manage_tags(request, recipe_id):
    if user_or_mod(request):
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if recipe.user.id != request.user.id or recipe.is_verified or recipe.deletion_reason != None and recipe.deletion_reason != '':
            redirect('page_404')
        if request.method == 'POST':
            recipe_tag_form = RecipeTagHiddenForm(request.POST)
            if recipe_tag_form.is_valid():
                recipe_tag = recipe_tag_form.save(commit=False)
                recipe_tag.recipe = recipe
                recipe_tag.save()
                return redirect(reverse("manage_tags", args=[recipe_id]))

        else:
            recipe_tag_form = RecipeTagHiddenForm()

        context = {
            'recipe': recipe,
            'recipe_tag_form': recipe_tag_form,
        }
        return render(request, 'user/manage_tags.html', context)

@login_required(login_url='login')
def user_relationships(request, user_id, is_subscriber):
    if (user_or_mod(request)):
        is_subscriber = is_subscriber.lower() == 'true'
        user = get_object_or_404(User, id=user_id)
        if is_subscriber:  # Если true, получаем подписчиков
            followers = Friend.objects.filter(accepter=user)
            context = {
                'user': user,
                'followers': followers,
            }
            return render(request, 'user/followers_list.html', context)
        else:  # Если false, получаем подписки
            following = Friend.objects.filter(requester=user).select_related('accepter')
            context = {
                'user': user,
                'following': following,
            }
            return render(request, 'user/following_list.html', context)
    else:
        redirect('page_404')

class BackupSQLView(View):
    def get(self, request):
        if adm(request):
            response = HttpResponse(content_type='application/sql')
            response['Content-Disposition'] = 'attachment; filename=backup.sql'

            with connection.cursor() as cursor:
                # Получаем список всех таблиц в базе данных SQLite
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()

                for table in tables:
                    table_name = table[0]
                    if table_name != "sqlite_sequence":
                        # Получаем SQL команду создания таблицы
                        cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table_name}';")
                        create_table_sql = cursor.fetchone()[0]
                        response.write(f"{create_table_sql};")

                        # Получаем данные из таблицы
                        cursor.execute(f"SELECT * FROM {table_name};")
                        rows = cursor.fetchall()
                        columns = [column[0] for column in cursor.description]

                        for row in rows:
                            formatted_values = []
                            for value in row:
                                if isinstance(value, datetime.datetime):
                                    # Форматируем datetime в стандартный вид
                                    formatted_value = value.strftime('%Y-%m-%d %H:%M:%S')
                                    formatted_values.append(f"'{formatted_value}'")
                                elif isinstance(value, str):
                                    # Экранируем строки
                                    old = "'"
                                    new = "''"
                                    formatted_values.append(f"'{value.replace(old, new)}'")
                                else:
                                    # Для других типов (int, float и т.д.) просто добавляем значение
                                    formatted_values.append(str(value))

                            sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(formatted_values)});"
                            response.write(sql)
            return response
        else:
            return redirect('page_404')

class BackupCSVView(View):
    def get(self, request):
        if adm(request):
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=backup.csv'

            writer = csv.writer(response)
            writer.writerow(['Model', 'ID', 'Data'])  # Заголовки

            # Сохраняем данные пользователей
            for user in User.objects.all():
                writer.writerow(['User', user.id, user.username])
                writer.writerow(['User Description', user.id, user.description])
                writer.writerow(['User Date of Birth', user.id, user.date_of_birth])
                writer.writerow(['User Rating', user.id, user.rating])
                writer.writerow(['User Role', user.id, user.role])

            # Сохраняем данные рецептов
            for recipe in Recipe.objects.all():
                writer.writerow(['Recipe', recipe.id, recipe.title])
                writer.writerow(['Recipe Header', recipe.id, recipe.header])
                writer.writerow(['Recipe Cooking Time', recipe.id, recipe.cooking_time])
                writer.writerow(['Recipe Description', recipe.id, recipe.description])
                writer.writerow(['Recipe Rating', recipe.id, recipe.rating])
                writer.writerow(['Recipe Servings', recipe.id, recipe.servings])
                writer.writerow(['Recipe Is Verified', recipe.id, recipe.is_verified])
                writer.writerow(['Recipe Publication Date', recipe.id, recipe.publication_date])
                writer.writerow(['Recipe kcal per 100g', recipe.id, recipe.kcal_per_100g])
                writer.writerow(['Recipe Protein per 100g', recipe.id, recipe.protein_per_100g])
                writer.writerow(['Recipe Fat per 100g', recipe.id, recipe.fat_per_100g])
                writer.writerow(['Recipe Carbohydrates per 100g', recipe.id, recipe.carbohydrates_per_100g])

            for ingredient in Ingredient.objects.all():
                writer.writerow(['Ingredient', ingredient.id, ingredient.name])
                writer.writerow(['Ingredient kcal per 100g', ingredient.id, ingredient.kcal_per_100g])
                writer.writerow(['Ingredient Protein per 100g', ingredient.id, ingredient.protein_per_100g])
                writer.writerow(['Ingredient Fat per 100g', ingredient.id, ingredient.fat_per_100g])
                writer.writerow(['Ingredient Carbohydrates per 100g', ingredient.id, ingredient.carbohydrates_per_100g])

            # Сохраняем данные шагов рецепта
            for step in RecipeStep.objects.all():
                writer.writerow(['Recipe Step', step.id, step.description])
                writer.writerow(['Step Number', step.id, step.step_number])

            # Сохраняем данные ингредиентов рецепта
            for recipe_ingredient in RecipeIngredient.objects.all():
                writer.writerow(['Recipe Ingredient', recipe_ingredient.id, f'Recipe: {recipe_ingredient.recipe.id}, Ingredient: {recipe_ingredient.ingredient.id}, Quantity: {recipe_ingredient.quantity_in_grams}'])

            # Сохраняем данные тегов
            for tag in Tag.objects.all():
                writer.writerow(['Tag', tag.id, tag.name])
                writer.writerow(['Tag Description', tag.id, tag.description])

            # Сохраняем данные тегов рецептов
            for recipe_tag in RecipeTag.objects.all():
                writer.writerow(['Recipe Tag', recipe_tag.id, f'Tag: {recipe_tag.tag.id}, Recipe: {recipe_tag.recipe.id}'])

            # Сохраняем сообщения
            for message in Message.objects.all():
                writer.writerow(['Message', message.id,
                                 f'Sender: {message.sender.id}, Recipient: {message.recipient.id}, Text: {message.text}, Timestamp: {message.timestamp}'])

                # Сохраняем избранные рецепты
            for favorite_recipe in FavoriteRecipe.objects.all():
                writer.writerow(['Favorite Recipe', favorite_recipe.id,
                                 f'Recipe: {favorite_recipe.recipe.id}, User: {favorite_recipe.user.id}'])

                # Сохраняем отзывы
            for review in Review.objects.all():
                writer.writerow(['Review', review.id,
                                 f'User: {review.user.id}, Rating: {review.rating}, Title: {review.title}, Text: {review.text}, Date Written: {review.date_written}'])

                # Сохраняем друзей
            for friend in Friend.objects.all():
                writer.writerow(
                    ['Friendship', friend.id, f'Requester: {friend.requester.id}, Accepter: {friend.accepter.id}'])

            for recipe_review in RecipeReview.objects.all():
                writer.writerow(
                    ['Recipe Review', recipe_review.id,
                     f'Recipe: {recipe_review.recipe.id}', f'Review: {recipe_review.review.id}']
                )
            return response
        else:
            return redirect('page_404')

@login_required(login_url='login')
def upload_sql_file(request):
    if adm(request):
        if request.method == 'POST':
            form = UploadSQLFileForm(request.POST, request.FILES)
            if form.is_valid():
                sql_file = request.FILES['sql_file']
                with open('temp.sql', 'wb+') as temp_file:
                    for chunk in sql_file.chunks():
                        temp_file.write(chunk)
                db_path = settings.DATABASES['default']['NAME']
                connection.close()
                if os.path.exists(db_path):
                    os.remove(db_path)
                conn = sqlite3.connect(settings.DATABASES['default']['NAME'])
                cursor = conn.cursor()
                with open('temp.sql', 'r') as file:
                    sql_script = file.read()
                    cursor.executescript(sql_script)
                conn.commit()
                conn.close()
                os.remove('temp.sql')
                return render(request, 'sql/upload_success.html')
    else:
        return redirect('page_404')


@login_required(login_url='login')
def admin_home(request):
    if adm(request):
        tags = Tag.objects.all()
        users = User.objects.all()
        sql_form = UploadSQLFileForm()
        return render(request, 'admin/home.html', {'tags': tags, 'users': users, 'sql_form': sql_form})
    else:
        return redirect('page_404')

@login_required(login_url='login')
def add_tag(request):
    if adm(request):
        if request.method == 'POST':
            form = TagForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('admin_home')
        else:
            form = TagForm()
        return render(request, 'admin/add_tag.html', {'form': form})
    else:
        return redirect('page_404')

@login_required(login_url='login')
def delete_user(request, user_id):
    if adm(request) and user_id != request.user.id:
        user = get_object_or_404(User, id=user_id)
        if request.method == 'POST':
            form = UserDeletionForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect('admin_home')
        else:
            form = UserDeletionForm(instance=user)
        return render(request, 'admin/delete_user.html', {'form': form, 'user': user})
    else:
        return redirect('page_404')

@login_required(login_url='login')
def undelete_user(request, user_id):
    if adm(request) and user_id != request.user.id:
        user = get_object_or_404(User, id=user_id)
        user.deletion_reason = ''
        user.save()
        return redirect('admin_home')
    else:
        return redirect('page_404')

@login_required(login_url='login')
def change_user_role(request, user_id):
    if adm(request) and user_id != request.user.id:
        user = get_object_or_404(User, id=user_id)
        if request.method == 'POST':
            form = UserRoleChangeForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect('admin_home')
        else:
            form = UserRoleChangeForm(instance=user)
        return render(request, 'admin/change_user_role.html', {'form': form, 'user': user})
    else:
        return redirect('page_404')


def user_register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'auth/register.html', {'form': form})


@login_required(login_url='login')
def home(request):
    if user_or_mod(request):
        moder = False
        if mod(request):
            moder = True
        recipes = Recipe.objects.filter(is_verified=True, deletion_reason='').order_by('-publication_date')
        context = {'recipes': recipes, 'moder': moder}
        return render(request, 'home.html', context)
    else:
        if adm(request):
            return redirect('admin_home')
        return redirect('page_404')




def custom_404_view(request):
    return render(request, '404.html')



@login_required(login_url='login')
def user_profile(request, pk):
    if user_or_mod(request):
        user = get_object_or_404(User, id=pk)
        your_acc = False
        in_friends = Friend.objects.filter(requester=request.user.id, accepter=pk).exists()
        podpisok = Friend.objects.filter(requester=pk)
        podpischikov = Friend.objects.filter(accepter=pk)
        if request.user.id == pk:
            recipes = user.recipe_set.filter().order_by('-publication_date')
            your_acc = True
        else:
            recipes = user.recipe_set.filter(is_verified=True, deletion_reason='').order_by('-publication_date')


        podpisok_count = int(len(podpisok))
        podpischikov_count = int(len(podpischikov))
        context = {'user': user, 'recipes': recipes, 'your_acc': your_acc,
                   'in_friends': in_friends, 'podpisok_count': podpisok_count, 'podpischikov_count': podpischikov_count
                   }
        return render(request, 'user/user_profile.html', context)
    else:
        return redirect('page_404')


@login_required(login_url='login')
def my_profile(request):
    if user_or_mod(request):
        user = get_object_or_404(User, id=request.user.id)
        podpischikov = Friend.objects.filter(accepter=request.user.id)
        podpisok = Friend.objects.filter(requester=request.user.id)
        podpischikov_count = int(len(podpischikov))
        podpisok_count = int(len(podpisok))
        recipes = user.recipe_set.filter().order_by('-publication_date')
        context = {'user': user, 'recipes': recipes, 'your_acc': True, 'podpisok_count': podpisok_count, 'podpischikov_count': podpischikov_count}
        return render(request, 'user/user_profile.html', context)
    else:
        return redirect('page_404')


@login_required(login_url='login')
def recipe_detail(request, id):
    if user_or_mod(request):
        recipe = get_object_or_404(Recipe, id=id)
        ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        ingredient_list = [(ingredient.ingredient.name, ingredient.quantity_in_grams) for ingredient in ingredients]
        is_fav = FavoriteRecipe.objects.filter(user=request.user.id, recipe=recipe).exists()
        if not recipe.is_verified:
            if request.user.id == recipe.user.id or mod(request):
                if mod(request):
                    context = {'recipe': recipe, 'ingredients': ingredient_list, 'moder': True}
                    return render(request, 'user/recipe_detail.html', context)
                context = {'recipe': recipe, 'ingredients': ingredient_list}
                return render(request, 'user/recipe_detail.html', context)
            else:
                return redirect('page_404')
        else:
            context = {'recipe': recipe, 'ingredients': ingredient_list, 'is_fav': is_fav}
            return render(request, 'user/recipe_detail.html', context)
    else:
        return redirect('page_404')


@login_required(login_url='login')
def create_recipe(request):
    if user_or_mod(request):
        if request.method == 'POST':
            form = RecipeForm(request.POST, request.FILES)
            if form.is_valid():
                recipe = form.save(commit=False)
                recipe.user = request.user
                recipe.save()
                return redirect('manage_ingredients', recipe_id=recipe.id)
        else:
            form = RecipeForm()
            return render(request, 'user/create_recipe.html', {'form': form})
    else:
        return redirect('page_404')


@login_required(login_url='login')
def search_recipe(request):
    if user_or_mod(request):
        recipes = Recipe.objects.filter(is_verified=True)  # Получаем все рецепты по умолчанию

        # Фильтрация по названию
        title_query = request.GET.get('title', '')
        if title_query:
            recipes = recipes.filter(title__icontains=title_query)

        # Фильтрация по времени приготовления
        cooking_time_query = request.GET.get('cooking_time', '')
        if cooking_time_query.isdigit():
            recipes = recipes.filter(cooking_time__lte=int(cooking_time_query))

        # Фильтрация по тегам
        tag_ids = request.GET.getlist('tags')
        if tag_ids:
            recipes = recipes.filter(recipetag__tag__id__in=tag_ids).distinct()

        tags = Tag.objects.all()  # Получаем все теги для отображения в форме
        return render(request, 'user/search_recipe.html', {'recipes': recipes, 'tags': tags, 'selected_tags': tag_ids, 'title_query': title_query,
                                                           'cooking_time_query': cooking_time_query})

    else:
        return redirect('page_404')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.deletion_reason is not None and user.deletion_reason != '':
                return render(request, 'auth/login.html',{'error':
                'Вы были заблокированы по причине:' + user.deletion_reason})
            login(request, user)
            if user.role == 'ADMIN':
                return redirect('admin_home')
            return redirect('home')
        else:
            return render(request, 'auth/login.html', {'error':
                    'Неверное имя пользователя или пароль'})
    return render(request, 'auth/login.html')


def user_logout(request):
    logout(request)
    return redirect('login')
