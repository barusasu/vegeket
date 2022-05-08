from re import template
from django.shortcuts import render, redirect
from django.conf import settings
from django.views.generic import View, ListView
from base.models import Item
from collections import OrderedDict

class CartListView(ListView):
    model = Item
    template_name = 'pages/cart.html'

    def get_queryset(self):
        cart = self.request.session.get('cart', None)       # sessionにcartのキーの情報を返す。なければNoneを返す
        if cart is None or len(cart) == 0:
            return redirect('/')                            # トップページに返す
        self.queryset = []
        self.total = 0
        for item_pk, quantity in cart['items'].items():     # AddCartView()でcartに辞書が追加されている。.items()でキーとバリューを取り出す。
            obj = Item.objects.get(pk=item_pk)
            obj.quantity = quantity                         # Modelには追加していない。templatesで使うための一時的な格納先。
            obj.subtotal = int(obj.price * quantity)        # Modelには追加していない。templatesで使うための一時的な格納先。
            self.queryset.append(obj)
            self.total += obj.subtotal
        self.tax_included_total = int(self.total * (settings.TAX_RATE + 1))
        cart['total'] = self.total
        cart['tax_included_total'] = self.tax_included_total
        self.request.session['cart'] = cart
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)        # object_listのデータを取得
        try:
            context['total'] = self.total
            context['tax_included_total'] = self.tax_included_total
        except Exception:
            pass
        return context


class AddCartView(View):
    def post(self, request):
        item_pk = request.POST.get('item_pk')
        quantity = int(request.POST.get('quantity'))
        cart = request.session.get('cart', None)
        if cart is None or len(cart) == 0:
            items = OrderedDict()
            cart = {'items': items}
        if item_pk in cart['items']:
            cart['items'][item_pk] += quantity
        else:
            cart['items'][item_pk] = quantity
        request.session['cart'] = cart
        return redirect('/cart/')


def remove_from_cart(request, pk):
    cart = request.session.get('cart', None)
    if cart is not None:
        del cart['items'][pk]
        request.session['cart'] = cart
    return redirect('/cart/')