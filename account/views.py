from django.shortcuts import render, redirect,get_object_or_404
from django.contrib import auth
from .forms import *
from .models import User
from team.models import TeamMember
from django.contrib.auth.decorators import login_required

# Create your views here.


# 회원가입
def sign_up(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        # 폼이 검증되면 로그인 되고 sign_up url로 넘어감(이 부분은 메인 화면으로 넘어  가도록 수정할 예정)
        if form.is_valid():
            form.save()
            auth.login(request, User.objects.get(username=form.cleaned_data['username']))
            user = request.user
            return redirect('account:set_schedule')
        # 폼이 검증이 안되면 22번째 줄로 넘어가 에러메세지를 포함한 폼을 보내 템플릿을 렌더링함
    # request가 get이면 빈폼을 생성하고 22번째로 넘어가 템플릿 렌더링
    else:
        form = SignUpForm()
    return render(request, 'account/sign_up.html', {'form': form})


# 로그인
def sign_in(request):
    if request.method == "POST":
        form = SignInForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            # 폼이 검증되고 입력받은 아이디와 비밀번호가 일치하는 User모델을 user 변수에 저장
            user = auth.authenticate(username=username, password=password)

            # user가 존재하면 로그인을 하고 메인화면으로 넘어감(메인이 구현안되있어 로그인으로 넘어가게 수정함)
            if user:
                auth.login(request, user)
                return redirect('account:set_schedule')
            # 만약 존재하지 않으면 form에 에러메세지를 추가하고 46번째 줄로넘어가 템플릿을 렌더링함
            else:
                form.add_error(None, '아이디 또는 비밀번호가 올바르지 않습니다.')
    # 방식이 get일때 빈폼을 생성하고 46번째 줄로넘어가 로그인 템플릿을 폼을 포함하여 렌더링한다

    else:
        form = SignInForm()
    return render(request, 'account/sign_in.html', {'form': form})

def user_home(request, user_pk):
    user = request.user
    if user.id == user_pk:
        user = get_object_or_404(User, pk=user_pk)
        user_team = TeamMember.objects.filter(user=user) #팀의 목록을 출력해줄것임!
        return render(request, 'account/user_home.html', {'user':user, 'user_team':user_team})
    
    else: # 현재사용자가 다른 사용자의 홈을 들어갈경우 로그인창으로 돌아가게 함
        return redirect('account:sign_in')


# 로그아웃
def sign_out(request):
    auth.logout(request)
    return redirect('account:sign_in')


# 팀 유저의 개인정보를 보여주는 창
def user_info(request, user_pk):
   user = get_object_or_404(User, pk=user_pk)
   return render(request, 'account/user_info.html', {'user':user})

# 개인정보수정
def edit(request, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    if request.method == "POST":
        form = UserChangeForm(data=request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            return redirect("account:user_home", user_pk)
    else:
        form = UserChangeForm(instance=request.user)
        return render(request, "account/sign_in.html", {'form': form})


# 시간표 설정
@login_required
def set_schedule(request):
    user = get_object_or_404(User, pk=request.user.id)
    user_team = TeamMember.objects.filter(user=user) #팀의 목록을 출력해줄것임!

    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            user.time_table = form.cleaned_data['time_table']
            user.save()
        return redirect("account:user_home", user.pk)
    else:
        form = ScheduleForm(instance=request.user)
    return render(request, "account/schedule.html", {'form': form, 'user_team':user_team})
  
