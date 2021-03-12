from django.db import models
from django.contrib.auth.models import User, Group, Permission, ContentType
from django.test import TestCase
from .admin import CustomUserAdmin, CustomGroupAdmin, permission_id_str


permission_full_name = lambda p: f"{p.content_type.app_label}.{p.codename}"

class CreateTestPermissionUsersAndGroupMixin:
    PASS = 'pass'

    @classmethod
    def get_permissions(cls, permissions):
        return Permission.objects.annotate(
            permission_id_str=permission_id_str
        ).filter(permission_id_str__in=permissions)

    @classmethod
    def setUpTestData(cls):
        cls.users = []
        cls.permissions = []
        cls.groups = [
            Group.objects.create(name=name)
            for name in ('level1', 'level2', 'level3')
        ]

        ct = ContentType.objects.get_for_model(Group)
        for n, group in enumerate(cls.groups):
            can_read = Permission.objects.create(
                codename=f"can_read_{group.name}_vars",
                name=f"Can read {group.name} variables",
                content_type=ct,
            )
            can_write = Permission.objects.create(
                codename=f"can_write_{group.name}_vars",
                name=f"Can write {group.name} variables",
                content_type=ct,
            )
            cls.permissions.append(can_read)
            cls.permissions.append(can_write)
            group.permissions.add(*cls.permissions)

            if n >= 0:
                group.permissions.add(*cls.get_permissions([
                    'auth.view_group',
                    'auth.view_user',
                ]))

            if n >= 1:
                group.permissions.add(*cls.get_permissions([
                    'auth.change_group',
                    'auth.change_user',
                ]))

            if n >= 2:
                group.permissions.add(*cls.get_permissions([
                    'auth.add_group',
                    'auth.add_user',
                    'auth.delete_group',
                    'auth.delete_user',
                ]))

            user = User.objects.create_user(
                username=f"{group.name}_user",
                password=cls.PASS,
                is_staff=True,
            )
            user.groups.add(group)
            cls.users.append(user)

    def test_superuser_can_do_everything(self):
        admin = User.objects.create_superuser('admin', 'admin@test.com', self.PASS)
        self.client.login(username=admin.username, password=self.PASS)

        response = self.client.get(self.URL, follow=True)
        self.assertEqual(response.status_code, 200)

        for permission in self.permissions:
            perm_name = permission_full_name(permission)
            self.assertTrue(admin.has_perm(perm_name))


class ViewPermissionsTestCaseMixin:
    URL  = ''
    VIEW = ''

    def test_not_logged_users_are_redirected_to_login_view(self):
        response = self.client.get(self.URL, follow=True)
        self.assertRedirects(response, f'/admin/login/?next={self.URL}')

    def test_staff_users_can_view(self):
        user = self.users[0]
        self.assertTrue(user.is_staff)
        self.assertTrue(user.has_perm(self.VIEW))

        self.client.login(username=user.username, password=self.PASS)
        response = self.client.get(self.URL, follow=True)
        self.assertEqual(response.status_code, 200)

    def test_no_staff_users_cannot_view(self):
        user = User.objects.create_user(
            username="user",
            password=self.PASS,
            is_staff=False,
        )
        self.client.login(username=user.username, password=self.PASS)
        # https://github.com/django/django/commit/3c447b108ac70757001171f7a4791f493880bf5b
        response = self.client.get(self.URL, follow=True, HTTP_ACCEPT_LANGUAGE='en')
        self.assertRedirects(response, f'/admin/login/?next={self.URL}')
        self.assertContains(response, "are not authorized to access this page")


class AdminGroupPermissionsTestCase(
    CreateTestPermissionUsersAndGroupMixin,
    ViewPermissionsTestCaseMixin,
    TestCase,
):
    URL = '/admin/auth/group/'
    VIEW = 'auth.view_group'
    CHANGE = 'auth.change_group'

    def _user_has_group_permissions(user, group):
        user_perm = user.get_user_permissions()
        group_perm = (
            f""
            for p in group.permissions.all()
        )
        return all(p in user_perm for p in edited_perm)

    def test_members_can_edit_groups(self):
        user = self.users[1]
        group = self.groups[1]
        self.assertTrue(user.has_perm(self.CHANGE))
        self.assertTrue(user.groups.filter(name=group.name).exists()) # is member
        self.client.login(username=user.username, password=self.PASS)
        response = self.client.get(f"{self.URL}{group.pk}/change/", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_users_with_same_permissions_can_edit_groups(self):
        user = self.users[1]
        group = self.groups[0]
        self.assertTrue(user.has_perm(self.CHANGE))
        # TODO assert user has same permissions
        self.assertFalse(user.groups.filter(name=group.name).exists()) # is not member
        self.client.login(username=user.username, password=self.PASS)
        response = self.client.get(f"{self.URL}{group.pk}/change/", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_users_with_less_permissions_cannot_edit_groups(self):
        user = self.users[1]
        group = self.groups[2]
        self.assertTrue(user.has_perm(self.CHANGE))
        # TODO assert user has less permissions
        self.assertFalse(user.groups.filter(name=group.name).exists()) # is not member
        self.client.login(username=user.username, password=self.PASS)
        response = self.client.get(f"{self.URL}{group.pk}/change/", follow=True)
        self.assertEqual(response.status_code, 403)


class AdminUserPermissionsTestCase(
    CreateTestPermissionUsersAndGroupMixin,
    ViewPermissionsTestCaseMixin,
    TestCase,
):
    URL = '/admin/auth/user/'
    VIEW = 'auth.view_user'
    CHANGE = 'auth.change_user'

    @classmethod
    def _editor_has_edited_permissions(cls, editor, edited):
        editor_perm = editor.get_user_permissions()
        edited_perm = edited.get_user_permissions()
        return all(p in editor_perm for p in edited_perm)

    def test_users_with_same_permissions_can_edit_users(self):
        editor = self.users[1]
        edited = self.users[0]
        self.assertTrue(editor.has_perm(self.CHANGE))
        self.assertTrue(self._editor_has_edited_permissions(editor, edited))
        self.client.login(username=editor.username, password=self.PASS)
        response = self.client.get(f"{self.URL}{edited.pk}/change/", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_users_with_less_permissions_cannot_edit_users(self):
        editor = self.users[1]
        edited = self.users[2]
        self.assertTrue(editor.has_perm(self.CHANGE))
        self.assertFalse(self._editor_has_edited_permissions(editor, edited))
        self.client.login(username=editor.username, password=self.PASS)
        response = self.client.get(f"{self.URL}{edited.pk}/change/", follow=True)
        self.assertEqual(response.status_code, 403)