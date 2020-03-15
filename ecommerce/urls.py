from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<product_id>\d+)/(?P<product_slug>[-\w]+)/$',views.show_product, name='product_detail'),
    url(r'^cart/', views.show_cart, name='show_cart'),
    url(r'^checkout/', views.checkout, name='checkout'),
    url(r'^process-payment/', views.process_payment, name='process_payment'),
    url(r'^payment-done/', views.payment_done, name='payment_done'),
    url(r'^payment-cancelled/', views.payment_cancelled, name='payment_cancelled'),
]
if settings.DEBUG:
    urlpatterns+=static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)






    # url(r'(product/<int:product_id>/<slug:product_slug>\d+)/$',views.show_product, name='product_detail'),
