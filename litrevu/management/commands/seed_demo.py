import json
import shutil
import urllib.parse
import urllib.request
from datetime import timedelta
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlretrieve

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from litrevu.models import Review, Ticket, UserFollows

User = get_user_model()

DEMO_PASSWORD = 'Demo1234!'
USERS = ('demo', 'camille', 'hugo', 'sophie', 'thomas', 'ines')

SEED_COVERS_DIR = Path(__file__).resolve(
).parents[2] / 'seed_assets' / 'covers'
COVER_ISBN_API = 'https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg'
COVER_ID_API = 'https://covers.openlibrary.org/b/id/{cover_id}-L.jpg'
SEARCH_API = 'https://openlibrary.org/search.json?q={query}&limit=1'

# Livres grand public — couvertures via Open Library (ISBN ou recherche)
BOOKS = [
    {
        'key': 'harry_potter',
        'user': 'camille',
        'isbn': '9780747532699',
        'title': "Harry Potter à l'école des sorciers — J.K. Rowling",
        'description': (
            "Fan des films depuis longtemps, j'attaque enfin le livre. "
            "Est-ce que la lecture apporte vraiment quelque chose en plus, "
            "ou l'imagination est déjà « calée » sur le visuel ? "
            "Curieux de vos avis sans détailler l'intrigue."
        ),
        'when': timedelta(days=6, hours=3),
    },
    {
        'key': '1984',
        'user': 'hugo',
        'isbn': '9780451524935',
        'title': '1984 — George Orwell',
        'description': (
            "Pour un débat au travail : Big Brother, novlangue, télécrans… "
            "Quels parallèles avec 2026 vous semblent les plus pertinents — "
            "et lesquels relèvent du cliché ?"
        ),
        'when': timedelta(days=5, hours=8),
    },
    {
        'key': 'petit_prince',
        'user': 'sophie',
        'isbn': '9782070612758',
        'title': 'Le Petit Prince — Antoine de Saint-Exupéry',
        'description': (
            "Je l'offre à ma nièce de 9 ans. Par quelle édition illustrée "
            "vous avez-vous"
            "été marqué·e ? Faut-il laisser les chapitres sur la rose et le "
            "renard"
            "pour plus tard ?"
        ),
        'when': timedelta(days=4, hours=14),
    },
    {
        'key': 'seigneur_anneaux',
        'user': 'thomas',
        'isbn': '9780007488315',
        'title': 'Le Seigneur des Anneaux (La Communauté) — J.R.R. Tolkien',
        'description': (
            "Après les films : vaut-il le coup de s'attaquer aux trois "
            "volumes cette année ? "
            "Les passages de chants et de géographie vous ont-ils rebuté ou"
            "transporté ?"
        ),
        'when': timedelta(days=3, hours=6),
    },
    {
        'key': 'monte_cristo',
        'user': 'demo',
        'isbn': '9780140449266',
        'title': 'Le Comte de Monte-Cristo — Alexandre Dumas',
        'description': (
            "Relecture avant de le prêter à mon neveu de 17 ans. "
            "Par quelle scène vous êtes-vous laissé·e·s porter : la prison, "
            "la vengeance, ou les intrigues parisiennes ?"
        ),
        'when': timedelta(days=2, hours=4),
    },
    {
        'key': 'hunger_games',
        'user': 'hugo',
        'isbn': '9780439023481',
        'title': 'Hunger Games — Suzanne Collins',
        'description': (
            "Je (re)lis la saga avant de la conseiller à ma cousine de 15 "
            "ans."
            "Le premier tome reste-t-il aussi prenant qu'à sa sortie, ou le "
            "comparatif"
            "avec les films a vieilli l'expérience ? Avis sans spoiler."
        ),
        'when': timedelta(days=1, hours=2),
    },
    {
        'key': 'appel_coucou',
        'user': 'demo',
        'search': "The Cuckoo's Calling Robert Galbraith",
        'title': "L'appel du coucou — Robert Galbraith",
        'description': (
            "Je commence la série Cormoran Strike sans avoir vu l'adaptation. "
            "Le polar tient-il la route dès ce premier tome, ou faut-il "
            "attendre"
            "le suivant pour être accroché ? Merci d'éviter les spoilers."
        ),
        'when': timedelta(hours=18),
    },
]

REVIEWS_DATA = [
    {
        'user': 'hugo',
        'ticket': '1984',
        'rating': 5,
        'headline': 'Toujours glaçant, jamais « dépassé »',
        'body': (
            "La novlangue et la mise en abyme de la réécriture des faits "
            "résonnent"
            "avec les débats sur l'info aujourd'hui. Orwell ne prédit pas une "
            "tech"
            "précise : il décrit des mécanismes de pouvoir. Idéal pour un "
            "club qui"
            "veut parler politique sans s'enfermer dans l'actualité brûlante."
        ),
        'when': timedelta(days=4, hours=20),
    },
    {
        'user': 'demo',
        'ticket': '1984',
        'rating': 4,
        'headline': 'Winston et Julia : le cœur du roman',
        'body': (
            "Hugo, je rejoins l'idée du parallèle actuel, mais c'est la part "
            "intime"
            "qui m'a le plus touché : la fragilité du lien humain sous "
            "surveillance."
            "La chambre au-dessus de la boutique antique reste l'une des "
            "scènes"
            "les plus tristes de la littérature du XXe siècle."
        ),
        'when': timedelta(days=4, hours=8),
    },
    {
        'user': 'thomas',
        'ticket': 'petit_prince',
        'rating': 5,
        'headline': "Offrez l'édition illustrée couleur",
        'body': (
            "Sophie, pour 9 ans : oui aux chapitres rose et renard, ils sont "
            "concrets"
            "sans être moralisateurs. L'édition Folio classique ou Gallimard "
            "jeunesse"
            "tient bien. Lisez à voix haute : les répétitions deviennent des"
            "refrains."
        ),
        'when': timedelta(days=3, hours=22),
    },
    {
        'user': 'sophie',
        'ticket': 'seigneur_anneaux',
        'rating': 4,
        'headline': 'Les films aident, le livre approfondit',
        'body': (
            "Thomas, attaque les trois volumes si tu as le temps : la "
            "Communauté"
            "est la plus accessible, mais c'est au Two Towers que la guerre "
            "devient"
            "grise. Les chants ? Survole-les la première fois, reviens-y"
            "ensuite."
        ),
        'when': timedelta(days=2, hours=14),
    },
    {
        'user': 'ines',
        'ticket': 'monte_cristo',
        'rating': 5,
        'headline': 'La prison, puis tout décolle',
        'body': (
            "Demo : pour ton neveu, commence par lui dire que les 200 "
            "premières pages"
            "sont un investissement. Château d'If = tension pure. Ensuite la "
            "vengeance"
            "devient un jeu d'échecs. Même sans te suivre, je vois ce billet "
            "car"
            "j'y réponds — merci LITRevu !"
        ),
        'when': timedelta(days=1, hours=6),
    },
    {
        'user': 'sophie',
        'ticket': 'harry_potter',
        'rating': 4,
        'headline': 'Les films guident un peu, le livre ouvre le reste',
        'body': (
            "Camille, pour Harry, Ron, Hermione ou Poudlard, mon imagination "
            "est déjà calée sur le visuel des films — difficile de faire "
            "autrement."
            "Mais le livre apporte tellement de personnages absents à "
            "l'écran,"
            "de scènes et de décors inédits que l'ensemble reste très vivant. "
            "Au final, l'imagination n'est impactée que légèrement : on "
            "retrouve"
            "ses repères, et on découvre encore pas mal de choses neuves."
        ),
        'when': timedelta(days=5, hours=12),
    },
    {
        'user': 'thomas',
        'ticket': 'hunger_games',
        'rating': 5,
        'headline': 'Toujours aussi nerveux',
        'body': (
            "Hugo, le premier tome accroche dès les premiers chapitres : le "
            "rythme,"
            "la tension, le côté « téléréalité » glaçant. Même en connaissant "
            "la fin"
            "des films, la lecture garde son mordant."
        ),
        'when': timedelta(hours=26),
    },
    {
        'user': 'hugo',
        'ticket': 'appel_coucou',
        'rating': 4,
        'headline': 'Un bon entrée dans Strike',
        'body': (
            "Demo, le premier tome pose bien l'enquête et le duo Strike / "
            "Robin."
            "C'est dense, très londonien, parfois un peu long sur la mise en "
            "place,"
            "mais la fin justifie la patience. Parfait si tu aimes le polar "
            "sans"
            "violence gratuite."
        ),
        'when': timedelta(hours=17),
    },
]


class Command(BaseCommand):
    help = (
        'Charge une base de démonstration avec livres connus '
        'et couvertures.'
    )

    def handle(self, *args, **options):
        User.objects.filter(is_superuser=False).delete()
        UserFollows.objects.all().delete()
        Review.objects.all().delete()
        Ticket.objects.all().delete()

        media_tickets = Path(settings.MEDIA_ROOT) / 'tickets'
        if media_tickets.exists():
            shutil.rmtree(media_tickets)
        SEED_COVERS_DIR.mkdir(parents=True, exist_ok=True)

        users = {
            name: User.objects.create_user(
                username=name,
                password=DEMO_PASSWORD,
            )
            for name in USERS
        }

        follows = [
            ('demo', 'camille'),
            ('demo', 'hugo'),
            ('demo', 'sophie'),
            ('demo', 'thomas'),
            ('camille', 'demo'),
            ('camille', 'hugo'),
            ('hugo', 'demo'),
            ('hugo', 'sophie'),
            ('sophie', 'camille'),
            ('sophie', 'thomas'),
            ('thomas', 'demo'),
            ('thomas', 'ines'),
            ('ines', 'demo'),
        ]
        for follower, followed in follows:
            UserFollows.objects.create(
                user=users[follower],
                followed_user=users[followed],
            )

        now = timezone.now()
        tickets = {}

        def stamp(queryset, pk, when):
            queryset.filter(pk=pk).update(time_created=when)

        covers_ok = 0
        for book in BOOKS:
            cover_path = self._ensure_cover(
                book['key'],
                isbn=book.get('isbn'),
                search=book.get('search'),
            )
            ticket = Ticket.objects.create(
                user=users[book['user']],
                title=book['title'],
                description=book['description'],
            )
            if cover_path:
                with cover_path.open('rb') as cover_file:
                    ticket.image.save(
                        f"{book['key']}.jpg", File(cover_file), save=True)
                covers_ok += 1
            tickets[book['key']] = ticket
            stamp(Ticket.objects, ticket.pk, now - book['when'])

        for data in REVIEWS_DATA:
            review = Review.objects.create(
                user=users[data['user']],
                ticket=tickets[data['ticket']],
                rating=data['rating'],
                headline=data['headline'],
                body=data['body'],
            )
            stamp(Review.objects, review.pk, now - data['when'])

        self.stdout.write(self.style.SUCCESS('Base de présentation chargée.'))
        self.stdout.write(f'Couvertures : {covers_ok}/{len(BOOKS)}')
        self.stdout.write('Compte principal : demo / Demo1234!')
        self.stdout.write(
            f'{Ticket.objects.count()} billets, '
            f'{Review.objects.count()} critiques.'
        )

    def _ensure_cover(
        self,
        slug: str,
        *,
        isbn: str | None = None,
        search: str | None = None,
    ) -> Path | None:
        """Télécharge ou réutilise une couverture (Open Library)."""
        filename = f'{slug}.jpg'
        cached = SEED_COVERS_DIR / filename
        if cached.exists() and cached.stat().st_size >= 2000:
            return cached

        urls = []
        if isbn:
            urls.append(COVER_ISBN_API.format(isbn=isbn))
        if search:
            cover_id = self._search_cover_id(search)
            if cover_id:
                urls.append(COVER_ID_API.format(cover_id=cover_id))

        for url in urls:
            try:
                urlretrieve(url, cached)
            except (URLError, OSError) as exc:
                self.stdout.write(
                    self.style.WARNING(f'Échec téléchargement {slug} : {exc}')
                )
                continue
            if cached.exists() and cached.stat().st_size >= 2000:
                return cached
            if cached.exists():
                cached.unlink()

        self.stdout.write(
            self.style.WARNING(
                f'Couverture introuvable pour {slug}'))
        return None

    def _search_cover_id(self, query: str) -> int | None:
        url = SEARCH_API.format(query=urllib.parse.quote(query))
        try:
            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read())
        except (URLError, OSError, json.JSONDecodeError):
            return None
        docs = data.get('docs') or []
        if not docs:
            return None
        return docs[0].get('cover_i')
