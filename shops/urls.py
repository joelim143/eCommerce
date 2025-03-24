from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
# from django.urls import get_resolver

# print(get_resolver().reverse_dict.keys())

urlpatterns = [
    path('', views.home, name='home'), 
     
    path("signup/", views.signup, name="signup"),
    path('customers/', views.list_customers, name='customer_list'),
    path('customers/add/', views.create_customer, name='create_customer'),
    path('customers/<int:pk>/edit/', views.update_customer, name='update_customer'),
    path('customers/<int:pk>/delete/', views.delete_customer, name='delete_customer'),

    path('products/', views.list_products, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/add/', views.create_product, name='product_add'),
    path('products/<int:pk>/edit/', views.update_product, name='product_edit'),
    path('products/<int:pk>/delete/', views.delete_product, name='product_delete'),

    path('generate-description/', views.generate_description, name='generate_description'),

    # path('purchase-history/', views.purchase_history, name='purchase_history'),
    # path('purchase-details/<int:purchase_id>/', views.purchase_details, name='purchase_details'),

    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/edit/<int:cart_item_id>/', views.edit_cart_item, name='edit_cart_item'),
    path('cart/delete/<int:cart_item_id>/', views.delete_cart_item, name='delete_cart_item'),

    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path ('cart_detail/', views.cart_detail, name='cart_detail'),

    # path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('feedback/submit/<int:product_id>/', views.submit_feedback, name='submit_feedback'),
    path('feedback/view/<int:product_id>/', views.view_feedback, name='view_feedback'),
    path('products/<int:product_id>/feedback/', views.submit_feedback, name='product_feedback'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name="logout.html"), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('accounts/profile/', views.profile, name='profile'),
    
    # path('chatbot/', views.chatbot_page, name='chatbot_page'),
    # path('chatbot-response/', views.chatbot_response, name='chatbot_response'),
    # path("chatbot/", views.chatbot_response, name="chatbot_response"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
