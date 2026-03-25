"""
Script to populate the flower shop database with sample data.
Run: python manage.py shell < populate_data.py
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowershop.settings')
django.setup()

from shop.models import Category, Product

# Create categories
categories_data = [
    {'name': 'Розы', 'slug': 'rozy', 'description': 'Классические букеты из свежих роз', 'order': 1},
    {'name': 'Тюльпаны', 'slug': 'tulpany', 'description': 'Яркие весенние тюльпаны', 'order': 2},
    {'name': 'Смешанные букеты', 'slug': 'smeshannye', 'description': 'Авторские композиции из разных цветов', 'order': 3},
    {'name': 'Свадебные', 'slug': 'svadebnye', 'description': 'Элегантные свадебные букеты', 'order': 4},
    {'name': 'Подарочные наборы', 'slug': 'podarochnye', 'description': 'Букеты с шоколадом и подарками', 'order': 5},
]

categories = {}
for cat_data in categories_data:
    cat, created = Category.objects.get_or_create(
        slug=cat_data['slug'],
        defaults=cat_data
    )
    categories[cat.slug] = cat
    status = 'создана' if created else 'уже существует'
    print(f'  Категория "{cat.name}" — {status}')

# Create products
products_data = [
    {
        'category': 'rozy',
        'name': 'Букет "Алый закат"',
        'slug': 'alyj-zakat',
        'description': 'Роскошный букет из 25 алых роз. Идеален для романтического подарка.',
        'composition': '25 красных роз\nЗелень эвкалипта\nАтласная лента',
        'price': 4500,
        'available': True,
        'featured': True,
    },
    {
        'category': 'rozy',
        'name': 'Букет "Нежность"',
        'slug': 'nezhnost',
        'description': 'Нежный букет из розовых и белых роз.',
        'composition': '15 розовых роз\n10 белых роз\nГипсофила\nАтласная лента',
        'price': 5200,
        'available': True,
        'featured': True,
    },
    {
        'category': 'rozy',
        'name': 'Букет "Премиум"',
        'slug': 'premium',
        'description': 'Премиальный букет из 51 розы — незабываемый подарок.',
        'composition': '51 красная роза\nЗелень\nПремиальная упаковка',
        'price': 9800,
        'available': True,
        'featured': True,
    },
    {
        'category': 'tulpany',
        'name': 'Букет "Весна"',
        'slug': 'vesna',
        'description': 'Яркий букет из разноцветных тюльпанов — настроение весны.',
        'composition': '21 тюльпан разных цветов\nЗелень\nКрафтовая упаковка',
        'price': 3200,
        'available': True,
        'featured': True,
    },
    {
        'category': 'tulpany',
        'name': 'Букет "Солнечный"',
        'slug': 'solnechnyj',
        'description': 'Жёлтые тюльпаны — символ радости.',
        'composition': '15 жёлтых тюльпанов\nВеточки мимозы\nЛента',
        'price': 2800,
        'available': True,
        'featured': False,
    },
    {
        'category': 'smeshannye',
        'name': 'Букет "Лесная сказка"',
        'slug': 'lesnaya-skazka',
        'description': 'Авторская композиция из полевых цветов.',
        'composition': 'Ромашки\nЛаванда\nЭвкалипт\nСтатица\nЛьняная упаковка',
        'price': 3800,
        'available': True,
        'featured': True,
    },
    {
        'category': 'smeshannye',
        'name': 'Букет "Гармония"',
        'slug': 'garmoniya',
        'description': 'Гармоничное сочетание роз, лилий и хризантем.',
        'composition': '5 роз\n3 лилии\n5 хризантем\nГипсофила\nДекоративная зелень',
        'price': 4200,
        'available': True,
        'featured': True,
    },
    {
        'category': 'svadebnye',
        'name': 'Букет невесты "Элегант"',
        'slug': 'elegant',
        'description': 'Элегантный свадебный букет из белых пионов.',
        'composition': '9 белых пионов\nЭвкалипт\nШёлковая лента\nБрошь',
        'price': 6500,
        'available': True,
        'featured': False,
    },
    {
        'category': 'svadebnye',
        'name': 'Букет невесты "Романтика"',
        'slug': 'romantika',
        'description': 'Романтичный каскадный букет в пастельных тонах.',
        'composition': 'Пионовидные розы\nРанункулюсы\nФрезии\nЗелень',
        'price': 7800,
        'available': True,
        'featured': False,
    },
    {
        'category': 'podarochnye',
        'name': 'Набор "Сладкий сюрприз"',
        'slug': 'sladkij-sjurpriz',
        'description': 'Букет роз с бельгийским шоколадом.',
        'composition': '11 роз\nКоробка шоколада\nОткрытка\nПодарочная упаковка',
        'price': 5500,
        'available': True,
        'featured': False,
    },
]

for prod_data in products_data:
    cat_slug = prod_data.pop('category')
    cat = categories[cat_slug]
    product, created = Product.objects.get_or_create(
        slug=prod_data['slug'],
        defaults={**prod_data, 'category': cat}
    )
    status = 'создан' if created else 'уже существует'
    print(f'  Товар "{product.name}" — {status}')

print('\nГотово! Данные загружены.')
