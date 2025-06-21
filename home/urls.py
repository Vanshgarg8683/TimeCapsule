from django.urls import path, include
from .views import *
urlpatterns = [
    path('', home),
    path('registration', registration),
    path('login', loginpage),
    path('logout', logoutpage),
    path('capsule', create_capsule),
    path('success', successpage),
    path('mycapsules', my_capsules),
    path('editcapsule/<int:id>/', edit_capsule, name="edit_capsule"),
    path('deletecapsule/<int:id>/', delete_capsule, name="delete_capsule")
]