# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from .processor import MinidumpProcessor

from uwsgidecoratorsfallback import spool

import logging

logger = logging.getLogger(__name__)

@spool
def do_process_uploaded_crash(*args, **kwargs):
    minproc = MinidumpProcessor()
    minproc.process(kwargs['crash_id'])
    logger.info('processed: %s' % (kwargs['crash_id']))

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
