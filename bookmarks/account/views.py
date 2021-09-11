from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from .froms import LoginForm, UserRgistrationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from django.http.request import HttpRequest
from django.contrib.auth.models import User
from django.contrib import messages

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
def dashboard(request: HttpRequest):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})


def register(request: HttpRequest):
    if request.method == 'POST': # 用户输入的数据（新表单）
        user_form = UserRgistrationForm(request.POST) # request.POST是一个字典数据，通过这个字典数据创建表
        
        if user_form.is_valid():
            # 创建新的用户
            new_user:User = user_form.save(commit=False) # 暂时不保存

            new_user.set_password(user_form.cleaned_data['password']) # 使用set_password来存储散列过的密码
            # 保存用户
            new_user.save()

            # 转到注册完成
            return render(request, 'account/register_done.html', {'new_user': new_user})

    else:

        user_form = UserRgistrationForm() # 空的表单
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required
def edit(request: HttpRequest):
    if request.method == 'POST':
        print(request.POST)
        user_form = UserEditForm(instance=request.user, data=request.POST) # 从post中获取数据（用户填写），并且应用到当前的对象
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user) # type: ignore # 通过当前的请求的用户，通过关联在数据库中的数据来创建表单。
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form':profile_form})