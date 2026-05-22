from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing, name='landing'),
    path('connexion/', views.UserLoginView.as_view(), name='login'),
    path('deconnexion/', views.UserLogoutView.as_view(), name='logout'),
    path('inscription/', views.signup, name='signup'),
    path('flux/', views.feed, name='feed'),
    path('posts/', views.posts, name='posts'),
    path('abonnements/', views.following, name='following'),
    path('ticket/nouveau/', views.ticket_create, name='ticket_create'),
    path('ticket/<int:pk>/modifier/', views.ticket_edit, name='ticket_edit'),
    path('ticket/<int:pk>/supprimer/', views.ticket_delete, name='ticket_delete'),
    path(
        'ticket/<int:ticket_pk>/critique/nouvelle/',
        views.review_create,
        name='review_create',
    ),
    path(
        'ticket-critique/nouveau/',
        views.ticket_review_create,
        name='ticket_review_create',
    ),
    path('critique/<int:pk>/modifier/', views.review_edit, name='review_edit'),
    path('critique/<int:pk>/supprimer/', views.review_delete, name='review_delete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
