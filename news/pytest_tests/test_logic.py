from http import HTTPStatus
import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError
from news.forms import BAD_WORDS, WARNING

from news.models import Comment


def test_user_can_create_comment(author_client, author,
                                 form_data, pk_news, news):
    url = reverse('news:detail', args=pk_news)
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, pk_news):
    url = reverse('news:detail', args=pk_news)
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, pk_news):
    url = reverse('news:detail', args=pk_news)
    bad_word_data = {
        'text': f'Some_person - Ты {BAD_WORDS[0]} и {BAD_WORDS[1]}!'
    }
    response = author_client.post(url, data=bad_word_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    assert Comment.objects.count() == 0


def test_author_can_delete_comment(author_client, pk_comment, pk_news):
    url_to_comments = reverse('news:detail', args=pk_news) + '#comments'
    response = author_client.delete(reverse('news:delete', args=pk_comment))
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(admin_client, pk_comment):
    response = admin_client.delete(reverse('news:delete', args=pk_comment))
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_author_can_edit_comment(author_client, pk_comment, pk_news,
                                 new_form_data, comment):
    url_to_comments = reverse('news:detail', args=pk_news) + '#comments'
    response = author_client.post(
        reverse('news:edit', args=pk_comment),
        data=new_form_data
    )
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == new_form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(client, pk_comment,
                                                form_data, comment):
    response = client.post(
        reverse('news:edit', args=pk_comment),
        data=form_data
    )
    assert response.status_code, HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == form_data['text']
