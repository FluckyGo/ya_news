from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, arguments',
    [('news:home', None),
     #  ('news:detail', pytest.lazy_fixture('pk_news')),
     ('users:login', None),
     ('users:logout', None),
     ('users:signup', None)]
)
def test_home_availability_for_anonymous_user(name, arguments, client):
    url = reverse(name, args=arguments)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    (
        ('news:delete'),
        ('news:edit')
    )
)
def test_pages_availability_for_auth_user(author_client, name, comment):
    url = reverse(name, args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    (
        ('news:delete'),
        ('news:edit')
    )
)
def test_pages_availability_for_different_users(parametrized_client, name, comment, expected_status):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status
