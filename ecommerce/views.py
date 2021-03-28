from django.shortcuts import render, HttpResponse, redirect, \
    get_object_or_404, reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm
from django.views.decorators.csrf import csrf_exempt
from .models import Product, Order, LineItem
from .forms import CartForm, CheckoutForm
from . import cart     

# Create your views here.
@login_required(login_url='/accounts/login/')
def index(request):
    all_products = Product.objects.all()
    return render(request, "ecommerce/index.html", {
                                    'all_products': all_products,
                                    })


def show_product(request, product_id, product_slug):
    product = get_object_or_404(Product, 
                                id=product_id,
                                slug=product_slug)

    if request.method == 'POST':
        form = CartForm(request, request.POST)
        if form.is_valid():
            request.form_data = form.cleaned_data
            cart.add_item_to_cart(request)
            return redirect('show_cart')

    form = CartForm(request, initial={'product_id': product.id})
    return render(request, 'ecommerce/product_detail.html', {
                                            'product': product,
                                            'form': form,
                                            })


def show_cart(request):

    if request.method == 'POST':
        if request.POST.get('submit') == 'Update':
            cart.update_item(request)
        if request.POST.get('submit') == 'Remove':
            cart.remove_item(request)

    cart_items = cart.get_all_cart_items(request)
    cart_subtotal = cart.subtotal(request)
    return render(request, 'ecommerce/cart.html', {
                                            'cart_items': cart_items,
                                            'cart_subtotal': cart_subtotal,
                                            })


def search_results(request):

    if 'product' in request.GET and request.GET["product"]:
        search_term = request.GET.get("product")
        searched_articles = Article.search_by_title(search_term)
        message = f"{search_term}"

        return render(request, 'all-news/search.html',{"message":message,"articles": searched_articles})

    else:
        message = "You haven't searched for any term"
        return render(request, 'all-news/search.html',{"message":message})


def checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            o = Order(
                name = cleaned_data.get('name'),
                email = cleaned_data.get('email'),
                postal_code = cleaned_data.get('postal_code'),
                address = cleaned_data.get('address'),
            )
            o.save()

            all_items = cart.get_all_cart_items(request)
            for cart_item in all_items:
                li = LineItem(
                    product_id = cart_item.product_id,
                    price = cart_item.price,
                    quantity = cart_item.quantity,
                    order_id = o.id
                )

                li.save()

            cart.clear(request)

            request.session['order_id'] = o.id
            return redirect('process_payment')

            messages.add_message(request, messages.INFO, 'Order Placed!')
            return redirect('checkout')


    else:
        form = CheckoutForm()
        return render(request, 'ecommerce/checkout.html', {'form': form})
    
def process_payment(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    host = request.get_host()
    
    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': '%2f' % order.total_cost().quantize(
            Decimal('.01')),
        'item_name': 'Order{}.format(order.id)',
        'invoice': str(order_id),
        'currency_code': 'USD',
        'notify_url': 'https://{}{}'.format(host,
                                            reverse('paypal-ipn')),
        'return_url': 'https://{}{}'.format(host,
                                            reverse('payment_done')),
        'cancel_return': 'https://{}{}'.format(host,
                                               reverse('payment_cancelled')),
        
    }
    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'blog/process_payment.html', {'order': order, 'form':form})  

@csrf_exempt
def payment_done(request):
    return render(request, 'blog/payment_done.html')

@csrf_exempt
def payment_cancelled(request):
    return render(request, 'blog/payment_cancelled')  