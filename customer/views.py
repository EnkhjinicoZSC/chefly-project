import json
from django.shortcuts import render, redirect
from django.views import View
from django.db.models import Q
from django.core.mail import send_mail
from .models import MenuItem, Category, RequestModel

class Index(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/index.html')
    
class About(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/about.html')
    
class Request(View):
    def get(self, request, *args, **kwargs):
        # get every item from each category
        westerns = MenuItem.objects.filter(category__name__contains='Western')
        americans = MenuItem.objects.filter(category__name__contains='American')
        italians = MenuItem.objects.filter(category__name__contains='Italian')
        mongolians = MenuItem.objects.filter(category__name__contains='Mongolian')
        frenchs = MenuItem.objects.filter(category__name__contains='French')
        turkishes = MenuItem.objects.filter(category__name__contains='Turkish')

        # combine data into a single list
        cuisines = list(westerns) + list(americans) + list(italians) + list(mongolians) + list(frenchs) + list(turkishes)
        
        
        # pass into context
        context = {
            'cuisines': cuisines,
        }
        # render the template
        return render(request, 'customer/order.html', context)
    
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip')
        
        order_items = {
            'items': []
        }
        items = request.POST.getlist('items[]')
         
        for item in items:
            menu_item = MenuItem.objects.get(pk__contains=int(item))
            item_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price
            }
            
            order_items['items'].append(item_data)

            price = 0
            item_ids = []
            
        for item in order_items['items']:
            price += item['price']
            item_ids.append(item['id'])
        
        order = RequestModel.objects.create(
            price=price,
            name=name,
            email=email,
            street=street,
            city=city,
            state=state,
            zip_code=zip_code
        )
        
        order.items.add(*item_ids)
        # after everything is done, send confirmation
        body = ('Thank you for your request! Your request is sent and will be responded by chefs soon!\n'
                f'Your total: {price}\n'
                'Thank you again for your request!')
        
        send_mail(
            'Thank you for your request!',
            body,
            'emaple@example,com',
            [email], 
            fail_silently=False
        )
        
        context = { 
            'items': order_items['items'],
            'price': price 
        }
        
        return redirect('order-confirmation', pk=order.pk)
    
class OrderConfirmation(View):
    def get(self, request, pk, *args, **kwargs):
        order = RequestModel.objects.get(pk=pk)

        context = {
            'pk': order.pk,
            'items': order.items,
            'price': order.price,
        }

        return render(request, 'customer/order_confirmation.html', context)

    def post(self, request, pk, *args, **kwargs):
        data = json.loads(request.body)

        if data['isPaid']:
            order = RequestModel.objects.get(pk=pk)
            order.is_paid = True
            order.save()

        return redirect('payment-confirmation')


class OrderPayConfirmation(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'customer/order_pay_confirmation.html')
    
    
class Menu(View):
    def get(self, request, *args, **kwargs):
        menu_items = MenuItem.objects.all()

        context = {
            'menu_items': menu_items
        }

        return render(request, 'customer/menu.html', context)


class MenuSearch(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get("q")

        menu_items = MenuItem.objects.filter(
            Q(name__icontains=query) |
            Q(price__icontains=query) |
            Q(description__icontains=query)
        )

        context = {
            'menu_items': menu_items
        }

        return render(request, 'customer/menu.html', context)