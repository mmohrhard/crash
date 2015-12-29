# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from django.db import models

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
        filter_params = Version.get_filter_params(version)
        res = res.filter(**filter_params)
        return res

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
    @staticmethod
    def get_filter_params(version, prefix=''):
        split_versions = version.split('.')
        res = {}
        if len(split_versions) >= 1:
            res[prefix + 'major_version'] = split_versions[0]

        if len(split_versions) >= 2:
            res[prefix + 'minor_version'] = split_versions[1]

        if len(split_versions) >= 3:
            res[prefix + 'micro_version'] = split_versions[2]

        if len(split_versions) >= 4:
            res[prefix + 'patch_version'] = split_versions[3]

        return res

    # custom manager
    objects = VersionManager()

    class Meta:
        unique_together = ('product', 'major_version',
                'minor_version', 'micro_version', 'patch_version')

# vim:set shiftwidth=4 softtabstop=4 expandtab: */from __future__ import unicode_literals
