from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

import os
import json
import uuid
import shutil
import subprocess
from random import randint
from shutil import copyfile
from datetime import timedelta

from django.utils import timezone

from base.models import Version
from crashsubmit.models import UploadedCrash
from symbols.handler import SymbolsUploadHandler
from processor.models import CrashCount

class Command(BaseCommand):

    help = "Initialize the database with data."

    def _test_minidump_stackwalk(self):
        minidump_stackwalk = settings.MINIDUMP_STACKWALK
        try:
            return subprocess.call([minidump_stackwalk, "-m", ""])
        except:
            return False

    def _clear(self):
        Version.objects.all().delete()

    def _move_symbols(self):
        symbol_location = settings.SYMBOL_LOCATION
        shutil.rmtree(symbol_location)
        if not os.path.exists(symbol_location):
            os.makedirs(symbol_location)

        symbol_file = os.path.join(settings.BASE_DIR, "setup", "symbols", "symbols.zip")
        handler = SymbolsUploadHandler()
        data = {'version':'1.2.3.4','platform':'linux', 'system':True}
        handler.process(data, symbol_file)

    def _create_versions(self):
        version_file = os.path.join(settings.BASE_DIR, "setup", "versions", "version.json")
        with open(version_file, "r") as f:
            content = json.load(f)
        version_list = content["versions"]
        for version in version_list:
            version
            Version.objects.create_from_string(version["name"], featured = version.get("featured", False))

    def _create_chart_data(self):
        days = 7
        featured_versions = Version.objects.filter(featured=True)
        for i in range(1, days):
            for version in featured_versions:
                date = timezone.now().today() - timedelta(days=(days + 1 - i))
                crash_count = CrashCount.objects.get_or_create(version=version, date=date)
                crash_count[0].count = randint(1,100)
                crash_count[0].save()

    def _upload_crash_reports(self):
        crash_report_dir = os.path.join(settings.BASE_DIR, "setup", "crash_reports")
        for file in os.listdir(crash_report_dir):
            if file.endswith(".json"):
                print(file)
                with open(os.path.join(crash_report_dir, file), "r") as f:
                    content = json.load(f)
                    version_string = content["Version"]
                    file_path = content["File"]
                    del content["Version"]
                    del content["File"]

                    crash_id = uuid.uuid4()
                    tmp_upload_path = settings.TEMP_UPLOAD_DIR
                    target_path = os.path.join(tmp_upload_path,file_path)
                    print(target_path)
                    copyfile(os.path.join(crash_report_dir, file_path), target_path)

                    model_version = Version.objects.get_by_version_string(version_string)[0]

                    new_crash = UploadedCrash(crash_path=target_path, crash_id=str(crash_id),
                           version=model_version, additional_data = json.dumps(content) )
                    new_crash.save()

    def handle(self, *args, **kwargs):
        setup_dir = os.path.join(settings.BASE_DIR, "setup")
        self.stdout.write(setup_dir)

        if not self._test_minidump_stackwalk():
            self.stderr.write("minidump_stackwalk does not work")
            return

        self._clear()
        self._move_symbols()
        self._create_versions()
        self._upload_crash_reports()
        self._create_chart_data()
