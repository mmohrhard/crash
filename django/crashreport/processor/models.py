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
from django.db.utils import DataError

from datetime import timedelta

import json
import logging
import os

from crashsubmit import models as submit_models

from base.models import Version

logger = logging.getLogger(__name__)

module_blacklist = set()

with open(os.path.join(os.path.dirname(__file__), 'module_blacklist.txt'), 'r') as blacklist:
    module_blacklist = blacklist.read().splitlines()

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
    count = models.IntegerField(default = 0)

    # custom manager
    objects = CrashCountManager()

    class Meta:
        unique_together = ('version', 'date')

class BugReport(models.Model):
    # TODO: moggi: support different bug trackers
    bug_nr = models.IntegerField()

    fixed = models.BooleanField(default=False)

    def __str__(self):
        return "tdf#" + str(self.bug_nr)

    def get_url(self):
        return "https://bugs.documentfoundation.org/show_bug.cgi?id=" + str(self.bug_nr)

class Signature(models.Model):
    signature = models.CharField(max_length=255,
            primary_key=True)

    first_observed = models.DateTimeField()

    last_observed = models.DateTimeField()

    bugs = models.ManyToManyField(BugReport)

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
        sorted_values = sorted(values, key=CrashByVersionData.getKey)

        num_entries = len(values)
        if limit is not None and num_entries > limit:
            values = sorted_values[num_entries-limit:]

        return values

    def get_crashes_for_day(self, day, version):
        res = self.get_queryset()

        if version is not None:
            res = res.filter(version = version)

        if day is None:
            return res

        return res.filter(process_time__date = day)

    def get_crashes_to_process(self):
        processed = ProcessedCrash.objects.values_list('crash_id')
        return submit_models.UploadedCrash.objects.all().exclude(crash_id__in=processed)

    def get_crashes_for_version(self, version):
        res = self.get_queryset()
        version_filter_params = Version.get_filter_params(version, prefix='version__')
        res = res.filter(**version_filter_params)
        return res

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
    additional_data = models.TextField(default='{}')

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
    crash_cause = models.CharField(max_length=100,
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

    def __str__(self):
        return self.crash_id

    def set_view_os_name_to_model(self, view_os_name):
        if view_os_name.lower() == ProcessedCrash.LINUX:
            self.os_name = ProcessedCrash.LINUX
        elif view_os_name.lower().startswith(ProcessedCrash.WINDOWS):
            self.os_name = ProcessedCrash.WINDOWS
        elif view_os_name.lower() == ProcessedCrash.OSX:
            self.os_name = ProcessedCrash.OSX
        else:
            logger.warning("could not determine the os: " + view_os_name)

    def _convert_frames(self, frame_list):
        text = ""
        for frame in frame_list:
            text += self._convert_frames(frame) + "\n"
        return text

    def _find_frame(self, json_frame_list):
        for frame in json_frame_list:
            function = frame['lib_name']
            if function not in module_blacklist and function is not "":
                return frame

        return json_frame_list[0]

    def _set_signature(self, frame_list):
        text = ""
        json_frame_list = json.loads(frame_list)
        if len(json_frame_list) > 0:
            frame = self._find_frame(json_frame_list)
            function = frame['function']
            if len(function) > 0:
                text = function
            else:
                text = frame['lib_name']

        if len(text) is 0:
            text = "Invalid signature"
            logger.warn("could not create a valid signature for %s" % self.crash_id)

        text = text[:255] if len(text) > 255 else text
        signatures = Signature.objects.filter(signature=text)
        if len(signatures) < 1:
            signature = Signature()
            signature.signature = text
            signature.first_observed = self.upload_time
            signature.last_observed = self.upload_time
        else:
            signature = signatures[0]

        if signature.last_observed < self.upload_time:
            signature.last_observed = self.upload_time
        try:
            signature.save()
        except DataError as e:
            logger.error("error trying to save signature %s" % text)
            logger.error(str(e))
        self.signature = signature

    def set_thread_to_model(self, threads):
        other_threads = {}
        for thread_id, frame_list in threads.iteritems():
            if int(thread_id) == int(self.crash_thread):
                self._set_signature(frame_list)
                self.crashing_thread = frame_list
            else:
                other_threads[thread_id] = json.loads(frame_list)

        self.threads = json.dumps(other_threads)

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
