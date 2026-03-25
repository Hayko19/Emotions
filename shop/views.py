from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Category, Product, Order, OrderItem


def staff_required(view_func):
    """Decorator: only staff/superusers can access."""
    def check_staff(user):
        return user.is_active and user.is_staff
    return user_passes_test(check_staff, login_url='/admin/login/')(view_func)


def home(request):
    featured = Product.objects.filter(featured=True, available=True)[:6]
    categories = Category.objects.all()
    return render(request, 'shop/home.html', {
        'featured': featured,
        'categories': categories,
    })


def catalog(request):
    # Get view type: 'bouquet' or 'stem'
    current_type = request.GET.get('type', 'bouquet')

    from django.db.models import Count, Q
    if current_type == 'stem':
        categories = Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_by_stem=True, products__available=True))
        )
        products = Product.objects.filter(available=True, is_by_stem=True)
    else:
        categories = Category.objects.annotate(
            product_count=Count('products', filter=Q(products__is_by_stem=False, products__available=True))
        )
        products = Product.objects.filter(available=True, is_by_stem=False)

    category_slug = request.GET.get('category')
    current_category = None
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=current_category)

    sort = request.GET.get('sort', 'default')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')
    elif sort == 'newest':
        products = products.order_by('-created')

    return render(request, 'shop/catalog.html', {
        'categories': categories,
        'products': products,
        'current_category': current_category,
        'current_sort': sort,
        'current_type': current_type,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    variants = product.variants.filter(available=True) if product.is_by_stem else []
    related = Product.objects.filter(
        category=product.category, available=True
    ).exclude(id=product.id)[:4]
    return render(request, 'shop/product_detail.html', {
        'product': product,
        'variants': variants,
        'related': related,
    })


def cart_view(request):
    from .models import ProductVariant
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for key, item in cart.items():
        try:
            if '_' in key:
                product_id, variant_id = key.split('_')
                product = Product.objects.get(id=product_id)
                variant = ProductVariant.objects.get(id=variant_id)
                price = variant.price
                name = f"{product.name} ({variant.value})"
            else:
                product = Product.objects.get(id=key)
                variant = None
                price = product.price
                name = product.name

            item_total = price * item['quantity']
            total += item_total
            cart_items.append({
                'product': product,
                'variant': variant,
                'name': name,
                'price': price,
                'quantity': item['quantity'],
                'total': item_total,
                'key': key,
            })
        except (Product.DoesNotExist, ProductVariant.DoesNotExist, ValueError):
            continue

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })


def cart_add(request, product_id):
    from .models import ProductVariant
    product = get_object_or_404(Product, id=product_id, available=True)
    cart = request.session.get('cart', {})
    
    variant_id = request.POST.get('variant')
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)

    product_key = f"{product_id}_{variant.id}" if variant else str(product_id)
    quantity = int(request.POST.get('quantity', 1))

    if product_key in cart:
        cart[product_key]['quantity'] += quantity
    else:
        cart[product_key] = {
            'quantity': quantity,
            'price': str(variant.price) if variant else str(product.price),
        }

    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = sum(item['quantity'] for item in cart.values())
        return JsonResponse({'success': True, 'cart_count': cart_count})

    messages.success(request, f'«{product.name}» добавлен в корзину!')
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)


def cart_update(request, key):
    cart = request.session.get('cart', {})

    if key in cart:
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart[key]['quantity'] = quantity
        else:
            del cart[key]

        request.session['cart'] = cart
        request.session.modified = True

    return redirect('shop:cart')


def cart_remove(request, key):
    cart = request.session.get('cart', {})

    if key in cart:
        del cart[key]
        request.session['cart'] = cart
        request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart_count = sum(item['quantity'] for item in cart.values())
        return JsonResponse({'success': True, 'cart_count': cart_count})

    return redirect('shop:cart')


def checkout(request):
    from .models import ProductVariant
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, 'Ваша корзина пуста!')
        return redirect('shop:catalog')

    if request.method == 'POST':
        order = Order.objects.create(
            first_name=request.POST.get('first_name', ''),
            last_name=request.POST.get('last_name', ''),
            phone=request.POST.get('phone', ''),
            email=request.POST.get('email', ''),
            address=request.POST.get('address', ''),
            comment=request.POST.get('comment', ''),
        )

        total = 0
        for key, item in cart.items():
            try:
                if '_' in key:
                    product_id, variant_id = key.split('_')
                    product = Product.objects.get(id=product_id)
                    variant = ProductVariant.objects.get(id=variant_id)
                    price = variant.price
                else:
                    product = Product.objects.get(id=key)
                    variant = None
                    price = product.price

                item_total = price * item['quantity']
                total += item_total
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    variant=variant,
                    price=price,
                    quantity=item['quantity'],
                )
            except (Product.DoesNotExist, ProductVariant.DoesNotExist, ValueError):
                continue

        # Add delivery fee if applicable
        if total < 5000:
            total += 500
            
        order.total_price = total
        order.save()

        request.session['cart'] = {}
        request.session.modified = True

        return render(request, 'shop/order_success.html', {'order': order})

    cart_items = []
    total = 0
    for key, item in cart.items():
        try:
            if '_' in key:
                product_id, variant_id = key.split('_')
                product = Product.objects.get(id=product_id)
                variant = ProductVariant.objects.get(id=variant_id)
                price = variant.price
                name = f"{product.name} ({variant.value})"
            else:
                product = Product.objects.get(id=key)
                variant = None
                price = product.price
                name = product.name

            item_total = price * item['quantity']
            total += item_total
            cart_items.append({
                'product': product,
                'name': name,
                'price': price,
                'quantity': item['quantity'],
                'total': item_total,
            })
        except (Product.DoesNotExist, ProductVariant.DoesNotExist, ValueError):
            continue

    return render(request, 'shop/checkout.html', {
        'cart_items': cart_items,
        'total': total,
    })


@staff_required
def admin_dashboard(request):
    """Custom visual admin dashboard with shop statistics."""
    now = timezone.now()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Order stats
    total_orders = Order.objects.count()
    new_orders = Order.objects.filter(status='new').count()
    processing_orders = Order.objects.filter(status='processing').count()
    delivering_orders = Order.objects.filter(status='delivering').count()
    completed_orders = Order.objects.filter(status='completed').count()
    cancelled_orders = Order.objects.filter(status='cancelled').count()

    # Revenue
    total_revenue = Order.objects.filter(
        status__in=['completed', 'delivering', 'processing']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    revenue_today = Order.objects.filter(
        created__date=today,
        status__in=['new', 'processing', 'delivering', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    revenue_week = Order.objects.filter(
        created__gte=week_ago,
        status__in=['new', 'processing', 'delivering', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    revenue_month = Order.objects.filter(
        created__gte=month_ago,
        status__in=['new', 'processing', 'delivering', 'completed']
    ).aggregate(total=Sum('total_price'))['total'] or 0

    # Products stats
    total_products = Product.objects.count()
    available_products = Product.objects.filter(available=True).count()
    featured_products = Product.objects.filter(featured=True).count()
    total_categories = Category.objects.count()

    # Top selling products
    top_products = OrderItem.objects.values(
        'product__name', 'product__slug', 'product__price'
    ).annotate(
        total_sold=Sum('quantity'),
        order_count=Count('order', distinct=True)
    ).order_by('-total_sold')[:5]

    # Recent orders
    recent_orders = Order.objects.select_related().prefetch_related('items').order_by('-created')[:10]

    # Orders by day for last 7 days (chart data)
    orders_by_day = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        count = Order.objects.filter(created__date=day).count()
        rev = Order.objects.filter(
            created__date=day,
            status__in=['new', 'processing', 'delivering', 'completed']
        ).aggregate(total=Sum('total_price'))['total'] or 0
        orders_by_day.append({
            'day': day.strftime('%d.%m'),
            'count': count,
            'revenue': float(rev),
        })

    context = {
        'total_orders': total_orders,
        'new_orders': new_orders,
        'processing_orders': processing_orders,
        'delivering_orders': delivering_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        'total_revenue': total_revenue,
        'revenue_today': revenue_today,
        'revenue_week': revenue_week,
        'revenue_month': revenue_month,
        'total_products': total_products,
        'available_products': available_products,
        'featured_products': featured_products,
        'total_categories': total_categories,
        'top_products': top_products,
        'recent_orders': recent_orders,
        'orders_by_day': orders_by_day,
        'status_choices': Order.STATUS_CHOICES,
    }
    return render(request, 'shop/admin_dashboard.html', context)


@staff_required
def admin_order_update(request, order_id):
    """Update order status from admin dashboard."""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            messages.success(request, f'Статус заказа #{order.id} обновлён.')
    return redirect('shop:admin_dashboard')

