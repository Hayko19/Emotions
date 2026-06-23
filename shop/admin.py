from django.contrib import admin
from django.utils.html import format_html
from adminsortable2.admin import SortableAdminMixin
from .models import Category, Product, ProductVariant, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'slug', 'product_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    ordering = ['order']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Товаров'


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_by_stem', 'available', 'featured', 'image_preview']
    list_filter = ['available', 'is_by_stem', 'featured', 'category', 'created']
    list_editable = ['price', 'is_by_stem', 'available', 'featured']
    search_fields = ['name', 'description', 'composition']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['image_preview_large']
    inlines = [ProductVariantInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category')
        }),
        ('Описание', {
            'fields': ('description', 'composition')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'is_by_stem', 'available', 'featured')
        }),
        ('Изображения', {
            'fields': ('image', 'image_alt', 'image_preview_large')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:8px;" />',
                obj.image.url
            )
        return '—'
    image_preview.short_description = 'Фото'

    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width:300px;max-height:300px;border-radius:12px;" />',
                obj.image.url
            )
        return 'Нет изображения'
    image_preview_large.short_description = 'Предпросмотр'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'price', 'quantity', 'get_total']

    def get_total(self, obj):
        return f'{obj.get_total()} ₽'
    get_total.short_description = 'Сумма'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'phone', 'status', 'total_price', 'created']
    list_filter = ['status', 'created']
    list_editable = ['status']
    search_fields = ['first_name', 'last_name', 'phone', 'email', 'address']
    readonly_fields = ['created', 'updated', 'total_price']
    inlines = [OrderItemInline]

    fieldsets = (
        ('Клиент', {
            'fields': ('first_name', 'last_name', 'phone', 'email')
        }),
        ('Доставка', {
            'fields': ('address', 'comment')
        }),
        ('Статус', {
            'fields': ('status', 'total_price', 'created', 'updated')
        }),
    )
