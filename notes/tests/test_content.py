from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestNoteContent(TestCase):
    def test_user_notes_only_in_object_list(self):
        '''В список заметок одного пользователя не попадают заметки другого'''
        user1 = User.objects.create(username='User1')
        user2 = User.objects.create(username='User2')
        note1 = Note.objects.create(title='Note 1',
                                    text='Note 1 text',
                                    author=user1,
                                    )
        note2 = Note.objects.create(title='Note 2',
                                    text='Note 2 text',
                                    author=user2,
                                    )
        url = reverse('notes:list')
        self.client.force_login(user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(note1, response.context['object_list'])
        self.assertNotIn(note2, response.context['object_list'])


class TestNoteContent2(TestCase):
    def test_pages_contains_form(self):
        """На страницы создания и редактирования заметки передаются формы"""
        self.author = User.objects.create(username='Author')
        self.author_client = Client()
        self.author_client.force_login(self.author)
        note = Note.objects.create(title='Test Note',
                                   text='This is a test note',
                                   author=self.author,
                                   )
        for url in (reverse('notes:add'),
                    reverse('notes:edit', args=[note.slug])
                    ):
            with self.subTest(url=url):
                self.assertIsInstance(
                    self.author_client.get(url).context['form'],
                    NoteForm,
                )
