from django.shortcuts import render, get_object_or_404, redirect
from .models import OfferProduct,Category,Product,SubCategory, BlogPost, BlogCategory, Tag, BlogComment , Wishlist
from django.db.models import Count, Prefetch, Avg
from django.core.paginator import Paginator
from .forms import ReviewForm
from django.contrib.auth.decorators import login_required
from cart.cart import Cart
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse

# Create your views here.

def index(request):
    # Get offers and categories with related products
    offer = OfferProduct.objects.filter(is_active=True).select_related('product')
    category = Category.objects.annotate(
        subcategory_count=Count('subcategory')
    ).prefetch_related(
        Prefetch(
            'subcategory_set',
            queryset=SubCategory.objects.annotate(product_count=Count('product'))
        )
    )
    
    # Get recommended products (latest 12 products for the carousel)
    recommended_products = Product.objects.all().order_by('-id')[:12]

    # Get filter parameters
    subcategory_id = request.GET.get('subcategory')
    min_price = request.GET.get('min')
    max_price = request.GET.get('max')
    
    # Start with all products
    product = Product.objects.all()
    
    # Apply filters based on what's provided
    if subcategory_id:
        product = product.filter(subcategory=subcategory_id)
    
    # Apply price filter if both min and max are provided
    if min_price and max_price:
        try:
            product = product.filter(price__range=(float(min_price), float(max_price)))
        except ValueError:
            pass  # Invalid price values, ignore filter
    elif min_price:
        # Only min price provided
        try:
            product = product.filter(price__gte=float(min_price))
        except ValueError:
            pass
    elif max_price:
        # Only max price provided
        try:
            product = product.filter(price__lte=float(max_price))
        except ValueError:
            pass

    # Pagination - changed from 2 to 9 products per page (you can adjust this)
    paginator = Paginator(product, 9)
    page_n = request.GET.get('page')
    data = paginator.get_page(page_n)
    total = data.paginator.num_pages

    context = {
        'offer': offer,
        'category': category,
        'product': data,  # Changed to use paginated data
        'data': data,
        'num': [i+1 for i in range(total)],
        'recommended_products': recommended_products,  # Added for carousel
    }

    return render(request, 'core/index.html', context)



def blog(request):
    # Get all blog posts ordered by creation date
    posts_list = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    
    # Filter by category if provided
    category_id = request.GET.get('category')
    if category_id:
        posts_list = posts_list.filter(category_id=category_id)
    
    # Filter by tag if provided
    tag_slug = request.GET.get('tag')
    if tag_slug:
        posts_list = posts_list.filter(tags__slug=tag_slug)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts_list = posts_list.filter(
            title__icontains=search_query
        ) | posts_list.filter(
            content__icontains=search_query
        )
    
    # Pagination
    paginator = Paginator(posts_list, 6)  # Show 6 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)
    
    # Get blog categories with post count
    blog_categories = BlogCategory.objects.annotate(
        post_count=Count('blogpost')
    )
    
    # Get recent posts (last 5)
    recent_posts = BlogPost.objects.filter(
        is_published=True
    ).order_by('-created_at')[:5]
    
    # Get featured posts (last 3)
    featured_posts = BlogPost.objects.filter(
        is_published=True,
        is_featured=True
    ).order_by('-created_at')[:3]
    
    # Get popular tags
    popular_tags = Tag.objects.annotate(
        post_count=Count('blogpost')
    ).order_by('-post_count')[:10]
    
    context = {
        'posts': posts,
        'blog_categories': blog_categories,
        'recent_posts': recent_posts,
        'featured_posts': featured_posts,
        'popular_tags': popular_tags,
    }
    
    return render(request, 'core/blog.html', context)



def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    post.views += 1
    post.save(update_fields=['views'])
    
    context = {
        'post': post,
    }
    return render(request, 'core/blog_detail.html', context)

def about_us(request):
    return render(request,'core/about_us.html')

def contact(request):
    if request.method == 'POST':
        # Optional: add email sending later
        messages.success(request, 'Thank you! We\'ll reply within 1 hour.')
    return render(request, 'core/contact.html')

def product_detail(request, id):
    """
    Display product details with dynamic reviews and ratings.
    Handle review submission with authentication and duplicate checks.
    """
    product = get_object_or_404(Product, id=id)
    all_reviews = product.reviews.all()

    # --- 1. Dynamic Review Calculation ---
    review_stats = all_reviews.aggregate(
        average_rating=Avg('rating'), 
        review_count=Count('id')
    )
    
    # Extract calculated values with proper defaults
    average_rating = review_stats.get('average_rating') or 0
    review_count = review_stats.get('review_count', 0)
    
    # Round average rating for cleaner display (e.g., 4.5 instead of 4.523)
    if average_rating:
        average_rating = round(average_rating, 1)
    
    # Calculate star distribution for visual display
    full_stars = int(average_rating)
    half_star = 1 if (average_rating - full_stars) >= 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    # ------------------------------------

    form = ReviewForm()
    
    if request.method == 'POST':
        
        # --- 2. Authentication and Submission Guard ---
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to submit a review.")
            return redirect('log_in')
        
        # Check if user has already reviewed the product
        if all_reviews.filter(user=request.user).exists():
            messages.warning(request, "You have already reviewed this product.")
            return redirect("product_detail", id=product.id)
        
        form = ReviewForm(data=request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, "Your review has been successfully posted!")
            
            # PRG Pattern: Always redirect after a POST
            return redirect("product_detail", id=product.id)
        else:
            # Handle form validation errors
            messages.error(request, "Please correct the errors in your review.")
    # ---------------------------------------------
            
    context = {
        "product": product,
        'form': form,
        'reviews': all_reviews,
        'range': range(1, 6),
        
        # --- Review Statistics ---
        'review_count': review_count,
        'average_rating': average_rating,
        
        # --- Star Display Helper ---
        'full_stars': range(full_stars),
        'half_star': half_star,
        'empty_stars': range(empty_stars),
        # -------------------------
    }

    return render(request, 'core/product_detail.html', context)

# search funcitonality
def search(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.none()  # empty by default
    
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(desc__icontains=query) |
            Q(category__title__icontains=query) |
            Q(subcategory__title__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'products': products,
        'count': products.count(),
    }
    return render(request, 'core/search.html', context)



'''  Cart Details  '''
@login_required(login_url="log_in")
def cart_add(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("index")


@login_required(login_url="log_in")
def item_clear(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.remove(product)
    return redirect("cart_detail")


@login_required(login_url="log_in")
def item_increment(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.add(product=product)
    return redirect("cart_detail")


@login_required(login_url="log_in")
def item_decrement(request, id):
    cart = Cart(request)
    product = Product.objects.get(id=id)
    cart.decrement(product=product)
    return redirect("cart_detail")


@login_required(login_url="log_in")
def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect("cart_detail")


@login_required(login_url="log_in")
def cart_detail(request):
    return render(request, 'core/cart.html')


@login_required
def wishlist(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    
    context = {
        'wishlist_items': wishlist_items,
        'wishlist_count': wishlist_items.count()
    }
    return render(request, 'core/wishlist.html', context)


@login_required
def add_to_wishlist(request, product_id):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    # Check if already in wishlist
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product
    )
    
    if created:
        messages.success(request, f"{product.name} added to your wishlist!")
    else:
        messages.info(request, f"{product.name} is already in your wishlist.")
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'created': created,
            'message': f"{product.name} added to wishlist!" if created else "Already in wishlist"
        })
    
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))


@login_required
def remove_from_wishlist(request, product_id):
    """Remove product from wishlist"""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        messages.success(request, f"{product.name} removed from your wishlist.")
    except Wishlist.DoesNotExist:
        messages.error(request, "Product not found in your wishlist.")
    
    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': 'Removed from wishlist'
        })
    
    return redirect('wishlist')


@login_required
def toggle_wishlist(request, product_id):
    """Toggle product in/out of wishlist (for heart icon)"""
    product = get_object_or_404(Product, id=product_id)
    
    try:
        wishlist_item = Wishlist.objects.get(user=request.user, product=product)
        wishlist_item.delete()
        in_wishlist = False
        message = "Removed from wishlist"
    except Wishlist.DoesNotExist:
        Wishlist.objects.create(user=request.user, product=product)
        in_wishlist = True
        message = "Added to wishlist"
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'in_wishlist': in_wishlist,
            'message': message
        })
    
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))