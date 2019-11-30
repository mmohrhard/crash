# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import subprocess, re, json
import logging
import os

from .models import ProcessedCrash

from django.db import IntegrityError
from django.conf import settings

from crashsubmit import models as submit_model

logger = logging.getLogger(__name__)

class MinidumpProcessor(object):
    def __init__(self):
        self.minidump_stackwalker = settings.MINIDUMP_STACKWALK
        self.symbol_path = settings.SYMBOL_LOCATION

    def process(self, crash_id):

        if len(ProcessedCrash.objects.filter(crash_id=crash_id)) != 0:
            logger.error("trying to process the same uploaded crash twice")
            raise IntegrityError('object already in db')

        original_crash_report = submit_model.UploadedCrash.objects.get(crash_id=crash_id)
        path = original_crash_report.crash_path

        with open(os.devnull, 'w') as devnull:
            output = subprocess.check_output([self.minidump_stackwalker, "-m", path, self.symbol_path], stderr=devnull)

        modules = []
        os_version = []
        cpu = []
        crash = []
        frames = []
        thread_pattern = re.compile(r'^(?P<thread_id>\d+)\|')
        for line in output.splitlines():
            if line.startswith('OS'):
                os_version.append(line)
            elif line.startswith('CPU'):
                cpu.append(line)
            elif line.startswith('GPU'):
                pass
            elif line.startswith('Crash'):
                crash.append(line)
            elif line.startswith('Module'):
                modules.append(line)
            elif line is '':
                continue
            else:
                frames.append(line)

        self.processed_crash = ProcessedCrash()

        # Upload the original info from the UploadedCrash model
        # We might want to delete the UploadedCrash entry
        self.processed_crash.crash_id = original_crash_report.crash_id
        self.processed_crash.version = original_crash_report.version
        self.processed_crash.additional_data = original_crash_report.additional_data
        self.processed_crash.upload_time = original_crash_report.upload_time

        self.processed_crash.raw = output
        self.processed_crash.set_modules_to_model(modules)
        self._parse_crash(crash)
        self._parse_threads(frames)
        self._parse_os(os_version)
        self._parse_cpu(cpu)

        self.processed_crash.save()
        self.processed_crash = None

    def _parse_os(self, os_version):
        # ['OS|Linux|0.0.0 Linux 3.16.7-24-desktop #1 SMP PREEMPT Mon Aug 3 14:37:06 UTC 2015 (ec183cc) x86_64']
        assert(len(os_version) == 1)
        parsed_line = os_version[0].split('|')
        os_name = parsed_line[1]
        os_detail = parsed_line[2]
        self.processed_crash.os_detail = os_detail
        self.processed_crash.set_view_os_name_to_model(os_name)
        self.processed_crash.set_view_os_detail_parsed_to_model(os_detail)

    def _parse_frames(self, frames):
        threads = {}
        for frame in frames:
            parsed_line = frame.split('|')
            thread_id = parsed_line[0]
            frame_id = parsed_line[1]
            lib_name = parsed_line[2]
            function_name = parsed_line[3]
            file_name = parsed_line[4]
            if file_name.startswith("/home/buildslave/source/libo-core/"):
                file_name = file_name.replace("/home/buildslave/source/libo-core/", "")
            line_number = parsed_line[5]
            offset = parsed_line[6]

            if thread_id not in threads:
                threads[thread_id] = []

            threads[thread_id].append({'lib_name': lib_name, 'frame_id': frame_id, \
                    'function': function_name, 'file': file_name, \
                    'line': line_number, 'offset': offset})

        return threads

    def _parse_threads(self, frames):
        # 0|0|libsclo.so|crash|/home/moggi/devel/libo9/sc/source/ui/docshell/docsh.cxx|434|0x4
        thread_list = {}
        threads = self._parse_frames(frames)

        for thread_id, thread in threads.iteritems():
            thread_list[thread_id] = json.dumps(thread)

        self.processed_crash.set_thread_to_model(thread_list)

    def _parse_cpu(self, cpu):
        # CPU|amd64|family 6 model 30 stepping 5|4
        assert(len(cpu) == 1)
        parsed_line = cpu[0].split('|')
        architecture = parsed_line[1]
        cpu_info = parsed_line[2]
        self.processed_crash.cpu_info = cpu_info
        self.processed_crash.cpu_architecture = architecture

    def _parse_crash(self, crash):
        # Crash|SIGSEGV|0x0|0
        assert(len(crash) == 1)
        parsed_line = crash[0].split('|')

        cause = parsed_line[1]
        address = parsed_line[2]
        thread_id = parsed_line[3]
        self.processed_crash.crash_cause = cause
        self.processed_crash.crash_address = address
        self.processed_crash.crash_thread = thread_id

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
