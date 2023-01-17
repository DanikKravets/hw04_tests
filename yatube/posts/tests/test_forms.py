from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='TestName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='Test Group',
            slug='test_group',
        )

    def test_creation_post(self):
        """Проверка создания поста"""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'New post text into form',
            'group': self.group.id,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        error1 = 'Данные поста не совпадают'
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTrue(Post.objects.filter(
            text='New post text into form',
            group=self.group.id,
            author=self.user
        ).exists(), error1)

        error2 = 'Пост не добавлен в базу данных'
        self.assertEqual(Post.objects.count(), (posts_count + 1), error2)

    def test_post_edit(self):
        """Проверка прав редактирования"""
        self.post = Post.objects.create(
            text='Test text',
            author=self.user,
            group=self.group,
        )

        post_v1 = self.post

        self.group2 = Group.objects.create(
            title='Test Group 2',
            slug='test_group_2',
            description='test description',
        )

        form_data = {
            'text': 'New test text',
            'group': self.group2.id,
        }

        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': post_v1.id}
            ),
            data=form_data,
            follow=True,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        error1 = 'Данные обновленного поста не совпадают'

        self.assertTrue(Post.objects.filter(
            text='New test text',
            group=self.group2.id,
            author=self.user,
            pub_date=self.post.pub_date,
        ).exists(), error1)

        error1 = 'Пользователь не может обновить текст поста'
        self.assertNotEqual(post_v1.text, form_data['text'], error1)
        error2 = 'Пользователь не может изменить группу поста'
        self.assertNotEqual(post_v1.group, form_data['group'], error2)

    def test_group_null(self):
        """Проверка возможности не указывать группу"""
        self.post = Post.objects.create(
            text='Test text',
            author=self.user,
            group=self.group,
        )
        post_v1 = self.post

        form_data = {
            'text': 'Edited post text',
            'group': '',
        }

        response = self.authorized_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': post_v1.id}
            ),
            data=form_data,
            follow=True,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        error = 'Пользователь не может оставить группу пустой'
        self.assertNotEqual(post_v1.group, form_data['group'], error)

    def test_redirect_guest_client(self):
        """проверка редиректа неавторизованного пользователя"""
        self.post = Post.objects.create(
            text='Test text',
            author=self.user,
            group=self.group,
        )

        form_data = {
            'text': 'Edited post text',
            'group': self.group.id
        }

        response = self.guest_client.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

    def test_guest_client_cant_create(self):
        """Проверка запрета на coздание постов"""
        """неавторизованным пользователем"""
        posts_count = Post.objects.count()

        form_data = {
            'text': 'Post text',
            'group': self.group.id
        }

        response = self.guest_client.post(
            reverse(
                'posts:post_create'
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        error = 'Неавторизованный пользователь смог создать пост'
        self.assertEqual(Post.objects.count(), posts_count, error)
