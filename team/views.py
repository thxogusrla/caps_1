from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.utils import timezone
from .models import Team, TeamMember, TeamTimeTable
from account.models import User
from django.contrib.auth.decorators import login_required
from .forms import TeamForm, AddForm
# Create your views here.
# def correct_teammember(request, team_pk):
#    team = get_object_or_404(Team, pk=team_pk)
#    user = request.user
#    for i in TeamMember.objects.filter(team__team_name=team.team_name):
#       if i.user.pk == user.pk:
#          return render
# 2진 데이터를 or로 비교

def or_gate(a, b):      
    result = ""
    for i in range(len(a)):
        if (a[i] == b[i]) and a[i] == '0':
            result += '0'
        else:
            result += '1'

    return result

# 2진 데이터를 not으로 변환
def not_gate(binary):
    result = ""
    for i in binary:
        if i == '1':
            result += '0'
        else:
            result += '1'
    return result

# or게이트와 not게이트를 이용해서 팀에 소속된 유저들의 시간표를 각각 비교해서 원하는 이진데이터를 구함
def get_time_table(team_id):
    team = get_object_or_404(Team, pk=team_id)
    team_members = team.members.all()
    result_time_table = team_members[0].time_table
    for member in team_members[1:]:
        result_time_table = or_gate(result_time_table, member.time_table)

    return not_gate(result_time_table)

@login_required
def detail_team(request, team_id):
   details = get_object_or_404(Team, pk=team_id)
   login_user = request.user
   user_team = TeamMember.objects.filter(user=login_user)
   team_member = TeamMember.objects.filter(team=details)
   team_time_table = TeamTimeTable.objects.filter(team=details)
   for i in TeamMember.objects.filter(team__pk=details.pk):
      if i.user.pk == login_user.pk:         
         return render(request, 'team/detail_team.html',{
             'details': details, 'team_member':team_member,
             'login_user':login_user, 'user_team':user_team
             })
   
   return redirect('account:user_home', login_user.pk)
   
@login_required
def create_team(request):
   # user = get_object_or_404(User, pk=user_id)
   user = request.user
   
   if request.method == 'POST':
      form = TeamForm(request.POST)
      if form.is_valid():
         team = form.save()
         TeamMember.objects.create(team=team, user=user)
         # team.members.add(user)
         team.team_leader.add(user)
         team.team_name = form.cleaned_data['team_name']
         team.introduce = form.cleaned_data['introduce']
         team.created_date = timezone.now()
         team.save()
         return redirect('team:detail_team', team.pk)
   else:
      teamform = TeamForm()
      return render(request, 'team/create_team.html', {'teamform': teamform})

@login_required
def add_member(request, team_id):
   team1 = get_object_or_404(Team, pk=team_id)
   login_user = request.user
   if TeamMember.objects.filter(team__pk=team1.pk).count() < 6:
      if request.method == 'POST':
         form = AddForm(request.POST)
         if form.is_valid():
            member = form.save(commit=False)
            member.team = team1 #팀에대한 정보를 가져와 TeamMember의 team 에다가 저장을 하고.
            if User.objects.filter(username=form.cleaned_data['username']):
                member.user = User.objects.get(username=form.cleaned_data['username']) #해당유저에 대한 데이터를 가져오고
                if TeamMember.objects.filter(team=team1, user=member.user): #해당 팀에 user가 이미 존재해 있는 경우
                    return HttpResponse('해당사용자가 팀에 존재합니다!')
               
                else: # 해당 팀에 user가 존재하지 않는다면 멤버로 추가
                    tm = TeamMember(team=team1, user=member.user) 
                    tm.save()
                    return redirect('team:detail_team', team_id)
            
            # elif TeamMember.objects.filter(team=team1, user=member.user):
            #    return HttpResponse('해당사용자가 팀에 존재합니다!')
            else:
                return HttpResponse('해당 사용자가 존재하지 않습니다!')
      else:
        for i in TeamMember.objects.filter(team__pk=team1.pk):
            if i.user.pk == login_user.pk: 
               form = AddForm()
               return render(request, 'team/add_member.html', {'form':form})
        return redirect('account:uset_home', login_user.pk)
   else:
        return HttpResponse('정원이 초과되었습니다!')

@login_required
def expulsion_member(request, team_id, user_id):  # 어느 팀에서 몇번 째 유저를 삭제할지.
    login_user = request.user
    team = get_object_or_404(Team, pk=team_id)  # 어느 팀 객체인지 가져오고
    user = get_object_or_404(User, pk=user_id)  # 어느 유저 객체인지 가져온 다음에
    delete_member = TeamMember.objects.filter(team=team, user=user)  # 외래키 설정 되어있는 team과 user 에 각각을 매칭 시켜주기
    delete_member.delete()
    return redirect('team:detail_team', team_id)

@login_required
def leave_team(request, team_pk, user_pk):
    user = get_object_or_404(User, pk=user_pk)
    team = get_object_or_404(Team, pk=team_pk)
    leave = TeamMember.objects.filter(team=team, user=user)
    leave.delete()
    if TeamMember.objects.filter(team__team_name=team.team_name).count() != 0: # 팀 멤버들이 존재한다면!
        if team.team_leader == user:
            if Team.objects.filter(team_leader__pk=user_pk): # 
                next_leader = TeamMember.objects.filter(team__team_name=team.team_name).first()
                leader = get_object_or_404(User, pk=next_leader.user.pk)
                team.team_leader.set([leader])
                team.save()
                return redirect('account:user_home', user_pk)
            return HttpResponse('리더 위임 실패')
        else:
            return redirect('account:user_home', user_pk)
    else:
        team.delete()
        return redirect('account:user_home', user_pk)

def edit_team(request, team_pk):
   team = get_object_or_404(Team, pk=team_pk)
   user = request.user
   if request.method == "POST":
      form = TeamForm(request.POST)
      if form.is_valid():
         team.team_name = form.cleaned_data['team_name']
         team.introduce = form.cleaned_data['introduce']
         team.team_photho_url = form.cleaned_data['team_photo_url']
         team.save()
         return redirect('team:detail_team',team_pk)
   else:
      teamform = TeamForm(instance=team)
      return render(request, 'team/create_team.html', {'teamform':teamform})

# def add_time_table(request, team_pk):

#     team = get_object_or_404(Team, pk=team_pk)
#     user = request.user
#     if TeamTimeTable.objects.filter(team=team, user=user).count() >= 1:
#         return 1
#     ttt = TeamTimeTable(team=team, user=user, total_time_table=user.time_table)
#     ttt.save()
#     return 2

def add_time_table(request, team_pk):
    team = get_object_or_404(Team, pk=team_pk)
    user = request.user
    if TeamTimeTable.objects.filter(team=team, user=user).count() >= 1:
        return ValueError
    ttt = TeamTimeTable(team=team, user=user, total_time_table=user.time_table)
    ttt.save()
    return redirect('team:detail_team', team_pk)
    
def delete_time_table(request, team_pk):
    team = get_object_or_404(Team, pk=team_pk)
    user = request.user
    delete_user_time_table = TeamTimeTable.objects.filter(team=team, user=user)
    delete_user_time_table.delete()
    return redirect("team:detail_team", team_pk)

def team_user_timetable(request, team_pk):
    team = get_object_or_404(Team, pk=team_pk)
    user_team = TeamMember.objects.filter(team=team)
    member_time_table = TeamTimeTable.objects.filter(team=team)
    user = request.user
    return render(request, "team/teamtimetable.html",{'user_team':member_time_table, 'user':user, 'team':team})
