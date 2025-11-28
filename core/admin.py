from django.contrib import admin
from .models import OfferProduct, Category, SubCategory, Product, ProductImage, Review, Wishlist

# OfferProduct
@admin.register(OfferProduct)
class OfferProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'product', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'desc']
    list_editable = ['is_active']

# Keep as is
admin.site.register(SubCategory)
admin.site.register(Category)

# ProductImage Inline
class ProductAdminImage(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'mark_price', 'discount_percent', 'category', 'subcategory']
    list_filter = ['category', 'subcategory', 'created_date']
    search_fields = ['name', 'desc']
    inlines = [ProductAdminImage]
    readonly_fields = ['price', 'created_date']
    
    # Organize fields nicely
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'subcategory', 'image')
        }),
        ('Pricing', {
            'fields': ('mark_price', 'discount_percent', 'price'),
            'description': 'Price is auto-calculated based on mark price and discount'
        }),
        ('Descriptions', {
            'fields': ('desc', 'description'),
            'description': '"desc" for product cards, "description" for detail page'
        }),
        ('Metadata', {
            'fields': ('created_date',),
            'classes': ('collapse',)
        })
    )

# Review Admin
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating', 'created_date']
    list_filter = ['rating', 'created_date', 'product']
    search_fields = ['user__username', 'product__name', 'feedback']
    readonly_fields = ['created_date']
    date_hierarchy = 'created_date'

# Blog Admins
from .models import BlogCategory, Tag, BlogPost, BlogComment

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ['name']

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'is_featured', 'views', 'created_at']
    list_filter = ['is_published', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'content']
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ['created_at', 'updated_at', 'views']
    filter_horizontal = ('tags',)
    date_hierarchy = 'created_at'

@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'is_approved']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['author__username', 'post__title', 'content']
    date_hierarchy = 'created_at'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'added_date']
    list_filter = ['added_date']
    search_fields = ['user__username', 'product__name']
    readonly_fields = ['added_date']
    date_hierarchy = 'added_date'