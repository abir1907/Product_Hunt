from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Vote
from django.utils import timezone


# Create your views here.

def home(request):
    products = Product.objects.order_by('id')
    votes = []
    if request.user.is_authenticated:
        user_votes = Vote.objects.filter(hunter=request.user).values('product_id')
        for user in user_votes:
            votes.append(user['product_id'])
    return render(request, 'products/home.html', {'products': products, 'votes': votes})


@login_required(login_url='/accounts/login')
def create(request):
    if request.method == 'POST':
        if request.POST['title'] and request.POST['body'] and request.POST['url'] and request.FILES['icon'] and \
                request.FILES['image']:
            product = Product()
            product.title = request.POST['title']
            product.body = request.POST['body']
            if request.POST['url'].startswith("http://") or request.POST['url'].startswith("https://"):
                product.url = request.POST['url']
            else:
                product.url = "http://" + request.POST['url']
            product.icon = request.FILES['icon']
            product.image = request.FILES['image']
            product.pub_date = timezone.datetime.now()
            product.hunter = request.user
            product.save()
            return redirect('detail', product.id)
        else:
            return render(request, 'products/create.html', {'error': 'All fields are required'})
    else:
        return render(request, 'products/create.html')


def detail(request, product_id):
    votes = []
    if request.user.is_authenticated:
        user_votes = Vote.objects.filter(hunter=request.user).values('product_id')
        for user in user_votes:
            votes.append(user['product_id'])
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'products/detail.html', {'product': product, 'votes': votes})


@login_required(login_url='/accounts/login')
def upvote(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        product.votes_total += 1
        product.save()
        vote = Vote()
        vote.product = product
        vote.hunter = request.user
        vote.save()
        return redirect('detail', product_id)
