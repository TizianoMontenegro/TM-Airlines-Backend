from django.urls import path
from . import views

urlpatterns = [
    path("users/<int:user_id>/", views.RAGUserProfileView.as_view(), name="rag-user-profile"),
    path("users/<int:user_id>/bookings/", views.RAGUserBookingsView.as_view(), name="rag-user-bookings"),
    path("users/<int:user_id>/loyalty/", views.RAGUserLoyaltyView.as_view(), name="rag-user-loyalty"),
    path("bookings/<str:booking_id>/", views.RAGBookingDetailView.as_view(), name="rag-booking-detail"),
    path("flights/<str:flight_number>/status/", views.RAGFlightStatusView.as_view(), name="rag-flight-status"),
    path("flights/search/", views.RAGFlightSearchView.as_view(), name="rag-flight-search"),
]
