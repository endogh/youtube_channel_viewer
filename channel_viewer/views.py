from django.shortcuts import render, redirect
from googleapiclient.discovery import build
from django.conf import settings
from .models import YouTubeChannel, YouTubeVideo, FavoritePlaylist
from .forms import ContentForm, FavoritePlaylistForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from django.views.decorators.http import require_http_methods
from .forms import ContentForm, FavoritePlaylistForm

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

def get_youtube_service():
    return build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)

def get_channel_id(channel_name):
    youtube = get_youtube_service()
    request = youtube.search().list(
        q=channel_name,
        part='snippet',
        type='channel',
        maxResults=1
    )
    response = request.execute()
    return response['items'][0]['snippet']['channelId'] if response['items'] else None

def get_channel_videos(channel_id):
    youtube = get_youtube_service()
    request = youtube.search().list(
        channelId=channel_id,
        part='snippet',
        type='video',
        maxResults=50,
        order='date'
    )
    response = request.execute()
    return response.get('items', [])

def get_video_details(video_id):
    youtube = get_youtube_service()
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    response = request.execute()
    return response['items'][0]['snippet'] if response['items'] else None


@login_required
def add_to_favorites(request, video_id):
    video = YouTubeVideo.objects.get(video_id=video_id)
    
    if request.method == 'POST':
        form = FavoritePlaylistForm(request.POST)
        if form.is_valid():
            playlist, created = FavoritePlaylist.objects.get_or_create(
                user=request.user,
                name=form.cleaned_data['name'],
                defaults={}
            )
            playlist.videos.add(video)
            messages.success(request, f'Video ditambahkan ke playlist {playlist.name}!')
            return redirect('home')
    else:
        form = FavoritePlaylistForm()
    
    return render(request, 'channel_viewer/add_to_favorites.html', {
        'form': form,
        'video': video
    })

@login_required
def view_favorites(request):
    playlists = FavoritePlaylist.objects.filter(user=request.user)
    return render(request, 'channel_viewer/favorites.html', {
        'playlists': playlists
    })




def search_videos(request):
    query = request.GET.get('q', '')
    
    if query:
        youtube = get_youtube_service()
        search_response = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=10
        ).execute()
        
        suggestions = [{
            'title': item['snippet']['title'],
            'video_id': item['id']['videoId'],
            'channel': item['snippet']['channelTitle'],
            'thumbnail': item['snippet']['thumbnails']['default']['url']
        } for item in search_response.get('items', [])]
        
        return JsonResponse({'suggestions': suggestions})
    
    return JsonResponse({'suggestions': []})

from django.contrib.auth.decorators import login_required


# @login_required
# def home(request):
#     if request.method == 'POST':
#         form = ContentForm(request.POST)
#         if form.is_valid():
#             input_content = form.cleaned_data['input_content']
            
#             if input_content.startswith('@'):
#                 channel_name = input_content[1:]
#                 channel_id = get_channel_id(channel_name)
                
#                 if channel_id:
#                     channel, created = YouTubeChannel.objects.get_or_create(
#                         channel_id=channel_id,
#                         user=request.user,  # Tambahkan user di sini
#                         defaults={
#                             'channel_name': channel_name,
#                             'is_whitelisted': True
#                         }
#                     )
                    
#                     if not created:
#                         channel.is_whitelisted = True
#                         channel.save()
                    
#                     videos = get_channel_videos(channel_id)
#                     for video in videos:
#                         YouTubeVideo.objects.update_or_create(
#                             video_id=video['id']['videoId'],
#                             user=request.user,  # Tambahkan user di sini
#                             defaults={
#                                 'title': video['snippet']['title'],
#                                 'channel': channel,
#                                 'published_at': video['snippet']['publishedAt'],
#                                 'thumbnail_url': video['snippet']['thumbnails']['medium']['url'],
#                                 'description': video['snippet']['description']
#                             }
#                         )
                    
#                     messages.success(request, f'Channel {channel_name} berhasil di-whitelist!')
#             else:
#                 video_id = request.POST.get('selected_video_id')
#                 if video_id:
#                     video_details = get_video_details(video_id)
#                     channel_id = video_details['channelId']
#                     channel_name = video_details['channelTitle']
                    
#                     channel, _ = YouTubeChannel.objects.get_or_create(
#                         channel_id=channel_id,
#                         user=request.user,  # Tambahkan user di sini
#                         defaults={
#                             'channel_name': channel_name
#                         }
#                     )
                    
#                     YouTubeVideo.objects.update_or_create(
#                         video_id=video_id,
#                         user=request.user,  # Tambahkan user di sini
#                         defaults={
#                             'title': video_details['title'],
#                             'channel': channel,
#                             'published_at': video_details['publishedAt'],
#                             'thumbnail_url': video_details['thumbnails']['medium']['url'],
#                             'description': video_details['description'],
#                             'is_whitelisted': True
#                         }
#                     )
                    
#                     messages.success(request, f'Video {video_details["title"]} berhasil di-whitelist!')
#                 else:
#                     messages.error(request, 'Silakan pilih video dari saran yang tersedia')
            
#             return redirect('home')
#     else:
#         form = ContentForm()
    
#     # Filter berdasarkan user yang login
#     whitelisted_channels = YouTubeChannel.objects.filter(
#         is_whitelisted=True,
#         user=request.user  # Filter berdasarkan user
#     )
#     whitelisted_videos = YouTubeVideo.objects.filter(
#         is_whitelisted=True,
#         user=request.user  # Filter berdasarkan user
#     )
    
#     return render(request, 'channel_viewer/home.html', {
#         'form': form,
#         'whitelisted_channels': whitelisted_channels,
#         'whitelisted_videos': whitelisted_videos
#     })

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from googleapiclient.discovery import build
from .forms import ContentForm, FavoritePlaylistForm
from .models import YouTubeChannel, YouTubeVideo, FavoritePlaylist
from django.conf import settings
from django.views.decorators.http import require_GET

def get_youtube_service():
    return build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)

@login_required
def home(request):
    form = ContentForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        input_content = form.cleaned_data['input_content']
        selected_video_id = form.cleaned_data['selected_video_id']
        
        if input_content.startswith('@'):
            # Handle channel whitelisting
            channel_name = input_content[1:]
            channel_id = get_channel_id(channel_name)
            
            if channel_id:
                channel, created = YouTubeChannel.objects.get_or_create(
                    channel_id=channel_id,
                    user=request.user,
                    defaults={
                        'channel_name': channel_name,
                        'is_whitelisted': True
                    }
                )
                
                if not created:
                    channel.is_whitelisted = True
                    channel.save()
                
                # Save channel videos
                videos = get_channel_videos(channel_id)
                for video in videos:
                    YouTubeVideo.objects.update_or_create(
                        video_id=video['id']['videoId'],
                        user=request.user,
                        defaults={
                            'title': video['snippet']['title'],
                            'channel': channel,
                            'published_at': video['snippet']['publishedAt'],
                            'thumbnail_url': video['snippet']['thumbnails']['medium']['url'],
                            'description': video['snippet']['description']
                        }
                    )
                
                messages.success(request, f'Channel @{channel_name} berhasil di-whitelist!')
        elif selected_video_id:
            # Handle video whitelisting
            video_details = get_video_details(selected_video_id)
            
            if video_details:
                channel_id = video_details['channelId']
                channel_name = video_details['channelTitle']
                
                channel, _ = YouTubeChannel.objects.get_or_create(
                    channel_id=channel_id,
                    user=request.user,
                    defaults={'channel_name': channel_name}
                )
                
                YouTubeVideo.objects.update_or_create(
                    video_id=selected_video_id,
                    user=request.user,
                    defaults={
                        'title': video_details['title'],
                        'channel': channel,
                        'published_at': video_details['publishedAt'],
                        'thumbnail_url': video_details['thumbnails']['medium']['url'],
                        'description': video_details['description'],
                        'is_whitelisted': True
                    }
                )
                messages.success(request, f'Video "{video_details["title"]}" berhasil di-whitelist!')
        else:
            messages.error(request, 'Silakan pilih video dari saran yang tersedia')
        
        return redirect('home')
    
    # Get user's whitelisted content
    whitelisted_channels = YouTubeChannel.objects.filter(
        user=request.user,
        is_whitelisted=True
    )
    whitelisted_videos = YouTubeVideo.objects.filter(
        user=request.user,
        is_whitelisted=True
    )
    
    return render(request, 'channel_viewer/home.html', {
        'form': form,
        'whitelisted_channels': whitelisted_channels,
        'whitelisted_videos': whitelisted_videos
    })

@require_GET
def search_suggestions(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    query = request.GET.get('q', '')
    if len(query) < 3 or query.startswith('@'):
        return JsonResponse({'suggestions': []})
    
    try:
        youtube = get_youtube_service()
        search_response = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=10
        ).execute()
        
        suggestions = [{
            'title': item['snippet']['title'],
            'video_id': item['id']['videoId'],
            'channel': item['snippet']['channelTitle'],
            'thumbnail': item['snippet']['thumbnails']['default']['url']
        } for item in search_response.get('items', [])]
        
        return JsonResponse({'suggestions': suggestions})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)