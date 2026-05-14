from django.contrib import admin
from .models import Product, Brand, Feedback, Order, OrderItem, Category, Banner, ProductImage,ContactMessage
from django.utils import timezone
from django.http import HttpResponse
import csv
import json
from django.urls import path
from django.shortcuts import render, redirect
import io
from django.db import models
from django_json_widget.widgets import JSONEditorWidget

from modeltranslation.admin import TranslationAdmin, TabbedTranslationAdmin

@admin.action(description="Пометить выбранные как активные")
def mark_active(modeladmin, request, queryset):
    updated = queryset.update(is_active=True)
    modeladmin.message_user(request, f"{updated} объект(ов) помечено(ы) как активные.")

class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 1
    autocomplete_fields = ["product"]
    fields = ["name", "message"]
    readonly_fields = ["created_at"]
    show_change_link = True

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3

@admin.register(Brand)
class BrandAdmin(TranslationAdmin):
    search_fields = ["name"]
    list_display = ["name"]
    search_help_text = "Brand name"

@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ["name"]


@admin.register(Product)
class ProductAdmin(TabbedTranslationAdmin):
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }

    list_display = ["name", "slug", "brand", "category", "price", "old_price", "quantity", "published", "published_at"]
    list_editable = ["price", "old_price", "quantity", "published"]
    search_fields = ["name", "slug", "brand__name", "price"]
    search_help_text = "Поиск по имени, бренду или цене"
    list_filter = ["brand", "category", "price", "published"]
    autocomplete_fields = ["brand"]
    inlines = [ProductImageInline, FeedbackInline]

    actions = ["make_published", "make_unpublished", "export_csv", "mark_active"]
    actions_on_top = True
    actions_on_bottom = False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("import-csv/", self.import_csv_view, name="products_import_csv"),
        ]
        return my_urls + urls

    def import_csv_view(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            file_data = csv_file.read()
            try:
                decoded_file = file_data.decode('utf-8-sig')
            except UnicodeDecodeError:
                decoded_file = file_data.decode('cp1251')

            io_string = io.StringIO(decoded_file)
            first_line = io_string.readline()
            io_string.seek(0)
            delimiter = ';' if ';' in first_line else ','
            reader = csv.DictReader(io_string, delimiter=delimiter)

            created_count = 0
            updated_count = 0

            for row in reader:
                brand_name = row.get("brand")
                brand = None
                if brand_name:
                    brand, _ = Brand.objects.get_or_create(name=brand_name)

                category_name = row.get("category")
                category = None
                if category_name:
                    category, _ = Category.objects.get_or_create(name=category_name)

                def clean_price(value):
                    if not value: return 0
                    return value.replace(" ", "").replace("\xa0", "").replace(",", ".")

                price = clean_price(row.get("price", "0"))
                old_price_raw = row.get("old_price")
                old_price = clean_price(old_price_raw) if old_price_raw else None

                specs_str = row.get("specifications")
                specifications = {}
                if specs_str:
                    try:
                        specifications = json.loads(specs_str)
                    except json.JSONDecodeError:
                        specifications = {}

                is_published = row.get("published", "False").lower() in ("true", "1", "yes")
                pub_at = timezone.now() if is_published else None

                product_data = {
                    "name": row["name"],
                    "slug": row.get("slug") if row.get("slug") else None,
                    "brand": brand,
                    "category": category,
                    "price": price,
                    "old_price": old_price,
                    "quantity": int(row.get("quantity", 0)),
                    "image": row.get("image", ""),
                    "specifications": specifications,
                    "published": is_published,
                    "published_at": pub_at
                }

                product_id = row.get("id")
                if product_id:
                    obj, created = Product.objects.update_or_create(id=product_id, defaults=product_data)
                    if created: created_count += 1
                    else: updated_count += 1
                else:
                    Product.objects.create(**product_data)
                    created_count += 1

            self.message_user(request, f"Готово! Создано: {created_count}, Обновлено: {updated_count} товаров.")
            return redirect("..")

        context = dict(self.admin_site.each_context(request))
        return render(request, "myapp/csv_import.html", context)

    @admin.action(description="Снять публикацию с выбранных")
    def make_unpublished(self, request, queryset):
        count = queryset.update(published=False, published_at=None)
        self.message_user(request, f"{count} товаров снято с публикации.")

    @admin.action(description="Отметить выбранные как опубликованные")
    def make_published(self, request, queryset):
        now = timezone.now()
        count = queryset.update(published=True, published_at=now)
        self.message_user(request, f"{count} товаров опубликовано.")

    @admin.action(description="Экспорт выбранных в CSV")
    def export_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=products.csv'
        writer = csv.writer(response)

        writer.writerow([
            "id", "name", "slug", "brand", "category",
            "price", "old_price", "quantity",
            "image", "specifications",
            "published", "published_at"
        ])

        for product in queryset.select_related("brand", "category"):
            writer.writerow([
                product.id,
                product.name,
                product.slug,
                product.brand.name if product.brand else "",
                product.category.name if product.category else "",
                product.price,
                product.old_price if product.old_price else "",
                product.quantity,
                product.image.name if product.image else "",
                json.dumps(product.specifications, ensure_ascii=False),
                product.published,
                product.published_at
            ])
        return response

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name","rating", "created_at", "message")
    fields = ("name","rating", "message", "product")
    list_filter = ("created_at","rating", "product")
    search_fields = ("name", "message")
    autocomplete_fields = ["product"]
    ordering = ("-created_at",)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'first_name', 'last_name', 'status', 'get_total_cost', 'email', 'phone', 'city', 'payment_method', 'paid', 'created', 'updated']
    list_filter = [ 'status', 'paid', 'created', 'updated', 'payment_method']
    list_editable = ['status', 'paid']
    inlines = [OrderItemInline]


@admin.register(Banner)
class BannerAdmin(TranslationAdmin):
    list_display = ["title", "is_active", "created_at"]
    list_editable = ["is_active"]

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'created_at']
    readonly_fields = ['name', 'email', 'message', 'created_at']
    search_fields = ['name', 'email', 'message']