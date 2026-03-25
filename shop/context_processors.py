def cart_context(request):
    """Add cart item count to all templates."""
    cart = request.session.get('cart', {})
    cart_count = sum(item.get('quantity', 0) for item in cart.values())
    cart_total = sum(
        float(item.get('price', 0)) * item.get('quantity', 0)
        for item in cart.values()
    )
    return {
        'cart_count': cart_count,
        'cart_total': cart_total,
    }
