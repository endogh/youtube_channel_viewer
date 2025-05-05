from django import forms
from .models import FavoritePlaylist

class ContentForm(forms.Form):
    input_content = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Masukkan @namaChannel atau judul video',
            'autocomplete': 'off',
            'id': 'video-search'
        }),
        help_text='Gunakan @ untuk channel atau ketik judul video'
    )
    selected_video_id = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'selected-video-id'}),
        required=False
    )

class FavoritePlaylistForm(forms.ModelForm):
    class Meta:
        model = FavoritePlaylist
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nama playlist favorit'
            })
        }