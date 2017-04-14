from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

import os
import json
import subprocess
from base.models import Version

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
        symbol_dir = os.path.join(settings.BASE_DIR, "setup", "symbols")
        pass

    def _create_versions(self):
        version_file = os.path.join(settings.BASE_DIR, "setup", "versions", "version.json")
        with open(version_file, "r") as f:
            content = json.load(f)
        version_list = content["versions"]
        for version in version_list:
            version
            Version.objects.create_from_string(version["name"], featured = version.get("featured", False))

    def _upload_crash_reports(self):
        crash_report_dir = os.path.join(settings.BASE_DIR, "setup", "crash_reports")
        pass

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
