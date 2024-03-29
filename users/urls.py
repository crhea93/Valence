from django.urls import path

from . import views, views_CAM, views_Project, views_undo

urlpatterns = [
    path('index/', views.index, name='index'),
    path('loginpage', views.loginpage, name='loginpage'),
    path('signup', views.signup, name='signup'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('settings_account', views.settings, name='settings_account'),
    path('clear_CAM',views.clear_CAM, name='clear_CAM'),
    path('Background',views.background, name='Background'),
    path('Background_German',views.background_german, name='Background_German'),
    path('image_CAM', views.Image_CAM, name ='image_CAM'),
    path('view_pdf', views.view_pdf, name='view_pdf'),
    path('export_CAM', views.export_CAM, name='export_CAM'),
    path('import_CAM', views.import_CAM, name='import_CAM'),
    path('contact_form', views.contact_form, name='contact_form'),
    path('language_change', views.language_change, name='language_change'),
    path('send_cam', views.send_cam, name='send_cam'),
    path('create_participant', views.create_participant, name='create_participant'),
    path('create_researcher', views.create_researcher, name='create_researcher'),
    path('create_random', views.create_random, name='create_random'),
    path('create_individual_cam', views_CAM.create_individual_cam, name='create_individual_cam'),
    path('load_cam', views_CAM.load_cam, name='load_cam'),
    path('delete_cam', views_CAM.delete_cam, name='delete_cam'),
    path('download_cam', views_CAM.download_cam, name='download_cam'),
    path('update_cam_name', views_CAM.update_cam_name, name='update_cam_name'),
    path('join_project', views_Project.join_project, name='join_project'),
    path('create_project', views_Project.create_project, name='create_project'),
    path('project_page', views_Project.project_page, name='project_page'),
    path('join_project_link', views_Project.join_project_link, name='join_project_link'),
    path('project_settings', views_Project.project_settings, name='project_settings'),
    path('load_project', views_Project.load_project, name='load_project'),
    path('delete_project', views_Project.delete_project, name='delete_project'),
    path('download_project', views_Project.download_project, name='download_project'),
    path('language_change_anonymous', views.language_change_anonymous, name='language_change_anonymous'),
    path('tutorials', views.tutorials, name='tutorials'),
    path('instructions', views.instructions, name='instructions'),
    path('delete_user_cam', views.delete_user_cam, name='delete_user_cam'),
    path('contributors', views.contributors, name='contributors'),
    path('privacy', views.privacy, name='privacy'),
    path('FAQ', views.FAQ, name='FAQ'),
    path('clone_cam', views_CAM.clone_CAM, name='clone_cam'),
    path('undo_action', views_undo.undo_action, name='undo_action'),
]
