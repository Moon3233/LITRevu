from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Review, Ticket

User = get_user_model()


class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username',)
        labels = {
            'username': "Nom d'utilisateur",
            'password1': 'Mot de passe',
            'password2': 'Confirmer le mot de passe',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.fields:
            self.fields[name].help_text = ''
        self.fields['username'].widget.attrs.update({
            'placeholder': 'Ex. camille_leroy',
            'autocomplete': 'username',
        })
        self.fields['password1'].widget.attrs.update({
            'autocomplete': 'new-password',
        })
        self.fields['password2'].widget.attrs.update({
            'autocomplete': 'new-password',
        })


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ('title', 'description', 'image')
        widgets = {
            'title': forms.TextInput(
                attrs={
                    'placeholder': 'Titre du livre ou article'}),
            'description': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Description'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('rating', 'headline', 'body')
        widgets = {
            'rating': forms.HiddenInput(),
            'headline': forms.TextInput(
                attrs={
                    'placeholder': "Titre de la critique"}),
            'body': forms.Textarea(
                attrs={
                    'rows': 5,
                    'placeholder': 'Commentaire'}),
        }


class TicketReviewForm(forms.Form):
    """Création simultanée d'un billet et d'une critique."""

    title = forms.CharField(max_length=128, label='Titre')
    description = forms.CharField(
        max_length=2048,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Description',
    )
    image = forms.ImageField(required=False, label='Image')
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        label='Note',
        error_messages={'required': 'Veuillez sélectionner une note.'},
    )
    headline = forms.CharField(max_length=128, label='Titre de la critique')
    body = forms.CharField(
        max_length=8192,
        required=False,
        widget=forms.Textarea(attrs={'rows': 4}),
        label='Commentaire',
    )


class FollowForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Nom d'utilisateur",
        widget=forms.TextInput(
            attrs={
                'placeholder': "Entrez un nom d'utilisateur"}),
    )

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        try:
            self.followed_user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(
                "Cet utilisateur n'existe pas. Vérifiez le nom saisi."
            )
        return username
