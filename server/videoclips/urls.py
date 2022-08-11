from django.urls import path

from videoclips.views import CategoryView, VideoclipView


urlpatterns = [
    path('list/', VideoclipView.as_view(), name='videoclip'),
    path('category/', CategoryView.as_view({'get': 'list'}), name='category'),
    path('category/<int:pk>/',
         CategoryView.as_view({'get': 'retrieve'}), name='category'),
]
