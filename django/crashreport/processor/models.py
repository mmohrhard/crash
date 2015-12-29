# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from __future__ import unicode_literals

from django.db import models
from django.db.models import Count
from django.utils import timezone

from datetime import timedelta

from crashsubmit import models as submit_models

from base.models import Version

class CrashCountManager(models.Manager):
    def get_crash_count_processed(self, versions=None, time=None):
        query_set = self.get_crash_count(versions=versions, time=time)
        keys = set()
        data = {}
        for entry in query_set:
            date = str(entry.date)
            keys.add(date)
            version_string = entry.version.str_without_product()
            if version_string not in data:
                data[version_string] = {}
            data[version_string][date] = entry.count
        return sorted(list(keys)), data

    def get_crash_count(self, versions=None, time=None):
        res = self.get_queryset()
        if versions is not None:
            res = res.filter(version__in=versions)

        if time is not None:
            now = timezone.now()
            before = timezone.now() - timedelta(days=time)
            res = res.filter(date__range=[before, now])
        res.order_by('date')

        return res

class CrashCount(models.Model):
    version = models.ForeignKey(submit_models.Version)
    date = models.DateField()
    count = models.IntegerField()

    # custom manager
    objects = CrashCountManager()

    class Meta:
        unique_together = ('version', 'date')


class Signature(models.Model):
    signature = models.CharField(max_length=100,
            primary_key=True)

    first_observed = models.DateTimeField()

    last_observed = models.DateTimeField()

    def __str__(self):
        return self.signature

class CrashByVersionData(object):
    def __init__(self, id):
        self.all = 0
        self.win = 0
        self.lin = 0
        self.id = Signature.objects.get(signature=id)

    def getKey(item):
        return item.all

class ProcessedCrashManager(models.Manager):
    def get_top_crashes(self, version=None, time=None, limit=None):
        res = self.get_queryset()

        if version is not None:
            version_filter_params = Version.get_filter_params(version, prefix='version__')
            res = res.filter(**version_filter_params)

        if time is not None:
            target = timezone.now() - timedelta(days=time)
            res = res.filter(upload_time__gte=target)

        res = res.values('os_name', 'signature').annotate(Count('os_name'))

        data = {}
        for entry in res:
            signature = entry['signature']
            if not signature in data:
                data[signature] = CrashByVersionData(signature)
            count = entry['os_name__count']
            data[signature].all += count
            if entry['os_name'] == 'linux':
                data[signature].lin = count
            elif entry['os_name'] == 'windows':
                data[signature].win = count
        values = data.values()
        sorted(values, key=CrashByVersionData.getKey)
        if limit is not None and len(values) > limit:
            values = values[0:limit]
        return values

class ProcessedCrash(models.Model):
    # custom manager
    objects = ProcessedCrashManager()

    crash_id = models.CharField(max_length=100,
            unique=True)

    upload_time = models.DateTimeField()

    process_time = models.DateTimeField(auto_now_add=True)

    version = models.ForeignKey(Version,
            null=True)

    # Look for better solution to store dictionary
    device_id = models.CharField(max_length=100,
            null=True,
            default=None)
    vendor_id = models.CharField(max_length=100,
            null=True,
            default=None)

    # OS info
    LINUX = 'linux'
    WINDOWS = 'windows'
    OSX = 'osx'
    ANDROID = 'android'
    IOS = 'ios'
    OS_NAMES = (
            (LINUX, 'Linux'),
            (WINDOWS, 'Windows'),
            (OSX, 'OSX'),
            (ANDROID, 'Android'),
            (IOS, 'IOS')
            )
    os_name = models.CharField(max_length=10,
            choices=OS_NAMES)

    os_detail = models.CharField(max_length=100,
            default='')

    # CPU info
    cpu_architecture = models.CharField(max_length=20)

    cpu_info = models.CharField(max_length=100,
            default='')

    signature = models.ForeignKey(Signature, on_delete=models.CASCADE)

    # crash info
    crash_cause = models.CharField(max_length=35,
            default='SIGSEGV')

    crash_address = models.CharField(max_length=100,
            default='0x0')

    crash_thread = models.SmallIntegerField(
            default=0,
            help_text='The id of the thread that caused the crash')

    # modules
    modules = models.TextField()

    # TODO: moggi: look for better solutions
    # threads
    crashing_thread = models.TextField()

    threads = models.TextField()

    raw = models.TextField()

    def set_view_os_name_to_model(self, view_os_name):
        if view_os_name.lower() == ProcessedCrash.LINUX:
            self.os_name = ProcessedCrash.LINUX
        elif view_os_name.lower() == ProcessedCrash.WINDOWS:
            self.os_name = ProcessedCrash.WINDOWS
        elif view_os_name.lower() == ProcessedCrash.OSX:
            self.os_name = ProcessedCrash.OSX

    def _convert_frame(self, frame):
        text = "Frame: %s, Module: %s, Method: %s, File: %s:%s" %  (frame['frame_id'], frame['lib_name'], frame['function'], frame['file'], frame['line'])
        return text

    def _convert_frames(self, frame_list):
        text = ""
        for frame in frame_list:
            text += self._convert_frame(frame) + "\n"
        return text

    def _set_signature(self, frame_list):
        text = ""
        if len(frame_list) > 0:
            frame = frame_list[0]
            function = frame['function']
            if len(function) > 0:
                text = "%s+%s" % (function,frame['offset'])
            else:
                text = "%s+%s" % (frame['lib_name'], frame['offset'])

        signature = Signature.objects.get(signature=text)
        if signature is None:
            signature = Signature()
            signature.signature = text
            signature.first_observed = self.upload_time
            signature.last_observed = self.upload_time
        if signature.last_observed < self.upload_time:
            signature.last_observed = self.upload_time
        signature.save()
        self.signature = signature

    def set_thread_to_model(self, threads):
        main_text = ""
        for thread_id, frame_list in threads.iteritems():
            if int(thread_id) == self.crash_thread:
                self._set_signature(frame_list)
                self.crashing_thread = self._convert_frames(frame_list)
            else:
                if len(main_text) > 0:
                    main_text += "\n\n"
                main_text += "Thread %s:\n"%(thread_id) + self._convert_frames(frame_list)

        self.threads = main_text

    def set_modules_to_model(self, modules):
        self.modules = "\n".join(modules)

    def get_split_module_list(self):
        modules = self.modules.splitlines()
        ret = []
        for module in modules:
            line = module.split('|')
            module_name = line[1]
            if module_name.startswith('LC_'):
                continue
            version = line[2]
            debug_id = line[4]
            ret.append({'name':module_name,
                'version':version, 'id':debug_id})
        return ret

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
