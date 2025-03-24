from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    is_admin = models.BooleanField(default=False)  # For admin users
    address = models.TextField(blank=True, null=True)  # For customer address

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer', null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=15)
    address = models.TextField()
    status = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Product(models.Model):
    code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    # name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    qty = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True) # Add Image field

# class Cart(models.Model):
#     customer = models.ForeignKey('Customer', on_delete=models.CASCADE, default=1)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)

#     def save(self, *args, **kwargs):
#         # If this is a new instance without a primary key, save first.
#         if not self.pk:
#             super().save(*args, **kwargs)
#         # Now recalculate totals based on related CartItem objects.
#         items = self.items.all()
#         self.discount = sum(item.discount for item in items)
#         self.total = sum(item.line_total for item in items)
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Cart for {self.customer} - Total: {self.total}"

# class Cart(models.Model):
#     # Use a OneToOneField so each customer has one unique cart;
#     # or if you prefer a separate PK, remove primary_key=True from customer.
#     customer = models.OneToOneField(
#         'Customer',
#         on_delete=models.CASCADE,
#         related_name='cart'
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

#     def save(self, *args, **kwargs):
#         # Dynamically calculate the total
#         self.total = sum(item.line_total for item in self.items.all())
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"Cart for {self.customer.name} – Total: {self.total}"

class Cart(models.Model):
    customer = models.OneToOneField(
        'Customer',
        on_delete=models.CASCADE,
        related_name='cart'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, editable=False)

    def save(self, *args, **kwargs):
        # Only calculate the total if the Cart already exists
        if self.pk:
            self.total = sum(item.line_total for item in self.items.all())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cart for {self.customer.name} – Total: {self.total}"

class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price per unit
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Discount per unit
    line_total = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # Calculate the line total
        self.line_total =(self.price * self.qty) - self.discount
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product} - {self.qty} units"


class PurchaseHeader(models.Model):
    purchase_date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default=1, related_name='purchase_headers')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default = 0)

class PurchaseDetail(models.Model):
    purchaseHeader = models.ForeignKey(PurchaseHeader, on_delete=models.CASCADE, related_name='purchase_details')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    description = models.TextField()
    qty = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default = 0)

class Feedback(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, default=1)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, default=1)
    comments = models.TextField()
    sentiment_score = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sentiment = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Populate sentiment based on sentiment_score
        if self.sentiment_score > 0:
            self.sentiment = 'Positive'
        elif self.sentiment_score < 0:
            self.sentiment = 'Negative'
        else:
            self.sentiment = 'Neutral'
        super().save(*args, **kwargs)

class ChatHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat by {self.user.username} at {self.timestamp}"