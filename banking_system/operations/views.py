
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import BankAccount, Transaction
from .forms import TransactionForm
from .forms import LoanPredictionForm

import joblib
import numpy as np
import os
#Login
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

@login_required
def view_balance(request):
    """View the balance of the user's bank account."""
    try:
        bank_account = BankAccount.objects.get(user=request.user)
        balance = bank_account.balance
    except BankAccount.DoesNotExist:
        balance = 0
    return render(request, 'operations/view_balance.html', {'balance': balance})

@login_required
def deposit(request):
    """Handle deposits into the user's bank account."""
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            bank_account, created = BankAccount.objects.get_or_create(user=request.user)
            if amount > 0:
                transaction = Transaction.objects.create(
                    account=bank_account,
                    amount=amount,
                    transaction_type=Transaction.DEPOSIT
                )
                messages.success(request, f'Deposited {amount} successfully!')
                return redirect('view_balance')
            else:
                messages.error(request, 'Amount must be positive.')
    else:
        form = TransactionForm()
    return render(request, 'operations/transaction_form.html', {'form': form, 'transaction_type': 'Deposit'})

@login_required
def withdraw(request):
    """Handle withdrawals from the user's bank account."""
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            bank_account = BankAccount.objects.get(user=request.user)
            if amount > 0 and bank_account.balance >= amount:
                transaction = Transaction.objects.create(
                    account=bank_account,
                    amount=amount,
                    transaction_type=Transaction.WITHDRAWAL
                )
                messages.success(request, f'Withdrew {amount} successfully!')
                return redirect('view_balance')
            else:
                messages.error(request, 'Insufficient balance or invalid amount.')
    else:
        form = TransactionForm()
    return render(request, 'operations/transaction_form.html', {'form': form, 'transaction_type': 'Withdraw'})

def login_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # redirect to a home page or dashboard
        else:
            error = "Invalid username or password."

    return render(request, 'operations/login.html', {'error': error})

from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.shortcuts import render, redirect

def signup_view(request):
    error = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            error = "Passwords do not match."
        elif User.objects.filter(username=username).exists():
            error = "Username already taken."
        else:
            user = User.objects.create_user(username=username, password=password)
            login(request, user)
            return redirect('home')  # redirect to home after successful signup

    return render(request, 'operations/signup.html', {'error': error})



def logout_view(request):
    logout(request)
    return redirect('login')


def home(request):
    return render(request, 'operations/home.html', {'hide_sidebar': True})


@login_required
def emi_calculator(request):
    result = None
    if request.method == 'POST':
        principal = float(request.POST['principal'])
        rate = float(request.POST['rate'])
        tenure = int(request.POST['tenure'])

        monthly_rate = rate / (12 * 100)
        months = tenure * 12
        emi = principal * monthly_rate * ((1 + monthly_rate) ** months) / (((1 + monthly_rate) ** months) - 1)
        result = round(emi, 2)

    return render(request, 'operations/emi_calculator.html', {'result': result})

def sip_calculator(request):
    result = None
    if request.method == 'POST':
        monthly_investment = float(request.POST['monthly_investment'])
        rate = float(request.POST['rate'])
        years = int(request.POST['years'])

        monthly_rate = rate / (12 * 100)
        months = years * 12
        maturity = monthly_investment * (((1 + monthly_rate) ** months - 1) * (1 + monthly_rate)) / monthly_rate
        result = round(maturity, 2)

    return render(request, 'operations/sip_calculator.html', {'result': result})


def rd_calculator(request):
    result = None
    if request.method == 'POST':
        monthly_investment = float(request.POST['monthly_investment'])
        rate = float(request.POST['rate'])
        years = int(request.POST['years'])

        tenure_months = years * 12
        monthly_rate = rate / (100 * 12)

        maturity = monthly_investment * tenure_months + \
                   monthly_investment * (tenure_months * (tenure_months + 1) / 2) * monthly_rate

        result = round(maturity, 2)

    return render(request, 'operations/rd_calculator.html', {'result': result})

def fd_calculator(request):
    result = None
    if request.method == 'POST':
        principal = float(request.POST['principal'])
        rate = float(request.POST['rate'])
        years = int(request.POST['years'])

        compounding_frequency = 4  # Quarterly compounding
        rate_per_period = rate / (100 * compounding_frequency)
        total_periods = years * compounding_frequency

        maturity = principal * ((1 + rate_per_period) ** total_periods)
        result = round(maturity, 2)

    return render(request, 'operations/fd_calculator.html', {'result': result})

def loan_eligibility_view(request):
    result = None
    if request.method == 'POST':
        income = float(request.POST['monthly_income'])
        expenses = float(request.POST['monthly_expenses'])
        years = int(request.POST['tenure'])
        rate = float(request.POST['interest_rate'])

        available_income = income - expenses
        monthly_rate = rate / (12 * 100)
        tenure_months = years * 12

        if monthly_rate == 0:
            result = available_income * tenure_months
        else:
            result = available_income * (((1 + monthly_rate) ** tenure_months - 1) /
                                         (monthly_rate * (1 + monthly_rate) ** tenure_months))
            result = round(result, 2)

    return render(request, 'operations/loan_eligibility_calculator.html', {'result': result})



def retirement_savings_view(request):
    result = None
    if request.method == 'POST':
        current_savings = float(request.POST['current_savings'])
        monthly_contribution = float(request.POST['monthly_contribution'])
        annual_rate = float(request.POST['annual_rate'])
        years_until_retirement = int(request.POST['years_until_retirement'])

        monthly_rate = annual_rate / (12 * 100)
        months = years_until_retirement * 12
        future_value = current_savings * ((1 + monthly_rate) ** months) + \
                       monthly_contribution * (((1 + monthly_rate) ** months - 1) * (1 + monthly_rate)) / monthly_rate

        result = round(future_value, 2)

    return render(request, 'operations/retirement_calculator.html', {'result': result})




def calculate_credit_card_balance(balance, annual_rate, months, min_payment_rate=0.05):

   
    
    if balance <= 0 or annual_rate < 0 or months <= 0:
        raise ValueError("Invalid input values")

    monthly_rate = annual_rate / 12 / 100
    for _ in range(months):
        min_payment = balance * min_payment_rate
        interest = balance * monthly_rate
        balance = balance - min_payment + interest
    return round(balance, 2)


def credit_card_calculator_view(request):
    result = None
    if request.method == 'POST':
        try:
            balance = float(request.POST['balance'])
            annual_rate = float(request.POST['annual_rate'])
            months = int(request.POST['months'])
            result = calculate_credit_card_balance(balance, annual_rate, months)
        except (ValueError, KeyError):
            result = "Invalid input. Please enter valid numbers."
    return render(request, 'operations/credit_card_calculator.html', {'result': result})

def calculate_taxable_income(gross_income, deductions=50000):
    """
    Calculate taxable income after standard deduction.
    
    Parameters:
    gross_income (float): Total gross income
    deductions (float): Deduction amount (default ₹50,000)
    
    Returns:
    float: Taxable income
    """
    if gross_income < 0 or deductions < 0:
        raise ValueError("Income and deductions must be non-negative")

    taxable_income = gross_income - deductions
    return round(max(taxable_income, 0), 2)


def taxable_income_view(request):
    result = None
    if request.method == 'POST':
        try:
            gross_income = float(request.POST['gross_income'])
            deductions = float(request.POST.get('deductions', 50000))  # Default ₹50,000
            result = calculate_taxable_income(gross_income, deductions)
        except (ValueError, KeyError, TypeError):
            result = "Invalid input. Please enter valid numbers."

    # Update the template name here (corrected the typo from .htmll to .html)
    return render(request, 'operations/taxable_income.html', {'result': result})




def plan_budget(income, fixed_expenses, variable_expenses):
    """
    Plan a simple budget based on income and expenses.

    Parameters:
    income (float): Monthly income
    fixed_expenses (float): Total fixed expenses
    variable_expenses (float): Total variable expenses

    Returns:
    dict: Summary of savings and suggestions
    """
    if income <= 0 or fixed_expenses < 0 or variable_expenses < 0:
        raise ValueError("Invalid input values")

    total_expenses = fixed_expenses + variable_expenses
    savings = income - total_expenses
    suggestion = "Increase savings" if savings < 0.2 * income else "Good saving habit"
    return {
        "Total Expenses": round(total_expenses, 2),
        "Savings": round(savings, 2),
        "Suggestion": suggestion
    }



def budget_planner_view(request):
    result = None
    if request.method == 'POST':
        try:
            income = float(request.POST['income'])
            fixed_expenses = float(request.POST['fixed_expenses'])
            variable_expenses = float(request.POST['variable_expenses'])
            result = plan_budget(income, fixed_expenses, variable_expenses)
        except (ValueError, KeyError):
            result = "Invalid input. Please enter valid numbers."
    return render(request, 'operations/budget_planner.html', {'result': result})


def calculate_net_worth(assets, liabilities):
    return round(assets - liabilities, 2)

def net_worth_view(request):
    result = None
    if request.method == 'POST':
        try:
            assets = float(request.POST.get('assets', 0))
            liabilities = float(request.POST.get('liabilities', 0))
            result = calculate_net_worth(assets, liabilities)
        except (ValueError, KeyError):
            result = "Invalid input. Please enter valid numbers."
    return render(request, 'operations/net_worth.html', {'result': result})


# Machine learning
def predict_loan_amount(request):
    prediction = None
    if request.method == 'POST':
        form = LoanPredictionForm(request.POST)
        if form.is_valid():
            data = np.array([[form.cleaned_data['age'],
                              form.cleaned_data['income'],
                              form.cleaned_data['credit_score'],
                              form.cleaned_data['tenure'],
                              form.cleaned_data['existing_loan'],
                              form.cleaned_data['dependents']]])
            model_path = os.path.join('operations', 'ml', 'loan_model.pkl')
            model = joblib.load(model_path)
            prediction = model.predict(data)[0]
    else:
        form = LoanPredictionForm()

    return render(request, 'operations/predict_loan.html', {'form': form, 'prediction': prediction})
