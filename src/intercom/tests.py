import datetime
import pytz
from django.test import TestCase, Client
from django.utils import timezone
from . import models

class MembershipTypeModelTest (TestCase):

    def setUp(self):
        models.MembershipType.objects.all().delete()

    def test_creates_slug_from_name(self):
        mt = models.MembershipType(name='Hello, World!')
        mt.save()
        self.assertEqual(mt.slug, 'hello-world')


class MemberModelTest (TestCase):

    def setUp(self):
        models.Member.objects.all().delete()
        models.MembershipType.objects.all().delete()
        models.TimeRule.objects.all().delete()

    def test_access_updates_last_accessed_time(self):
        mt = models.MembershipType.objects.create(name='Basic')
        m = models.Member(name='Mjumbe Poe', membership=mt, last_access=timezone.datetime(1, 1, 1, 0, 0, 0, 0, pytz.utc))
        m.save()

        time_now = timezone.now()
        self.assertLess(m.last_access, time_now)

        m.access()

        m = models.Member.objects.get(name='Mjumbe Poe')
        self.assertGreaterEqual(m.last_access, time_now)

    def test_access_checks_work(self):
        mt = models.MembershipType.objects.create(name='Basic')
        mt_dummy = models.MembershipType.objects.create(name='Dummy')
        m = models.Member(name='Mjumbe Poe', membership=mt, last_access=timezone.datetime(1, 1, 1, 0, 0, 0, 0, pytz.utc))

        r1 = models.TimeRule.objects.create(membership=mt_dummy, day='*', is_open=True)
        r2 = models.TimeRule.objects.create(membership=mt_dummy, day='mf', is_open=True)
        r3 = models.TimeRule.objects.create(membership=mt_dummy, day='mf', is_open=True, closing_time=datetime.time(18, 0, 0))
        r4 = models.TimeRule.objects.create(membership=mt_dummy, day='0', is_open=True, closing_time=datetime.time(20, 0, 0))
        r5 = models.TimeRule.objects.create(membership=mt_dummy, day='0', is_open=True, closing_time=datetime.time(18, 0, 0))
        r6 = models.TimeRule.objects.create(membership=mt_dummy, day='1', is_open=True, closing_time=datetime.time(20, 0, 0))
        dt = timezone.datetime(2012, 6, 11, 19, 30, 0, 0, timezone.get_current_timezone())

        self.assert_(not m.is_allowed_access(dt))

        r1.membership = mt; r1.save()
        self.assert_(m.is_allowed_access(dt))
        r1.membership = mt_dummy; r1.save()

        r2.membership = mt; r2.save()
        self.assert_(m.is_allowed_access(dt))
        r2.membership = mt_dummy; r2.save()

        r3.membership = mt; r3.save()
        self.assert_(not m.is_allowed_access(dt))
        r3.membership = mt_dummy; r3.save()

        r4.membership = mt; r4.save()
        self.assert_(m.is_allowed_access(dt))
        r4.membership = mt_dummy; r4.save()

        r5.membership = mt; r5.save()
        self.assert_(not m.is_allowed_access(dt))
        r5.membership = mt_dummy; r5.save()

        r6.membership = mt; r6.save()
        self.assert_(not m.is_allowed_access(dt))
        r6.membership = mt_dummy; r6.save()
