from django.core.files.uploadedfile import SimpleUploadedFile

from admin_smoke import tests
from testproject.testapp import admin, models


class ProjectAdminTestCase(tests.AdminTests):
    model_admin = admin.ProjectAdmin
    model = models.Project
    object_name = 'project'
    excluded_fields = ['client']

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.project = models.Project.objects.create(name='project', pid=123)
        cls.task = cls.project.task_set.create(
            name='task', attachment=SimpleUploadedFile("txt.doc", b'text'))
        cls.tag = cls.project.tags.create(name='tag')

    def transform_to_new(self, data: dict) -> dict:
        data = data.copy()
        del data['pid']
        data['name'] = 'new'
        self.reset_inline_data(data, 'task_set', 'project')
        self.reset_inline_data(
            data, 'testapp-tag-content_type-object_id', None, pk='tid')
        data['task_set-0-name'] += '_new'
        data['task_set-0-attachment'] = SimpleUploadedFile("doc.txt", b'text')
        return data

    def prepare_deletion(self):
        self.task.delete()

    def test_post_changeform_arguments(self):
        """
        Field values may be cleared or altered while performing post request.
        """
        r = self.post_changeform(erase=('name',))

        self.assertTrue(self.get_errors_from_response(r))
        self.assertEqual(r.status_code, 200)

        r = self.post_changeform(fields={'name': "new_name"})

        self.assertFalse(self.get_errors_from_response(r))
        self.assertEqual(r.status_code, 302)
        self.assert_object_fields(
            self.project,
            name="new_name")


class TaskAdminTestCase(tests.ReadOnlyAdminTests):
    """ Tests for read-only task admin."""
    model_admin = admin.TaskAdmin
    model = models.Task
    object_name = 'task'

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.project = models.Project.objects.create(name='project', pid=123)
        cls.task = cls.project.task_set.create(
            name='task', attachment=SimpleUploadedFile("txt.doc", b'text'))

    def transform_to_new(self, data: dict) -> dict:
        data['attachment'] = SimpleUploadedFile("txt.doc", b'text')
        return data
