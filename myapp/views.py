from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .form import FeedbackForm, CartAddProductForm, OrderCreateForm, ContactForm
from django.views.decorators.http import require_POST
from django.db.models import Q, F, Avg
from .models import Feedback, Product, Brand, OrderItem, Category, Order, Banner
from .cart import Cart
from .wishlist import Wishlist
from django.contrib.auth.decorators import login_required
from users.forms import UserUpdateForm
from django.contrib import messages

def index(request):
    products_list = Product.objects.filter(published=True).annotate(avg_rating=Avg('feedback__rating'))
    brands = Brand.objects.all()
    categories = Category.objects.all()
    banners = Banner.objects.filter(is_active=True).order_by('-created_at')

    # 1. пошук
    query = request.GET.get('query')
    if query:
        products_list = products_list.filter(
            Q(name__icontains=query) | Q(brand__name__icontains=query)
        )

    # 2. Фильтр по брендам
    selected_brand_ids = request.GET.getlist('brand')
    if selected_brand_ids:
        selected_brand_ids = [int(id) for id in selected_brand_ids if id.isdigit()]
        products_list = products_list.filter(brand__id__in=selected_brand_ids)

    # 3. Фильтр по категоріям
    selected_category_ids = request.GET.getlist('category')
    if selected_category_ids:
        selected_category_ids = [int(id) for id in selected_category_ids if id.isdigit()]
        products_list = products_list.filter(category__id__in=selected_category_ids)

    # 4. По Скидкам
    on_sale = request.GET.get('on_sale')
    if on_sale == 'true':
        products_list = products_list.filter(old_price__isnull=False, old_price__gt=F('price'))

    # 5. Рейтинг
    rating_filter = request.GET.get('rating')
    if rating_filter and rating_filter.isdigit():
        products_list = products_list.filter(avg_rating__gte=int(rating_filter))

        # ЛОГИКА ДЛЯ ДИНАМИЧЕСКИХ ХАРАКТЕРИСТИК (JSON)
        # А. Сначала собираем все возможные ключи и значения из УЖЕ отфильтрованных товаров (или всех)
    available_specs = {}

        # Лучше собирать спецификации ДО применения фильтров по самим спецификациям,
        # но ПОСЛЕ фильтров бренда/категории, чтобы не показывать лишнего.
    for product in products_list:
        if product.specifications:
            for key, value in product.specifications.items():
                if key not in available_specs:
                    available_specs[key] = set()

                    # ИСПРАВЛЕНИЕ: Проверяем, является ли значение списком
                if isinstance(value, list):
                        # Если в JSON хранится массив ["Для телефонів", "Для планшетів"]
                    available_specs[key].update(value)
                else:
                        # Если это обычная строка "Білий"
                    available_specs[key].add(value)

    selected_specs = {}

    for param, values in request.GET.lists():
        if param.startswith('spec_'):
            # Убираем префикс "spec_", чтобы получить реальный ключ JSON (например, "Цвет")
            real_key = param.replace('spec_', '')
            selected_specs[real_key] = values
            # Фильтруем QuerySet
            # Синтаксис: specifications__Ключ__in=[список_значений]
            filter_kwargs = {f"specifications__{real_key}__in": values}
            products_list = products_list.filter(**filter_kwargs)

    # 6. Сортировка
    sort_by = request.GET.get('sort_by')
    if sort_by == 'price_asc':
        products_list = products_list.order_by('price')
    elif sort_by == 'price_desc':
        products_list = products_list.order_by('-price')
    else:
        products_list = products_list.order_by('-published_at', '-id')

    # Пагинация
    paginator = Paginator(products_list, 9)
    page_number = request.GET.get('page')
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    wishlist = Wishlist(request)
    wishlist_product_ids = wishlist.wishlist

    context = {
        'products': products,
        'brands': brands,
        'categories': categories,
        'selected_brand_ids': selected_brand_ids,
        'selected_category_ids': selected_category_ids,
        'current_sort': sort_by,
        'query': query,
        'on_sale_checked': on_sale == 'true',
        'rating_filter': rating_filter,
        'banners': banners,
        'wishlist_product_ids': wishlist_product_ids,

        # 👇 Передаем новые данные в шаблон
        'available_specs': available_specs,  # Все доступные опции (для рендера меню)
        'selected_specs': selected_specs,  # То, что выбрал юзер (для галочек)
    }
    return render(request, 'myapp/index.html', context)

def wishlist_add(request, product_id):
    wishlist = Wishlist(request)
    product = get_object_or_404(Product, id=product_id)
    wishlist.add(product)
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def wishlist_remove(request, product_id):
    wishlist = Wishlist(request)
    product = get_object_or_404(Product, id=product_id)
    wishlist.remove(product)
    return redirect(request.META.get('HTTP_REFERER', 'wishlist_view'))

def wishlist_view(request):
    wishlist = Wishlist(request)
    return render(request, 'myapp/wishlist.html', {'wishlist': wishlist})

def about(request):
    breadcrumbs = [
        {'name': _('Главная'), 'url': reverse('home')},
        {'name': _('О нас'), 'url': reverse('about')},
    ]
    context = {'breadcrumbs': breadcrumbs}
    return render(request, 'myapp/about.html', context)

def contact(request):
    breadcrumbs = [
        {'name': _('Главная'), 'url': reverse('home')},
        {'name': _('Контакты'), 'url': reverse('contact')},
    ]

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Ваше сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.'))
            return redirect('contact')
    else:
        # Если пользователь авторизован, предзаполняем форму его данными
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'name': request.user.get_full_name() or request.user.username,
                'email': request.user.email
            }
        form = ContactForm(initial=initial_data)

    context = {
        'breadcrumbs': breadcrumbs,
        'form': form
    }
    return render(request, 'myapp/contact.html', context)


def product_detail(request, slug):

    product = get_object_or_404(Product, slug=slug, published=True)

    reviews = product.feedback.all().order_by('-created_at')

    similar_products = Product.objects.filter(category=product.category, published=True).exclude(id=product.id)[:4]

    cart_product_form = CartAddProductForm()

    wishlist = Wishlist(request)
    wishlist_product_ids = wishlist.wishlist

    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            new_review = form.save(commit=False)
            new_review.product = product
            new_review.save()

            return redirect('product_detail', slug=product.slug)
    else:
        form = FeedbackForm()

    breadcrumbs = [
        {'name': _('Главная'), 'url': reverse('home')},
        {'name': product.category.name,
         'url': f"{reverse('home')}?category={product.category.id}"} if product.category else None,
        {'name': product.name, 'url': reverse('product_detail', kwargs={'slug': product.slug})},
    ]

    breadcrumbs = [b for b in breadcrumbs if b]

    context = {
        'product': product,
        'reviews': reviews,
        'similar_products': similar_products,
        'form': form,
        'cart_product_form': cart_product_form,
        'breadcrumbs': breadcrumbs,
        'wishlist_product_ids': wishlist_product_ids,
    }

    return render(request, 'myapp/show.html', context)

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
    return redirect('favorites')

@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('favorites')


def favorites(request):
    cart = Cart(request)

    breadcrumbs = [
        {'name': _('Главная'), 'url': reverse('home')},
        {'name': _('Корзина'), 'url': reverse('favorites')},
    ]

    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={
            'quantity': item['quantity'],
            'override': True})

    return render(request, 'myapp/favorites.html', {'cart': cart, 'breadcrumbs': breadcrumbs})


def order(request):
    cart = Cart(request)

    breadcrumbs = [
        {'name': _('Главная'), 'url': reverse('home')},
        {'name': _('Корзина'), 'url': reverse('favorites')},
        {'name': _('Оформление заказа'), 'url': reverse('order')},
    ]

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():

            for item in cart:
                product = item['product']
                if item['quantity'] > product.quantity:
                    form.add_error(None, f"Извините, товара '{product.name}' осталось всего {product.quantity} шт.")
                    return render(request, 'myapp/order.html', {'cart': cart, 'form': form})


            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()


            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])

                product = item['product']
                product.quantity -= item['quantity']
                product.save()
            cart.clear()
            return render(request, 'myapp/created.html', {'order': order})
    else:

        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'email': request.user.email,
            }
        form = OrderCreateForm(initial=initial_data)

    return render(request, 'myapp/order.html', {'cart': cart, 'form': form, 'breadcrumbs': breadcrumbs})


def handler404(request, exception):
    return render(request, 'myapp/404.html', status=404)

def handler400(request, exception):

    return render(request, 'myapp/400.html', status=400)

def handler405(request, exception):

    return render(request, 'myapp/405.html', status=405)

def handler500(request):

    return render(request, 'myapp/500.html', status=500)


def feedback_view(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            #return FeedbackForm('thanks')
            return redirect('/ru/thanks/')
    else:
        form = FeedbackForm()
    return render(request, 'myapp/feedback.html', {'form': form})


@login_required
def profile(request):

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user_form.save()
            messages.success(request, _('Ваш профиль был успешно обновлен!'))
            return redirect('profile')
    else:

        user_form = UserUpdateForm(instance=request.user)


    orders = Order.objects.filter(user=request.user).order_by('-created')

    breadcrumbs = [
        {'name': _('Главная'), 'url': reverse('home')},
        {'name': _('Мои заказы'), 'url': reverse('profile')},
    ]

    context = {
        'orders': orders,
        'user_form': user_form,
        'breadcrumbs': breadcrumbs
    }

    return render(request, 'myapp/profile.html', context)