# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from __future__ import unicode_literals

from django.db import models

from crashsubmit import models as submit_models

class ProcessedCrash(models.Model):
    crash_id = models.OneToOneField(submit_models.UploadedCrash,
            to_field = 'crash_id')

    # OS info
    LINUX = 'linux'
    WINDOWS = 'windows'
    OSX = 'osx'
    ANDROID = 'android'
    IOS = 'ios'
    OS_NAMES = (
            (LINUX, 'linux'),
            (WINDOWS, 'windows'),
            (OSX, 'osx'),
            (ANDROID, 'android'),
            (IOS, 'ios')
            )
    os_name = models.CharField(max_length=10,
            choices=OS_NAMES)

    os_detail = models.CharField(max_length=100,
            default='')

    # CPU info
    cpu_architecture = models.CharField(max_length=20)

    cpu_info = models.CharField(max_length=100,
            default='')

    signature = models.CharField(max_length=100,
            help_text='The signature(method in frame 0)')

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

    # threads
    threads = models.TextField()

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
        self.signature = text

    def set_thread_to_model(self, threads, crash_thread):
        main_text = ""
        crash_thread_text = "Crashing Thread (Thread %d):\n" % (crash_thread)
        for thread_id, frame_list in threads.iteritems():
            if int(thread_id) == crash_thread:
                self._set_signature(frame_list)
                crash_thread_text += self._convert_frames(frame_list)
            else:
                main_text += "\n\nThread %s:\n"%(thread_id) + self._convert_frames(frame_list)

        text = crash_thread_text + "\n\n" + main_text

        self.threads = text

    def set_modules_to_model(self, modules):
        text = ""
        for module in modules:
            text += "%s\n"%(module)
        self.modules = text

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
