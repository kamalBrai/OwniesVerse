from django.db import models
from django_ckeditor_5.fields import CKEditor5Field
from accounts.models import CustomUserModel
from django.conf import settings
from django.utils.text import slugify


class OfferProduct(models.Model):
    title = models.CharField(max_length=200)
    desc = models.TextField()
    image = models.ImageField(upload_to='offers/')
    is_active = models.BooleanField(default=True)
    
    product = models.ForeignKey(
        'Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offers',
        help_text="Link this offer to a specific product"
    )

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title
    

class SubCategory(models.Model):
    title = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    desc = CKEditor5Field('Text', config_name='extends', help_text="Short description for product listings")
    
    # ADD THIS - Full description for product detail page
    description = CKEditor5Field('Description', config_name='extends', blank=True, null=True, 
                                   help_text="Full detailed description for product detail page")
    
    image = models.ImageField(upload_to="images")
    mark_price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=4, decimal_places=2)
    price = models.DecimalField(max_digits=8, decimal_places=2, editable=False)
    created_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.price = self.mark_price * (1 - self.discount_percent / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

# Multiple image for same product
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="images")

    def __str__(self):
        return self.product.name
    

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    feedback = models.TextField()
    created_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}★)"


# Blog Models (keep as is)
class BlogCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Blog Categories"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True)
    excerpt = models.TextField(max_length=300, help_text="Short description")
    content = models.TextField()
    views = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def comment_count(self):
        return self.blogcomment_set.count()
    
    def __str__(self):
        return self.title


class BlogComment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
class Wishlist(models.Model):
    user = models.ForeignKey(CustomUserModel, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate wishlist entries
        ordering = ['-added_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.product.name}"