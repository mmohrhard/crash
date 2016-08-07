# -*- Mode: python; tab-width: 4; indent-tabs-mode: nil; c-basic-offset: 4 -*- */
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#

from .processor import MinidumpProcessor

from uwsgidecoratorsfallback import spool

from subprocess import CalledProcessError

import logging

logger = logging.getLogger(__name__)

@spool
def do_process_uploaded_crash(env):
    minproc = MinidumpProcessor()
    try:
        minproc.process(env['crash_id'])
    except CalledProcessError as e:
        logger.warn('error processing: %s with error %s'%(env['crash_id'], str(e)))
        return 0
    logger.info('processed: %s' % (env['crash_id']))
    return -2

# vim:set shiftwidth=4 softtabstop=4 expandtab: */
