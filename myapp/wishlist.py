from django.conf import settings
from .models import Product

class Wishlist:
    def __init__(self, request):
        """
        Инициализируем список желаний
        """
        self.session = request.session
        wishlist = self.session.get(settings.WISHLIST_SESSION_ID)
        if not wishlist:
            # Сохраняем пустой список в сессии
            wishlist = self.session[settings.WISHLIST_SESSION_ID] = []
        self.wishlist = wishlist

    def add(self, product):
        """
        Добавить продукт в список желаний
        """
        product_id = product.id
        if product_id not in self.wishlist:
            self.wishlist.append(product_id)
            self.save()

    def remove(self, product):
        """
        Удалить продукт из списка желаний
        """
        product_id = product.id
        if product_id in self.wishlist:
            self.wishlist.remove(product_id)
            self.save()

    def save(self):
        # Помечаем сессию как "измененную", чтобы Django сохранил её
        self.session.modified = True

    def __iter__(self):
        """
        Перебираем товары в списке желаний и получаем их из базы данных
        """
        product_ids = self.wishlist
        products = Product.objects.filter(id__in=product_ids)
        for product in products:
            yield product

    def __len__(self):
        """
        Считаем количество товаров
        """
        return len(self.wishlist)

    def clear(self):
        """
        Очистить список желаний
        """
        del self.session[settings.WISHLIST_SESSION_ID]
        self.save()