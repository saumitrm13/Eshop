from django.shortcuts import render,redirect,HttpResponse,HttpResponseRedirect
from django.contrib.auth.hashers import make_password,check_password
from .models.customer import  Customer
from django.views import View
from .models.category import Category
from .models.product import Product
from .models.orders import Order



class Signup(View):
    def get(self,request):
        return render(request, 'signup.html')
    def post(self,request):
        postData = request.POST
        first_name = postData.get('firstname')
        last_name = postData.get('lastname')
        phone = postData.get('phone')
        email = postData.get('email')
        password = postData.get('password')
        value = {
            'first_name': first_name,
            'last_name': last_name,
            'phone': phone,
            'email': email
        }
        error_message = None
        customer = Customer(first_name=first_name, last_name=last_name, phone=phone, email=email, password=password)
        error_message = self.validatecustomer(customer)

        # saving
        if not error_message:
            customer.password = make_password(customer.password)
            customer.register()
            return redirect('homepage')

        else:
            data = {
                'error': error_message,
                'values': value
            }
            return render(request, 'signup.html', data)

    def validatecustomer(self, customer):
        # Validations
        error_message = None
        if not customer.first_name:
            error_message = "First Name Required"
        elif len(customer.first_name) > 50:
            error_message = "First Name should be less than 50 characters"
        elif not customer.last_name:
            error_message = "Last Name Required"
        elif len(customer.last_name) > 50:
            error_message = "Last Name should be less than 50 characters"
        elif not customer.email:
            error_message = "Email Required"
        elif len(customer.email) > 50:
            error_message = "Email should be less than 50 characters"
        elif not customer.phone:
            error_message = "Phone Number Required"
        elif len(customer.phone) < 10:
            error_message = "Phone number should atleast have 10 numbers"
        elif not customer.password:
            error_message = "Password Required"
        elif len(customer.password) < 6:
            error_message = "Password should atleast have 6 characters"
        elif customer.isExists():
            error_message = "Email Address already registered"

        return error_message


class Index(View):
    def post(self,request):
        product = request.POST.get('product')
        remove = request.POST.get('remove')
        cart = request.session.get('cart')
        if cart:
            quantity = cart.get(product)
            if quantity:
                if remove:
                    if quantity<=1:
                        cart.pop(product)
                    else:
                        cart[product] = quantity-1
                else:
                    cart[product] = quantity+1
            else:
                cart[product] = 1
        else:
            cart = {}
            cart[product] = 1

        request.session['cart'] = cart
        print('cart' , request.session['cart'])
        return redirect('homepage')

    def get(self,request):
        cart = request.session.get('cart')
        if not cart:
            request.session.cart = {}
        products = None

        categories = Category.get_all_categories()
        categoryId = request.GET.get('category')
        if categoryId:
            products = Product.get_all_products_by_categoryid(categoryId)
        else:
            products = Product.get_all_products()
        data = {}
        data['products'] = products
        data['categories'] = categories
        print(request.session.get('email'))
        return render(request, 'index.html', data)


class Login(View):
    return_url = None
    def get(self,request):
        Login.return_url = request.GET.get('return_url')
        return render(request, 'login.html')
    def post(self,request):
        postData = request.POST
        email = postData.get('email')
        password = postData.get('password')
        customer = Customer.get_customer_by_email(email)
        error_message = None
        if customer:
            flag = check_password(password, customer.password)
            if flag:
                request.session['customer'] = customer.id

                if Login.return_url:
                    return HttpResponseRedirect(Login.return_url)

                else:
                    Login.return_url = None
                    return redirect('homepage')
            else:
                error_message = 'Invalid email or password!!'
        else:
            error_message = 'Invalid email or password!!'
        return render(request, 'login.html', {'error': error_message})


def logout(request):
    request.session.clear()
    return redirect('login')

class Cart(View):
    def get(self,request):
        check = request.session.get('cart')
        if check == None:
            return HttpResponse('Your cart is empty.')
        else:
            ids = list(request.session.get('cart').keys())
            print(ids)

            products= Product.get_products_by_id(ids)
            print(products)

            return render(request,'cart.html',{'products': products})

class CheckOut(View):
    def post(self,request):
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        customer = request.session.get('customer')
        if not customer:
            error_message = 'You have to log in to place your order'
            return render(request,'login.html',{'error':error_message})
        cart = request.session.get('cart')
        products = Product.get_products_by_id(list(cart.keys()))


        for product in products:
            order = Order(customer = Customer(id = customer),
                          product = product,
                          price = product.price,
                          address = address,
                          phone = phone,
                          quantity = cart.get(str(product.id)))
            order.placeOrder()

        request.session['cart'] = {}

        return redirect('cart')

class Order_view(View):


    def get(self,request):
        customer = request.session.get('customer')
        orders = Order.get_orders_by_customer(customer)
        print('These Are', orders)
        return render(request,'orders.html',{'orders':orders})
