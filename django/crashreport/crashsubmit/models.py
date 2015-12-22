# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Product(models.Model):
    product_name = models.CharField(max_length=50,
            unique=True,
            primary_key=True,
            help_text='The name of the product.')

    def __str__(self):
        return self.product_name

class VersionManager(models.Manager):
    def get_by_version_string(self, version):
        res = self.get_queryset()
        major_version, minor_version, micro_version, patch_version = \
                self._split_version_string(version)

        if major_version:
            res = res.filter(major_version=major_version)

        if minor_version:
            res = res.filter(minor_version=minor_version)

        if micro_version:
            res = res.filter(micro_version=micro_version)

        if patch_version:
            res = res.filter(patch_version=patch_version)

        return res

    def _split_version_string(self, version):
        split_version = version.split('.')
        return split_version

class Version(models.Model):
    product = models.ForeignKey(Product)
    major_version = models.SmallIntegerField()
    minor_version = models.SmallIntegerField()
    micro_version = models.SmallIntegerField()
    patch_version = models.SmallIntegerField()

    featured = models.BooleanField(
            default=False)

    def __str__(self):
        return str(self.product) + " Version: " + self.str_without_product()

    def str_without_product(self):
        return str(self.major_version) + "." + \
                str(self.minor_version) + "." + str(self.micro_version) + "." + str(self.patch_version)

    # custom manager
    objects = VersionManager()

    class Meta:
        unique_together = ('product', 'major_version',
                'minor_version', 'micro_version', 'patch_version')

class UploadedCrash(models.Model):
    # TODO: moggi: change to UUIDField
    crash_id = models.CharField(max_length=50,
            unique=True)
    # TODO: moggi: change to FilePathField
    crash_path = models.CharField(max_length=200, help_text='The path to the original crash report on the file system.')
    upload_time = models.DateTimeField(auto_now_add=True)
    version = models.ForeignKey(Version)
    device_id = models.CharField(max_length=100,
            null=True)
    vendor_id = models.CharField(max_length=100,
            null=True)

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
