# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

import subprocess, re

from .models import ProcessedCrash

from django.db import IntegrityError

from crashsubmit import models as submit_model

class MinidumpProcessor(object):
    def __init__(self):
        # TODO: moggi: get these values from the config
        self.minidump_stackwalker = 'minidump_stackwalk'
        self.symbol_path = '/home/moggi/devel/libo9/instdir/program/symbols/'

    def process(self, crash_id):

        original_crash_report = submit_model.UploadedCrash.objects.get(crash_id=crash_id)
        path = original_crash_report.crash_path
        if len(ProcessedCrash.objects.filter(crash_id=crash_id)) != 0:
            raise IntegrityError('object already in db')

        output = subprocess.check_output([self.minidump_stackwalker, "-m", path, self.symbol_path])

        content = {}
        content['Modules'] = []
        content['Thread'] = {}
        thread_pattern = re.compile(r'^(?P<thread_id>\d+)\|')
        for line in output.splitlines():
            if line.startswith('OS'):
                content['OS'] = [line]
            elif line.startswith('CPU'):
                content['CPU'] = [line]
            elif line.startswith('Crash'):
                content['Crash'] = [line]
            elif line.startswith('Module'):
                content['Modules'].append(line)
            elif len(line.strip()) == 0:
                pass
            elif thread_pattern.search(line) != None:
                thread_id = thread_pattern.search(line).group('thread_id')
                if thread_id not in content['Thread']:
                    content['Thread'][thread_id] = []
                content['Thread'][thread_id].append(line)

        self.processed_crash = ProcessedCrash()

        # Upload the original info from the UploadedCrash model
        # We might want to delete the UploadedCrash entry
        self.processed_crash.crash_id = original_crash_report.crash_id
        self.processed_crash.version = original_crash_report.version
        self.processed_crash.device_id = original_crash_report.device_id
        self.processed_crash.vendor_id = original_crash_report.vendor_id
        self.processed_crash.upload_time = original_crash_report.upload_time

        self.processed_crash.raw = output
        self.processed_crash.set_modules_to_model(content['Modules'])
        self._parse_threads(content['Thread'])
        self._parse_os(content['OS'])
        self._parse_cpu(content['CPU'])
        self._parse_crash(content['Crash'])

        self.processed_crash.save()
        self.processed_crash = None

    def _parse_os(self, os):
        # ['OS|Linux|0.0.0 Linux 3.16.7-24-desktop #1 SMP PREEMPT Mon Aug 3 14:37:06 UTC 2015 (ec183cc) x86_64']
        assert(len(os) == 1)
        parsed_line = os[0].split('|')
        os_name = parsed_line[1]
        os_detail = parsed_line[2]
        self.processed_crash.os_detail = os_detail
        self.processed_crash.set_view_os_name_to_model(os_name)

    def _parse_frames(self, frames):
        frame_pattern = re.compile(r'^(?P<thread_id>\d+)\|(?P<frame_id>\d+)\|(?P<lib_name>[^|]+)\|(?P<function_name>[^!]*)\|(?P<file>[^|]*)\|(?P<line_number>\d*)\|(?P<offset>[^|]*)')
        frame_list = []
        for frame in frames:
            parsed_line = frame_pattern.search(frame)
            if not parsed_line:
                print(frame)
            else:
                lib_name = parsed_line.group('lib_name')
                frame_id = parsed_line.group('frame_id')
                function_name = parsed_line.group('function_name')
                file_name = parsed_line.group('file')
                line_number = parsed_line.group('line_number')
                offset = parsed_line.group('offset')
                frame_list.append({'lib_name': lib_name, 'frame_id': frame_id, \
                        'function': function_name, 'file': file_name, \
                        'line': line_number, 'offset': offset})

        return frame_list

    def _parse_threads(self, threads):
        # 0|0|libsclo.so|crash|/home/moggi/devel/libo9/sc/source/ui/docshell/docsh.cxx|434|0x4
        thread_list = {}
        for thread_id, frames in threads.iteritems():
            parsed_frames = self._parse_frames(frames)
            thread_list[thread_id] = parsed_frames

        # TODO: moggi: fix the wrong crash_thread parameter
        self.processed_crash.set_thread_to_model(thread_list, 0)

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
