from itertools import chain

from django.db.models import CharField, Q, Value

from .models import Review, Ticket, UserFollows


def _following_ids(user):
    return UserFollows.objects.filter(user=user).values_list(
        'followed_user_id', flat=True
    )


def get_users_viewable_tickets(user):
    following = _following_ids(user)
    return Ticket.objects.filter(
        Q(user=user) | Q(user_id__in=following)
    ).select_related('user')


def get_users_viewable_reviews(user):
    following = _following_ids(user)
    return Review.objects.filter(
        Q(user=user)
        | Q(user_id__in=following)
        | Q(ticket__user=user)
    ).select_related('user', 'ticket', 'ticket__user')


def get_user_posts(user):
    tickets = Ticket.objects.filter(user=user).select_related('user')
    reviews = Review.objects.filter(user=user).select_related(
        'user', 'ticket', 'ticket__user'
    )
    return tickets, reviews


def build_feed(user):
    tickets = get_users_viewable_tickets(user).annotate(
        content_type=Value('TICKET', CharField())
    )
    reviews = get_users_viewable_reviews(user).annotate(
        content_type=Value('REVIEW', CharField())
    )
    return sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True,
    )


def build_own_posts(user):
    tickets, reviews = get_user_posts(user)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))
    return sorted(
        chain(reviews, tickets),
        key=lambda post: post.time_created,
        reverse=True,
    )
