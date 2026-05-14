# myapp/translation.py
from modeltranslation.translator import register, TranslationOptions
from .models import Category, Brand, Product, Banner


@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Brand)
class BrandTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Product)
class ProductTranslationOptions(TranslationOptions):
    fields = ('name',)


@register(Banner)
class BannerTranslationOptions(TranslationOptions):
    fields = ('title', 'text',)