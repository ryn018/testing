from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    # path('home/', views.emi_calculator, name='home'),
    path('home/', views.home, name='home'),
    path('emi/', views.emi_calculator, name='emi_calculator'),
    path('sip/', views.sip_calculator, name='sip_calculator'),
    path('fd/', views.fd_calculator, name='fd_calculator'),
    path('rd/', views.rd_calculator, name='rd_calculator'),
    path('retirement/', views.retirement_savings_view, name='retirement_savings_estimator'),
    path('loan-eligibility/', views.loan_eligibility_view, name='loan_eligibility_estimator'),
    path('credit-card/', views.credit_card_calculator_view, name='credit_card_interest_calculator'),
    path('taxable-income/', views.taxable_income_view, name='taxable_income_calculator'),
    path('budget/', views.budget_planner_view, name='simple_budget_planner'),
    path('net-worth/', views.net_worth_view, name='net_worth_calculator'),

     path('balance/', views.view_balance, name='view_balance'),
    path('deposit/', views.deposit, name='deposit'),
    path('withdraw/', views.withdraw, name='withdraw'),
    # ml
     path('predict-loan/', views.predict_loan_amount, name='predict_loan')
]
