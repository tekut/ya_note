from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    def test_home_page(self):
        '''Главная страница доступна анонимному пользователю.'''
        url = reverse('notes:home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability(self):
        '''Страницы регистрации, входа и выхода из учетки доступны всем.'''
        urls = (
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель простой')
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст'
        )

    def test_availability_for_comment_edit_and_delete(self):
        '''Страницы заметки, удаления и ред. доступны только автору'''
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        '''Анонимный пользователь перенаправляется на страницу логина'''
        login_url = reverse('users:login')
        for name in ('notes:detail',
                     'notes:edit',
                     'notes:delete',
                     ):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

        for name in ('notes:list',
                     'notes:success',
                     'notes:add',
                     ):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)


class TestAuthenticatedUserPages(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='testuser')
        cls.user.set_password('testpassword')
        cls.user.save()

    def setUp(self):
        self.client.login(username='testuser', password='testpassword')

    def test_pages_availability_authenticated(self):
        '''Аутентифицированному пользователю доступен список заметок,
страница успешного добавления заметки,
страница добавления новой заметки.'''
        for name in ('notes:list', 'notes:add', 'notes:success'):
            with self.subTest(user=User, name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
