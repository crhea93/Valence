from django.urls import path, re_path
from link import views

urlpatterns = [
    path("add_link", views.add_link, name="add_link"),
    path("delete_link", views.delete_link, name="delete_link"),
    path("update_link", views.update_link, name="update_link"),
    path("update_link_pos", views.update_link_pos, name="update_link_pos"),
    path("swap_link_direction", views.swap_link_direction, name="swap_link_direction"),
]
