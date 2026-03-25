import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowershop.settings')
django.setup()

from shop.models import Product, ProductVariant, Category

def run():
    cat, _ = Category.objects.get_or_create(name="Розы", slug="roses")
    prod, Created = Product.objects.get_or_create(
        category=cat,
        name="Роза Эквадор (Кружево)",
        slug="rose-ecuador-lace",
        defaults={
            'description': "Премиум роза с крупным бутоном",
            'price': 150,
            'is_by_stem': True,
            'composition': "Роза поштучно",
        }
    )
    # Always ensure variants exist
    ProductVariant.objects.filter(product=prod).delete()
    ProductVariant.objects.create(product=prod, name="Длина стебля", value="50 см", price=150)
    ProductVariant.objects.create(product=prod, name="Длина стебля", value="60 см", price=180)
    ProductVariant.objects.create(product=prod, name="Длина стебля", value="70 см", price=210)
    print("Test variants created successfully for Product id:", prod.id)

if __name__ == '__main__':
    run()
