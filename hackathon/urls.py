from django.contrib import admin
from django.urls import path, include
from home import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Admin
    path('admin/', admin.site.urls),

    # Home
    path('', views.homepage, name="homepage"),
    path('home/', views.index1, name="student_home"),
    path("payments/", include("payments.urls")),

    # Auth
    path('login/', views.login_page, name="login_page"),
    path('register/', views.register_page, name="register_page"),

    # Profile
    path('profile/', views.profile, name="profile"),
    path('profile/update/', views.update_profile, name='update_profile'),

    

    # BFI TEST ROUTES
    path('bfi/', views.submit_bfi, name="bfi_form"),     # display + submit BFI form
    path('results/', views.results_new, name="results"), 
            # BFI matches

    path('logout/', views.logout_view, name='logout'),
    # Chat App URLs
    path('chat/', include('chat.urls')),
]

# Static files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)



# """
# URL configuration for hackathon project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.0/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# from django.contrib import admin
# from django.urls import path,include
# from home import views
# from home.views import *
# from django.conf import settings
# from django.conf.urls.static import static


# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path("home/",views.index1,name="index"),
#     path("export_data_to_excel",export_data_to_excel),
#     path('login/',login_page,name="login_page"),
#     path('register/',register_page,name="register_page"),
#     path('',homepage,name="homepage"),
#     path('result/',views.results,name="homepage"),
#     path('profile/',views.profile,name="profile"),
#     path('profile/update/', views.update_profile, name='update_profile'),
#     path('chat/', include('chat.urls')),
    
# ]
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
