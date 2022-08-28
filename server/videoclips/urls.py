from django.urls import path, include

from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from . import views


router = SimpleRouter()
router.register(r'list', views.VideoclipView, basename='videoclip')
router.register(r'category', views.CategoryView, basename='category')
router.register(r'subscription', views.VCSubscriptionView,
                basename='subscription')


videoclips_router = routers.NestedSimpleRouter(
    router, r'list', lookup='videoclip')
videoclips_router.register(
    r'categories', views.VCCategoriesView, basename='categories')

videoclips_router.register(
    r'file', views.UploadView, basename='file')

videoclips_router.register(
    r'comments', views.VCCommentView, basename='comments')

videoclips_router.register(
    r'reactions', views.UserReactionView, basename='reactions')

videoclips_router.register(
    r'bans', views.VCBanView, basename='bans')

# urlpatterns = router.urls
urlpatterns = [
    path(r'', include(router.urls)),
    # path(r'', include(router_add.urls)),
    path(r'', include(videoclips_router.urls)),
]

# urlpatterns += router.urls
