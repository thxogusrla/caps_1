from django.shortcuts import render, redirect, get_object_or_404
from .models import ArticleFile, ArticleUrl, CommentUrl
from .forms import ArticleFileForm, ArticleUrlForm
from team.models import Team, TeamMember
from account.models import User
from django.utils import timezone

# Create your views here.
def workspace(request, team_pk, user_pk):
    team = get_object_or_404(Team, pk=team_pk) #팀에 대한 정보를 가져오고
    user = get_object_or_404(User, pk=user_pk) #사용자에 대한 정보를 가져오고
    member = TeamMember.objects.filter(team=team)
    now_user = request.user    
    urlform = ArticleUrlForm()
    fileform = ArticleFileForm()
#     ur = 'https://docs.djangoproject.com/en/2.2/ref/templates/builtins/' 
    search_url = ArticleUrl.objects.filter(team=team, user=user)
    search_file = ArticleFile.objects.filter(team=team, user=user)

    return render(request, 'team_article/workspace.html', {
        'search_url':search_url, 
        'search_file':search_file, 
        'team':team, 'user':user,
        'urlform':urlform,
        'fileform':fileform,
        'now_user':now_user,
        'user_team':member,
        # 'ur':ur,
        })

def articleurl(request, team_pk, user_pk):
    team = get_object_or_404(Team, pk=team_pk)
    user = get_object_or_404(User, pk=user_pk)
    if request.method == "POST":
        form = ArticleUrlForm(request.POST)
        if form.is_valid():
            articleurl = form.save(commit=False)
            articleurl.created_date = timezone.now()
            articleurl.team = team
            articleurl.user = user
            articleurl.url = form.cleaned_data['url']
            articleurl.explain_content = form.cleaned_data['explain_content']
            articleurl.save()
            return redirect('team_article:workspace', team_pk, user_pk)

    else:
        form = ArticleUrlForm()
        return render(request, 'team_article/url.html', {'form': form})

def articlefile(request, team_pk, user_pk):
    team = get_object_or_404(Team, pk=team_pk)
    user = get_object_or_404(User, pk=user_pk)
    if request.method == "POST":
        form = ArticleFileForm(request.POST, request.FILES)
        if form.is_valid():
            articlefiles = form.save(commit=False)
            articlefiles.team = team
            articlefiles.user = user
            articlefiles.file_url = form.cleaned_data['file_url']
            articlefiles.explain_content = form.cleaned_data['explain_content']
            articlefiles.created_date = timezone.now()
            articlefiles.save()
            return redirect('team_article:workspace', team_pk, user_pk)
    
    else:
        form = ArticleFileForm()
        return(request, 'team_article/file.html', {'form':form})


def delete_articleurl(request, team_pk, user_pk, url_pk):
    url = ArticleUrl.objects.filter(pk=url_pk)
    url.delete()
    return redirect('team_article:workspace', team_pk, user_pk)


def delete_articlefile(request, team_pk, user_pk, file_pk):
    files = ArticleFile.objects.filter(pk=file_pk)
    files.delete()
    return redirect('team_article:workspace', team_pk, user_pk)