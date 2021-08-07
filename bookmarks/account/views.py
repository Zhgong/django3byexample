from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .froms import LoginForm
from django.contrib.auth.decorators import login_required

# def user_login(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST) # 根据提交的数据创建表单对象
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request,
#             username=cd['username'],
#             password=cd['password'])

#         if user is not None: # 检查用户是否存在
#             if user.is_active: # 检查用户是否被禁用
#                 login(request, user)
#                 return HttpResponse('Authenticated successfully')

#             else:
#                 return HttpResponse('Disabled account')

#         else:
#             return HttpResponse('Invalid login')

#     else:
#         form = LoginForm() # 创建一个空的表单供用户填写

#     return render(request, 'account/login.html', {'form': form})


# Create your views here.

@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})
