from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from . import views
from .views import forgot_password_view, set_new_password_view

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),

    # Authentification
    path('accounts/login/', auth_views.LoginView.as_view(template_name='licenses/login.html'), name='login'),
    
    # Déconnexion (logout) — utilise la vue intégrée Django
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),

    # Inscription
    path('accounts/signup/', views.signup_view, name='signup'),

    # Tableau de bord
    path('dashboard/', views.dashboard_view, name='dashboard'),

    # Gestion des licences
    path('licenses/create/', views.create_license_view, name='create_license'),
    #path('licenses/list/', views.list_licenses, name='license_list'),
    path('licenses/my-licenses/', views.my_licenses_view, name='my_licenses'),

    # Marché - offres achat/vente
    path('market/', views.market_view, name='market'),
    path('market/buy/<int:offer_id>/', views.buy_license_view, name='buy_license'),
    path('market/sell/', views.sell_license_view, name='sell_license'),

    # Historique des investissements
    path('history/', views.investment_history_view, name='history'),

    # Offres directes achat/vente
    path('add-buy-offer/', views.add_buy_offer_view, name='add_buy_offer'),
    path('add-sell-offer/', views.add_sell_offer_view, name='add_sell_offer'),

    # API vérification licence
    path('api/verify/', views.verify_license_post, name='verify_license_post'),

    # Test envoi email
    #path('test-email/', views.test_email, name='test_email'),

    # Vérification de compte
    path('verify/', views.verify_account, name='verify_account'),

    path("solde-data/", views.solde_data_view, name="solde_data"),

    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('set-new-password/', views.set_new_password_view, name='set_new_password'),
]
