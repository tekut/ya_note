from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.note = Note.objects.create(title='title',
                                       text='text',
                                       author=cls.author,
                                       )
        cls.reader = User.objects.create(username='Reader')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.url = reverse('notes:add', None)

#    def test_note_list_page_show_correct_context(self):
#        response = self.client.get(self.NOTES_URL)
#        object_list = response.context['object_list']
#        self.assertIn(self.note, object_list)
