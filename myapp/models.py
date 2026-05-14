# Create your models here.
from autoslug import AutoSlugField
from pytils.translit import slugify
from django.urls import reverse
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Avg

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Категория")

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name', unique=True, always_update=True, slugify=slugify, verbose_name="URL")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Категория"
    )

    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Image")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Цена (Текущая)")

    old_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Старая цена (для скидки)"
    )

    quantity = models.PositiveIntegerField(default=0, verbose_name="Quantity")
    published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)

    specifications = models.JSONField(verbose_name="Характеристики", default=dict, blank=True)

    def get_absolute_url(self):
        return reverse('product_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.published and not self.published_at:
            self.published_at = timezone.now()
        if not self.published and self.published_at is not None:
            self.published_at = None
        super().save(*args, **kwargs)

    def get_sale_percent(self):
        if self.old_price and self.old_price > self.price:
            discount = (self.old_price - self.price) / self.old_price * 100
            return int(discount)
        return 0

    def get_average_rating(self):
        reviews = self.feedback.all()
        if reviews:
            avg = reviews.aggregate(Avg('rating'))['rating__avg']
            return round(avg, 1) if avg else 0
        return 0


class Feedback(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='feedback', null=True, blank=True, )
    name = models.CharField(max_length=100)
    message = models.TextField()

    RATING_CHOICES = [
        (1, '1 - Очень плохо'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]
    rating = models.IntegerField(choices=RATING_CHOICES, default=5, verbose_name="Оценка")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.product is not None:
            return f"{self.name} ({self.product})"
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Пользователь")

    PAYMENT_METHOD_CHOICES = [
        ('on_delivery', 'Оплата при получении'),
        ('card', 'Оплата картой (на сайте)'),
        ('installments', 'Оплата частями'),
    ]

    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('shipped', 'Отправлен'),
        ('completed', 'Выполнен'),
        ('cancelled', 'Отменен'),
    ]

    first_name = models.CharField(max_length=50, verbose_name="Name")
    last_name = models.CharField(max_length=50, verbose_name="Last Name")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Phone")
    address = models.CharField(max_length=250, verbose_name="Address")
    postal_code = models.CharField(max_length=20, verbose_name="Postal Code")
    city = models.CharField(max_length=100, verbose_name="City")
    created = models.DateTimeField(auto_now_add=True, verbose_name="Created")
    updated = models.DateTimeField(auto_now=True, verbose_name="Updated")
    paid = models.BooleanField(default=False, verbose_name="Paid")

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='on_delivery',
        verbose_name="Способ оплаты"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус заказа"
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f'Order {self.id}'

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity

class Banner(models.Model):
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст описания", blank=True)
    image = models.ImageField(upload_to='banner/', verbose_name="Изображение (1920x600)")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/', verbose_name="Изображение")

    def __str__(self):
        return f"Image for {self.product.name}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Сообщение с сайта"
        verbose_name_plural = "Сообщения с сайта"
        ordering = ['-created_at']

    def __str__(self):
        return f"Сообщение от {self.name} ({self.email})"