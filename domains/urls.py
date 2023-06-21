from django.urls import path
from rest_framework.routers import DefaultRouter

from domains.views import (AccessLogView, CategoryView, DomainLeadSummaryView,
                           DomainLeadsView, DomainViewSet, GetVideoAPI,
                           MyStable, NegotiationView, NotificationView,
                           OrderView, SearchDomainAPI, SponsoredCartView,
                           SponsoredHeadlinesView, VideoUploadAPI, VideoView, UsersView, ApprovalView, ApprovalDetailView)

router = DefaultRouter()
router.register('', DomainViewSet, basename='domain')

urlpatterns = [
    path('search/', SearchDomainAPI.as_view()),
    path('upload_video/', VideoUploadAPI.as_view()),
    path('get_video/<int:pk>', GetVideoAPI.as_view()),
    path('my-stable/', MyStable.as_view()),
    path('videos/', VideoView.as_view()),
    path('domain-leads/', DomainLeadsView.as_view()),
    path('domain-leads-summary/', DomainLeadSummaryView.as_view()),
    path('notifications/', NotificationView.as_view()),
    path('sponsored-headlines/', SponsoredHeadlinesView.as_view()),
    path('sponsored-headlines/cart/', SponsoredCartView.as_view()),
    path('sponsored-headlines/order/', OrderView.as_view()),
    path('categories/', CategoryView.as_view()),
    path('negotiation/', NegotiationView.as_view()),
    path('accesslog/', AccessLogView.as_view()),
    path('admin/approval', ApprovalView.as_view()),
    path('admin/approval/<int:pk>', ApprovalDetailView.as_view()),
    path('users/', UsersView.as_view())
]

urlpatterns += router.urls
