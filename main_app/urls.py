import django.conf.urls
from django.conf.urls.static import static
from django.urls import path, re_path

from django.conf import settings
from .views import *

urlpatterns = [
    path('register/', user_register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('', home, name='home'),
    path('admin_home/', admin_home, name='admin_home'),
    path('search/', search_recipe, name='search_recipe'),
    path('profile/<int:pk>', user_profile, name='user_profile'),
    path('profile/', my_profile, name='my_profile'),
    path('create_recipe/', create_recipe, name='create_recipe'),
    path('recipe/<int:id>', recipe_detail, name='recipe_detail'),
    path('404/', custom_404_view, name='page_404'),
    path('admin_home/add_tag/', add_tag, name='add_tag'),
    path('admin_home/delete_user/<int:user_id>/', delete_user, name='delete_user'),
    path('admin_home/change_user_role/<int:user_id>/', change_user_role, name='change_user_role'),
    path('admin_home/undelete_user/<int:user_id>/', undelete_user, name='undelete_user'),
    path('backup/sql/', BackupSQLView.as_view(), name='backup_sql'),
    path('backup/csv/', BackupCSVView.as_view(), name='backup_csv'),
    path('import/sql/', upload_sql_file, name='upload_sql_file'),
    path('friend/<int:id>/', add_or_delete_friend, name='add_or_delete_friend'),
    path('recipe/fav/<int:id>/', add_or_delete_favorite_recipe, name='add_or_delete_favorite_recipe'),
    path('recipe/fav/', favorite_recipe_list, name='favorite_recipe_list'),
    path('user/<int:user_id>/relationships/<str:is_subscriber>/', user_relationships, name='user_relationships'),
    path('ingridients/add/<int:recipe_id>/', manage_ingredients, name='manage_ingredients'),
    path('tags/add/<int:recipe_id>/', manage_tags, name='manage_tags'),
    path('recipe/not_verified/', not_verified_recipes_list, name='not_verified_recipes_list'),
    path('steps/<int:recipe_id>/', recipe_steps_list, name='recipe_steps_list'),
    path('steps/add/<int:recipe_id>/', add_recipe_step, name='add_recipe_step'),
    path('recipe/accept/<int:recipe_id>/<str:is_accept>/', accept_recipe, name='accept_recipe'),
    path('admin_home/statistics/', statistics, name='statistics'),
    path('profile/edit/', edit_profile, name='edit_profile'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

