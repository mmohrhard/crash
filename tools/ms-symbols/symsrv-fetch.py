#!/usr/bin/env python
#
# Copyright 2016 Mozilla
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.



# This script will read a CSV of modules from Socorro, and try to retrieve
# missing symbols from Microsoft's symbol server. It honors a blacklist
# (blacklist.txt) of symbols that are known to be from our applications,
# and it maintains its own list of symbols that the MS symbol server
# doesn't have (skiplist.txt).
#
# The script also depends on having write access to the directory it is
# installed in, to write the skiplist text file.

import codecs
import config
import sys
import os
import time
import datetime
import subprocess
import io
import gzip
import shutil
import ctypes
import logging
from collections import defaultdict
from tempfile import mkdtemp
import urllib
import urlparse
import zipfile
import requests

# Just hardcoded here
MICROSOFT_SYMBOL_SERVER = 'http://msdl.microsoft.com/download/symbols/'
USER_AGENT = 'Microsoft-Symbol-Server/6.3.0.0'
MOZILLA_SYMBOL_SERVER = ('https://s3-us-west-2.amazonaws.com/'
                         'org.mozilla.crash-stats.symbols-public/v1/')

thisdir = os.path.dirname(__file__)
log = logging.getLogger()


class Win64ProcessError(Exception):
    pass


def fetch_symbol(debug_id, debug_file):
    '''
    Attempt to fetch a PDB file from Microsoft's symbol server.
    '''
    url = urlparse.urljoin(MICROSOFT_SYMBOL_SERVER,
                           os.path.join(debug_file,
                                        debug_id,
                                        debug_file[:-1] + '_'))
    r = requests.get(url,
                     headers={'User-Agent': USER_AGENT})
    if r.status_code == 200:
        return r.content
    return None


def fetch_symbol_and_decompress(tmpdir, debug_id, debug_file):
    '''
    Attempt to fetch a PDB file from Microsoft's symbol server, then
    write a decompressed version to tmpdir.
    Returns the filename if successful, or None if unsuccessful.
    '''
    data = fetch_symbol(debug_id, debug_file)
    if not data or not data.startswith(b'MSCF'):
        return None
    path = os.path.join(tmpdir, debug_file[:-1] + '_')
    with open(path, 'wb') as f:
        f.write(data)
    try:
        # Decompress it
        subprocess.check_call(['cabextract', '-L', '-d', tmpdir, path],
                              stdout=open(os.devnull, 'wb'))
        os.unlink(path)
        return os.path.join(tmpdir, debug_file.lower())
    except subprocess.CalledProcessError:
        return None


def fetch_and_dump_symbols(tmpdir, debug_id, debug_file,
                           code_id=None, code_file=None):
    pdb_path = fetch_symbol_and_decompress(tmpdir, debug_id, debug_file)
    if pdb_path is None:
        return None
    bin_path = None
    while True:
        try:
            # Dump it
            syms = subprocess.check_output(config.dump_syms_cmd + [pdb_path])
            lines = syms.splitlines()
            if not lines:
                return None
            os.unlink(pdb_path)
            if bin_path:
                os.unlink(bin_path)
            return syms
        except subprocess.CalledProcessError as e:
            if bin_path is None and e.output.splitlines()[0].split()[2] == 'x86_64':
                # Can't dump useful symbols for Win64 PDBs without binaries.
                if code_id and code_file:
                    log.debug('Fetching binary %s, %s', code_id, code_file)
                    bin_path = fetch_symbol_and_decompress(tmpdir, code_id, code_file)
                    if bin_path:
                        log.debug('Fetched binary %s', bin_path)
                    else:
                        log.warn("Couldn't fetch binary for %s, %s",
                                 code_id, code_file)
                        raise Win64ProcessError()
                    continue
                else:
                    raise Win64ProcessError()
            return None


def server_has_file(filename):
    '''
    Send the symbol server a HEAD request to see if it has this symbol file.
    TODO: moggi: Implement
    '''
    return False


def write_skiplist(skiplist):
    try:
        with open(os.path.join(thisdir, 'skiplist.txt'), 'w') as sf:
            for (debug_id, debug_file) in skiplist.iteritems():
                sf.write('%s %s\n' % (debug_id, debug_file))
    except IOError:
        log.exception('Error writing skiplist.txt')


def fetch_missing_symbols(log):
    return None


def main():
    verbose = False
    if len(sys.argv) > 1 and sys.argv[1] == '-v':
        verbose = True
        sys.argv.pop(1)

    log.setLevel(logging.DEBUG)
    urllib3_logger = logging.getLogger('urllib3')
    urllib3_logger.setLevel(logging.ERROR)
    formatter = logging.Formatter(fmt='%(asctime)-15s %(message)s',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    filelog = logging.FileHandler(filename=os.path.join(thisdir,
                                                        'symsrv-fetch.log'))
    filelog.setLevel(logging.INFO)
    filelog.setFormatter(formatter)
    log.addHandler(filelog)

    if verbose:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(formatter)
        log.addHandler(handler)
        verboselog = logging.FileHandler(filename=os.path.join(thisdir,
                                                               'verbose.log'))
        verboselog.setFormatter(formatter)
        log.addHandler(verboselog)

    log.info('Started')

    # Symbols that we know belong to us, so don't ask Microsoft for them.
    try:
        blacklist = set(
            l.rstrip() for l in open(
                os.path.join(
                    thisdir,
                    'blacklist.txt'),
                'r').readlines())
    except IOError:
        blacklist = set()
    log.debug('Blacklist contains %d items' % len(blacklist))

    # Symbols that we know belong to Microsoft, so don't skiplist them.
    try:
        known_ms_symbols = set(
            l.rstrip() for l in open(
                os.path.join(
                    thisdir,
                    'known-microsoft-symbols.txt'),
                'r').readlines())
    except IOError:
        known_ms_symbols = set()
    log.debug('Known Microsoft symbols contains %d items'
              % len(known_ms_symbols))

    # Symbols that we've asked for in the past unsuccessfully
    skiplist = {}
    skipcount = 0
    try:
        sf = file(os.path.join(thisdir, 'skiplist.txt'), 'r')
        for line in sf:
            line = line.strip()
            if line == '':
                continue
            s = line.split(None, 1)
            print(s)
            if len(s) != 2:
                continue
            (debug_id, debug_file) = s
            skiplist[debug_id] = debug_file.lower()
            skipcount += 1
        sf.close()
    except IOError:
        pass
    log.debug('Skiplist contains %d items' % skipcount)

    modules = defaultdict(set)
    if len(sys.argv) > 1:
        url = sys.argv[1]
        if os.path.isfile(url):
            log.debug("Loading missing symbols file %s" % url)
            missing_symbols = codecs.open(url, 'r', 'utf_8').read()
            print(missing_symbols)
        else:
            log.debug("Loading missing symbols URL %s" % url)
            fetch_error = False
            try:
                req = requests.get(url)
            except requests.exceptions.RequestException as e:
                fetch_error = True
            if fetch_error or req.status_code != 200:
                log.exception("Error fetching symbols")
                sys.exit(1)
            missing_symbols = req.text
    else:
        missing_symbols = fetch_missing_symbols(log)

    lines = iter(missing_symbols.splitlines())
    # Skip header
    next(lines)
    for line in lines:
        print(line)
        line = line.rstrip().encode('ascii', 'replace')
        bits = line.split(',')
        print(bits)
        if len(bits) < 2:
            continue
        pdb, uuid = bits[:2]
        code_file, code_id = None, None
        if len(bits) >= 4:
            code_file, code_id = bits[2:4]
        print(pdb)
        print(uuid)
        if pdb and uuid and pdb.endswith('.pdb'):
            print("added to modules list")
            modules[pdb].add((uuid, code_file, code_id))

    symbol_path = mkdtemp('symsrvfetch')
    temp_path = mkdtemp(prefix='symtmp')

    log.debug("Fetching symbols (%d pdb files)" % len(modules))
    total = sum(len(ids) for ids in modules.values())
    current = 0
    blacklist_count = 0
    skiplist_count = 0
    existing_count = 0
    not_found_count = 0
    not_processed_count = 0
    file_index = []
    # Now try to fetch all the unknown modules from the symbol server
    print(modules)
    for filename, ids in modules.iteritems():
        if filename.lower() in blacklist:
            # This is one of our our debug files from Firefox/Thunderbird/etc
            current += len(ids)
            blacklist_count += len(ids)
            continue
        for (id, code_file, code_id) in ids:
            current += 1
            if verbose:
                sys.stdout.write('[%6d/%6d] %3d%% %-20s\r' %
                                 (current, total, int(100 *
                                                      current /
                                                      total), filename[:20]))
            if id in skiplist and skiplist[id] == filename.lower():
                # We've asked the symbol server previously about this,
                # so skip it.
                log.debug('%s/%s already in skiplist', filename, id)
                skiplist_count += 1
                continue
            rel_path = os.path.join(filename, id,
                                    filename.replace('.pdb', '') + '.sym')
            if server_has_file(rel_path):
                log.debug('%s/%s already on server', filename, id)
                existing_count += 1
                continue
            # Not in the blacklist, skiplist, and we don't already have it, so
            # ask the symbol server for it.
            try:
                sym_output = fetch_and_dump_symbols(temp_path,
                                                    id, filename,
                                                    code_id, code_file)
                if sym_output is None:
                    not_found_count += 1
                    # Figure out how to manage the skiplist later...
                    log.debug(
                        'Couldn\'t fetch %s/%s, but not skiplisting',
                        filename,
                        id)
                else:
                    log.debug('Successfully downloaded %s/%s', filename, id)
                    file_index.append(rel_path.replace('\\', '/'))
                    sym_file = os.path.join(symbol_path, rel_path)
                    try:
                        os.makedirs(os.path.dirname(sym_file))
                    except OSError:
                        pass
                    # TODO: just add to in-memory zipfile
                    open(sym_file, 'w').write(sym_output)
            except Win64ProcessError:
                log.warn('Skipping Win64 PDB: %s/%s' % (filename, id))
                not_processed_count += 1

    if verbose:
        sys.stdout.write('\n')

    if not file_index:
        log.info(
            'No symbols downloaded: %d considered, '
            '%d already present, %d in blacklist, %d skipped, %d not found, '
            '%d not processed ' %
            (total,
             existing_count,
             blacklist_count,
             skiplist_count,
             not_found_count,
             not_processed_count))
        write_skiplist(skiplist)
        sys.exit(0)

    # Write an index file
    buildid = time.strftime('%Y%m%d%H%M%S', time.localtime())
    index_filename = 'microsoftsyms-1.0-WINNT-%s-symbols.txt' % buildid
    log.debug('Adding %s' % index_filename)
    success = False
    zipname = "symbols-%s.zip" % buildid
    with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as z:
        for f in file_index:
            z.write(os.path.join(symbol_path, f), f)
        # z.writestr(index_filename, '\n'.join(file_index))
    log.info('Wrote zip as %s' % zipname)

    shutil.rmtree(symbol_path, True)

    # Write out our new skip list
    write_skiplist(skiplist)
    log.info('Stored %d symbol files' % len(file_index))
    log.info('Finished, exiting')

if __name__ == '__main__':
    main()
