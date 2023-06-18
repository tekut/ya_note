from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TEXT = 'Note text'
    SLUG = 'slug'
    TITLE = 'title'
    TEXT = 'text'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.url = reverse('notes:add')
        cls.success_url = reverse('notes:success')
        cls.form_data = {'title': cls.TITLE,
                         'text': cls.NOTE_TEXT,
                         'slug': cls.SLUG,
                         'author': cls.auth_client}

    def test_anonymous_user_cant_create_note(self):
        '''Анонимный пользователь не может создать заметку'''
        self.client.post(self.url, data=self.form_data)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_can_create_note(self):
        '''Залогиненный пользователь может создать заметку'''
        response = self.auth_client.post(self.url,
                                         data=self.form_data,
                                         follow=True,
                                         )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        self.assertRedirects(response, reverse('notes:success'))


class TestNoteEditDelete(TestCase):
    NOTE_TEXT = 'Note text'
    NEW_NOTE_TEXT = 'New note text'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.done_url = reverse('notes:success')
        cls.reader = User.objects.create(username='Reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Title',
            author=cls.author,
            text=cls.NOTE_TEXT
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.new_data = {'text': cls.NEW_NOTE_TEXT,
                        'title': 'New Title',
                        }

    def test_author_can_delete_note(self):
        '''Пользователь может удалять свои заметки'''
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)

    def test_user_cant_delete_note_of_another_user(self):
        '''Пользователь не может удалять чужие заметки'''
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)

    def test_author_can_edit_note(self):
        '''Пользователь может редактировать свои заметки'''
        self.assertRedirects(
            self.author_client.post(self.edit_url, data=self.new_data),
            self.done_url,
            )
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        '''Пользователь не может редактировать чужие заметки'''
        response = self.reader_client.post(self.edit_url, data=self.new_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)


class TestNoteSlugUniqueness(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_duplicate_slug(self):
        '''Невозможно создать две заметки с одинаковым slug'''
        response = self.author_client.post(
            reverse('notes:add'),
            data={'title': 'Note 1',
                  'text': 'First note',
                  'slug': 'note-slug'}
        )
        self.assertEqual(response.status_code, 302)

        response = self.author_client.post(
            reverse('notes:add'),
            data={'title': 'Note 2',
                  'text': 'Second note',
                  'slug': 'note-slug'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, WARNING)


class TestNoteAutoSlug(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

    def test_auto_generate_slug(self):
        '''Если не заполнен slug, то он формируется автоматически'''
        title = 'Пример заметки без заполненного slug'
        expected_slug = slugify(title)
        response = self.author_client.post(
            reverse('notes:add'),
            data={'title': title, 'text': 'Text without slug'}
        )
        self.assertEqual(response.status_code, 302)
        note = Note.objects.get(title=title)
        self.assertEqual(note.slug, expected_slug)
