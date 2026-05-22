from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .feed import build_feed, build_own_posts
from .forms import FollowForm, ReviewForm, SignUpForm, TicketForm, TicketReviewForm
from .models import Review, Ticket, UserFollows


def landing(request):
    if request.user.is_authenticated:
        return redirect('feed')
    return redirect('login')


class UserLoginView(LoginView):
    template_name = 'litrevu/login.html'
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = 'login'


def signup(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé. Bienvenue sur LITRevu !')
            return redirect('feed')
    else:
        form = SignUpForm()
    return render(request, 'litrevu/signup.html', {'form': form})


@login_required
def feed(request):
    posts = build_feed(request.user)
    reviewed_ticket_ids = set(
        Review.objects.filter(user=request.user).values_list('ticket_id', flat=True)
    )
    return render(
        request,
        'litrevu/feed.html',
        {
            'posts': posts,
            'reviewed_ticket_ids': reviewed_ticket_ids,
        },
    )


@login_required
def posts(request):
    own_posts = build_own_posts(request.user)
    return render(request, 'litrevu/posts.html', {'posts': own_posts})


@login_required
def following(request):
    follow_form = FollowForm()
    if request.method == 'POST':
        if 'username' in request.POST:
            follow_form = FollowForm(request.POST)
            if follow_form.is_valid():
                followed = follow_form.followed_user
                if followed == request.user:
                    messages.error(request, 'Vous ne pouvez pas vous suivre vous-même.')
                else:
                    UserFollows.objects.get_or_create(
                        user=request.user,
                        followed_user=followed,
                    )
                    messages.success(
                        request,
                        f"Vous suivez désormais {followed.username}.",
                    )
                return redirect('following')
        elif 'unfollow_id' in request.POST:
            UserFollows.objects.filter(
                user=request.user,
                followed_user_id=request.POST['unfollow_id'],
            ).delete()
            messages.info(request, 'Abonnement supprimé.')
            return redirect('following')

    followed = UserFollows.objects.filter(user=request.user).select_related(
        'followed_user'
    )
    return render(
        request,
        'litrevu/following.html',
        {'follow_form': follow_form, 'followed': followed},
    )


@login_required
def ticket_create(request):
    form = TicketForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        ticket = form.save(commit=False)
        ticket.user = request.user
        ticket.save()
        messages.success(request, 'Billet publié.')
        return redirect('feed')
    return render(request, 'litrevu/ticket_form.html', {'form': form, 'action': 'create'})


@login_required
def ticket_edit(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)
    form = TicketForm(
        request.POST or None,
        request.FILES or None,
        instance=ticket,
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Billet modifié.')
        return redirect('posts')
    return render(
        request,
        'litrevu/ticket_form.html',
        {'form': form, 'ticket': ticket, 'action': 'edit'},
    )


@login_required
@require_POST
def ticket_delete(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk, user=request.user)
    ticket.delete()
    messages.info(request, 'Billet supprimé.')
    return redirect('posts')


@login_required
def review_create(request, ticket_pk):
    ticket = get_object_or_404(Ticket, pk=ticket_pk)
    if Review.objects.filter(ticket=ticket, user=request.user).exists():
        messages.warning(request, 'Vous avez déjà critiqué ce billet.')
        return redirect('feed')
    form = ReviewForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        review = form.save(commit=False)
        review.ticket = ticket
        review.user = request.user
        review.save()
        messages.success(request, 'Critique publiée.')
        return redirect('feed')
    return render(
        request,
        'litrevu/review_form.html',
        {'form': form, 'ticket': ticket, 'action': 'create'},
    )


@login_required
def ticket_review_create(request):
    form = TicketReviewForm(
        request.POST or None,
        request.FILES or None,
    )
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        ticket = Ticket.objects.create(
            title=data['title'],
            description=data['description'],
            image=data.get('image'),
            user=request.user,
        )
        Review.objects.create(
            ticket=ticket,
            rating=data['rating'],
            headline=data['headline'],
            body=data['body'],
            user=request.user,
        )
        messages.success(request, 'Billet et critique publiés.')
        return redirect('feed')
    return render(request, 'litrevu/ticket_review_form.html', {'form': form})


@login_required
def review_edit(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    form = ReviewForm(request.POST or None, instance=review)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Critique modifiée.')
        return redirect('posts')
    return render(
        request,
        'litrevu/review_form.html',
        {'form': form, 'review': review, 'action': 'edit'},
    )


@login_required
@require_POST
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk, user=request.user)
    review.delete()
    messages.info(request, 'Critique supprimée.')
    return redirect('posts')
