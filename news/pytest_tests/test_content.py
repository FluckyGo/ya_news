import pytest

from django.urls import reverse
from django.conf import settings


@pytest.mark.django_db
def test_news_count(client, created_news):
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, created_news_with_timedelta):
    home_url = reverse('news:home')
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, created_comment_with_timedelta, news):
    detail_url = reverse('news:detail', args=(news.pk,))
    response = client.get(detail_url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client',
    (
        (pytest.lazy_fixture('admin_client')),
        (pytest.lazy_fixture('author_client'))
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('pk_news')),
    )
)
def test_parametrized_client_has_from(parametrized_client, name, args):
    url = reverse(name, args=args)
    response = parametrized_client.get(url)
    assert 'form' in response.context
