from django.urls import path

from . import views

app_name = "myapp"
urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.loginView, name="login"),
    path("logout/", views.logoutView, name="logout"),
    path("missions/", views.missions, name="missions"),
    path("details/<int:mission_id>", views.details, name="details"),
    path("create_milestone/<int:mission_id>", views.create_milestone, name="create_milestone"),
    path("finish_milestone/<int:milestone_id>", views.finish_milestone, name="finish_milestone"),
    path("delete_milestone/<int:milestone_id>", views.delete_milestone, name="delete_milestone"),
    path("mark_milestone/<int:mission_id>", views.mark_milestone, name="mark_milestone"),
    path("edit/<int:mission_id>", views.edit, name="edit"),
    path("finish/<int:mission_id>", views.finish, name="finish"),
    path("fail/<int:mission_id>", views.fail, name="fail"),
    path("cancel/<int:mission_id>", views.cancel, name="cancel"),
    path("properties/", views.properties, name="properties"),
    path("new_mission/", views.new_mission, name="new_mission"),
    path("new_special_skill/", views.new_special_skill, name="new_special_skill")
]
