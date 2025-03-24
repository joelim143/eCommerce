# Correct way to import timezone in Django:
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import (
    Customer, 
    Product, 
    Cart, 
    CartItem, 
    # PurchaseHeader, 
    # PurchaseDetail, 
    Feedback,
    # ChatHistory
)
from .forms import (
    CustomerForm, 
    ProductForm, 
    FeedbackForm, 
    CartItemForm, 
    CustomUserCreationForm,
    # ChatForm
)
from transformers import pipeline
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.views.decorators.csrf import csrf_exempt
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import GPT2LMHeadModel, GPT2Tokenizer

import numpy as np
import pandas as pd
import google.generativeai as genai
import os
import json
import logging
import nltk
nltk.download('vader_lexicon')
from nltk.sentiment import SentimentIntensityAnalyzer
# When to use vader?
# •	Social media sentiment analysis (e.g., tweets, reviews, or comments).
# •	Short texts where emojis, slang, and punctuation are common.
# •	When speed and simplicity are priorities over advanced machine learning models.

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# @csrf_exempt  # Allows AJAX requests from frontend
# def chatbot_response(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         user_input = data.get("message", "")
#         if not user_input:
#             return JsonResponse({"error": "Empty message"}, status=400)
#         try:
#             model = genai.GenerativeModel("gemini-pro")  # Using Gemini AI model
#             response = model.generate_content(user_input)
#             bot_text = response.text

#             # Save the chat history if the user is authenticated
#             if request.user.is_authenticated:
#                 ChatHistory.objects.create(
#                     user=request.user,
#                     user_message=user_input,
#                     bot_response=bot_text
#                 )
#             return JsonResponse({"response": bot_text})
#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=500)
#     return JsonResponse({"error": "Invalid request"}, status=400)

# @login_required
# def chatbot_page(request):
#     form = ChatForm()
#     chat_history = ChatHistory.objects.filter(user=request.user).order_by('timestamp')
#     return render(request, 'chatbot.html', {'form': form, 'chat_history': chat_history})

@login_required
def profile(request):
    """
    View function to render the profile page.
    Args:
        request: The HTTP request object.
    Returns:
        Rendered profile.html template with context (if needed).
    """
    return render(request, 'profile.html', {"user": request.user})

def home(request):
    """
    View function to render the home page.
    Args:
        request: The HTTP request object.
    Returns:
        Rendered home.html template with context (if needed).
    """
    # If you need to pass context data, you can define it here
    context = {
        'page_title': 'Home Page',  # Example context data
    }
    return render(request, 'home.html', context)

# def signup(request):
#     if request.method == "POST":
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)  # Log in the new user
#             return redirect("home")  # Redirect after signup
#         else:
#             # Print form errors to the console for debugging
#             print(form.errors)
#     else:
#         form = CustomUserCreationForm()
#     return render(request, "signup.html", {"form": form})

def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        # form = CustomerForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create a new Customer instance
            Customer.objects.create(
                user=user, # Link the new customer to the new user
                name=user.username,
                email=user.email,
                contact=form.cleaned_data.get('contact'),
                address=form.cleaned_data.get('address'),
                status=form.cleaned_data.get('status')
            )
            login(request, user)  # Log in the new user
            return redirect("home")  # Redirect after signup
        else:
            # Print form errors to the console for debugging
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    return render(request, "signup.html", {"form": form})

# Create a customer
def create_customer(request):
    customer = None  # Initialize customer variable
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            customer = form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {'form': form})

# List customers
def list_customers(request):
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers})

# Update a customer
def update_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'customer_form.html', {'form': form})

# Delete a customer
def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        customer.delete()
        return redirect('customer_list')
    return render(request, 'customer_confirm_delete.html', {'customer': customer})


# GenAI model for description generation
def generate_product_description(name):
    generator = pipeline('text-generation', model='gpt2')
    prompt = f"Write a product description for {name}:"
    result = generator(prompt, max_length=50, num_return_sequences=1)
    return result[0]['generated_text']


def generate_description(request):
    if request.method == "POST":
        prompt = request.POST.get('prompt', '')
        if not prompt:
            return JsonResponse({"error": "Prompt is required."}, status=400)
        
        try:
            # Load the tokenizer and model directly (no pipeline involved)
            tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
            model = GPT2LMHeadModel.from_pretrained('gpt2')

            # Encode the prompt and generate text
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=50)
            outputs = model.generate(**inputs, max_length=50, num_return_sequences=1)

            # Decode the generated output back to text
            generated_description = tokenizer.decode(outputs[0], skip_special_tokens=True)

            return JsonResponse({"description": generated_description})
        
        except Exception as e:
            return JsonResponse({"error": f"Failed to generate description: {str(e)}"}, status=500)
    return JsonResponse({"error": "Invalid request method."}, status=405)


# Create a product with dynamic description
def create_product(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            # Access the 'prompt' field value for additional logic
            # prompt_value = form.cleaned_data.get('prompt')
            # product.description = generate_product_description(prompt_value)
            product.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form})

# List products
def list_products(request):
    # products = Product.objects.all()
    # return render(request, 'product_list.html', {'products': products})

    query = request.GET.get('query', '')
    products = Product.objects.all()
    if query:
        products = products.filter(description__icontains=query)
    return render(request, 'product_list.html', {'products': products})

# Update a product
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form})

def product_detail(request, product_id):
    products = get_object_or_404(Product, id=product_id)
    return render(
        request,
        'product_detail.html', 
        {
            'username': request.user.username,
            'products': [products]
            # 'product': product # Pass single product
        }

    )

# Delete a product
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})


# def purchase_history(request):
#     """View to display the purchase history of the logged-in customer."""
#     customer = Customer.objects.get(name=request.user.username)
#     # customer = request.user.customer  # Assuming a one-to-one relationship with User
#     purchase_headers = PurchaseHeader.objects.filter(customer=customer).order_by('-purchase_date')
#     context = {
#         'purchase_headers': purchase_headers,
#     }
#     return render(request, 'purchase_history.html', context)

# def purchase_details(request, purchase_id):
#     """View to display the details of a specific purchase."""
#     purchase_header = get_object_or_404(PurchaseHeader, id=purchase_id, customer=request.user.customer)
#     purchase_details = PurchaseDetail.objects.filter(purchaseHeader=purchase_header)
#     context = {
#         'purchase_header': purchase_header,
#         'purchase_details': purchase_details,
#     }
#     return render(request, 'purchase_details.html', context)

# View to display the profile of the logged-in user
@login_required
def profile(request):
    return render(request, "profile.html", {"user": request.user})


# View to display the cart and its item

@login_required
def cart_detail(request):
    """View to display cart details."""
    
    cart_customer = Customer.objects.get(name=request.user.username)
    try:
        cart = Cart.objects.get(customer=cart_customer)
        cart_items = cart.items.all()
        print("cart ")
        print(cart)
        print (cart_items)
    except Cart.DoesNotExist:
        cart, cart_items = None, None
    return render(request, 'cart_detail.html', {'cart': cart, 'cart_items': cart_items})

# @login_required
# def purchase(request):
#     cart_customer = Customer.objects.get(name=request.user.username)
#     cart = Cart.objects.get(customer=cart_customer)
#     cart_items = cart.items.all()
#     # You need to set the cart to empty
#     # You need to also add this to the Purchase History table so that
#     # you can render
#     return render(request, 'purchase_cart.html')
    


# View to add a product to the cart 
# @login_required
# def add_to_cart(request):
#     if request.method == "POST":
#         try:
#             data = json.loads(request.body)
#             product_id = data.get('product_id')
#             print(product_id)

#             customer_email = request.user.email
#             print(customer_email)

#             cart_customer = Customer.objects.get(email=customer_email)
#             print(cart_customer)

#             product = get_object_or_404(Product, id=product_id)
#             print(product)

            
#             cart, created = Cart.objects.get_or_create(
#                 customer=cart_customer,
#                 defaults={'discount': 0, 'total': 0}
#             )

#             # Set timestamps if the cart is newly created or updated
#             cart.updated_at = timezone.now()
#             if created:
#                 cart.created_at = timezone.now()
#             cart.save()

#             print(cart)

#             # Check if the product is already in the cart
#             cart_item, created = CartItem.objects.get_or_create(
#                 cart=cart,
#                 product=product,
#                 defaults={'qty': 1, 'price': product.price, 'discount': 0}
#             )

#             if not created:
#                 # If already in cart, just increase quantity
#                 cart_item.qty += 1
#                 cart_item.save()

#             # Recalculate the cart total and discount
#             cart_items = CartItem.objects.filter(cart=cart)
#             total = 0
#             discount = 0

#             for item in cart_items:
#                 item_total = item.price * item.qty
#                 total += item_total
#                 discount += item.discount  # Update this if specific discount logic applies per item

#             cart.total = total
#             cart.discount = discount  # Update this if you apply global cart-level discounts
#             cart.save()

#             return JsonResponse({"success": True, "total": cart.total, "discount": cart.discount})

#         except Exception as e:
#             return JsonResponse({"error": str(e)}, status=400)

#     return JsonResponse({"error": "Invalid request method."}, status=405)

@login_required
def add_to_cart(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            print("Product ID:", product_id)

            customer_email = request.user.email
            print("Customer Email:", customer_email)

            cart_customer = Customer.objects.get(email=customer_email)
            print("Cart Customer:", cart_customer)

            product = get_object_or_404(Product, id=product_id)
            print("Product:", product)

            # Get or create the cart for this customer
            cart, cart_created = Cart.objects.get_or_create(
                customer=cart_customer,
                defaults={
                    'discount': 0, 
                    'total': 0, 
                    'created_at': timezone.now(), 
                    'updated_at': timezone.now()
                }
            )
            # Update timestamp if the cart already existed
            cart.updated_at = timezone.now()
            cart.save()
            print("Cart:", cart)

            # Get or create the cart item for this product in the cart
            cart_item, item_created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'qty': 1, 'price': product.price, 'discount': 0}
            )
            if not item_created:
                # If the product already exists in the cart, increase its quantity
                cart_item.qty += 1
                cart_item.save()

            # Recalculate the cart total and discount
            cart_items = CartItem.objects.filter(cart=cart)
            total = sum(item.price * item.qty for item in cart_items)
            discount = sum(item.discount for item in cart_items)
            cart.total = total
            cart.discount = discount
            cart.save()

            return JsonResponse({"success": True, "total": cart.total, "discount": cart.discount})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

#View to edit a product quantity in the cart
@login_required
def edit_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)

    if request.method == 'POST':
        form = CartItemForm(request.POST, instance=cart_item)
        if form.is_valid():
            form.save()  # Save the updated quantity and line total
            cart_item.cart.save()  # Recalculate the cart total
            messages.success(request, 'Cart item updated successfully!')
            return redirect('cart_detail')
        else:
            messages.error(request, 'Invalid form submission. Please try again.')

    else:
        form = CartItemForm(instance=cart_item)
    
    return render(request, 'edit_cart_item.html', {'form': form})

# View to delete a product from the cart
@login_required
def delete_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()  # Delete the cart item
    cart_item.cart.save()  # Recalculate the cart total after deletion
    messages.success(request, 'Item removed from cart.')
    return redirect('cart_detail')


def analyze_sentiment(self):
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(self.comments)
    self.sentiment_score = sentiment_scores['compound']
    if sentiment_scores['compound'] > 0.05:
        self.sentiment = "Positive"
    elif sentiment_scores['compound'] < -0.05:
        self.sentiment = "Negative"
    else:
        self.sentiment = "Neutral"


# @login_required
# def submit_feedback(request, product_id):
#     """View to submit feedback for a product."""
#     product = get_object_or_404(Product, id=product_id)

#     if request.method == 'POST':
#         form = FeedbackForm(request.POST)
#         if form.is_valid():
#             feedback = form.save(commit=False)
#             customer = Customer.objects.get(email=request.user.email)
#             feedback.customer = customer
#             feedback.product = product
#             analyze_sentiment(feedback)
#             feedback.save()
#             messages.success(request, "Thank you for your feedback!")
#             return redirect('product_list')
#     else:
#         form = FeedbackForm()

#     return render(request, 'submit_feedback.html', {'form': form, 'product': product})
logger = logging.getLogger(__name__)
@login_required
def submit_feedback(request, product_id):
    """View to submit feedback for a product."""
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            try:
                # Assuming your User model has a one-to-one or one-to-many relationship with Customer
                name = request.user.username
                email = request.user.email
                customer = Customer.objects.get(email=email, name=name)

            except Customer.DoesNotExist:
                logger.error(f"Customer not found for user: {request.user}")
                messages.error(request, "Customer profile not found. Please contact support.")
                return redirect('product_list') #or some other page.
            print(feedback)
            feedback.customer = customer
            feedback.product = product
            try:
                # Asynchronous task (if needed)
                # analyze_sentiment.delay(feedback.id)  # Assuming Celery
                analyze_sentiment(feedback)
            except Exception as e:
                logger.error(f"Error analyzing sentiment: {e}")
                messages.error(request, "An error occurred while analyzing feedback.")

            feedback.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('product_detail', pk=product_id) # Redirect to the product detail page
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = FeedbackForm()

    return render(request, 'submit_feedback.html', {'form': form, 'product': product})

@login_required
def view_feedback(request, product_id):
    """View to see feedback for a specific product."""
    product = get_object_or_404(Product, id=product_id)
    feedback_list = Feedback.objects.filter(product=product).select_related('customer').order_by('-created_at')

    return render(request, 'feedback/view_feedback.html', {
        'product': product,
        'feedback_list': feedback_list,
    })
