from .models import Review, UserFollows


def user_follows(follower, followed_user_id):
    return UserFollows.objects.filter(
        user=follower,
        followed_user_id=followed_user_id,
    ).exists()


def can_review_ticket(user, ticket):
    """
    Vérifie qu'un utilisateur peut publier une critique sur un billet.

    Règles :
    - pas son propre billet (utiliser ticket-critique/nouveau pour ça) ;
    - une seule critique par utilisateur et par billet ;
    - doit suivre l'auteur du billet.
    """
    if ticket.user_id == user.pk:
        return False, 'Vous ne pouvez pas critiquer votre propre billet.'

    if Review.objects.filter(ticket=ticket, user=user).exists():
        return False, 'Vous avez déjà posté une critique pour ce billet.'

    if not user_follows(user, ticket.user_id):
        return (
            False,
            "Vous devez suivre l'auteur du billet pour y répondre.",
        )

    return True, ''
