# -*- coding: utf8 -*-

###
# Copyright (c) 2011, Valentin Lorentz
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
###

import re
import urllib
import urllib2

from django.http import Http404
from django.http import HttpResponse

from phonyproxy.common.templates import render_template
from sdz.common import *

regexp_basic_info = re.compile(r'<li><strong>(?P<name>[^:]*) : </strong>(?P<value>[^<]*)</li>')
regexp_activity = re.compile(r'<strong>(?P<name>[^:]*) : </strong>(?P<value>[^<]*)')

def profile(request, id):
    opener = UrlOpener()
    response = opener.open('http://www.siteduzero.com/membres-294-%s.html' % id)
    lines = response.read().split('\n')
    stage = 0
    basic_infos = []
    online = None
    activity = []
    for line in lines:
        if stage == 0 and '<table class="wrap_sections_profil">' in line:
            stage = 1
        elif stage == 1 or stage == 1.5:
            matched = regexp_basic_info.search(line)
            if matched is not None:
                block = Empty()
                block.name, block.value = matched.group('name'), matched.group('value')
                basic_infos.append(block)
                if block.name == 'Pseudo':
                    pseudo = block.value
            elif '<img src="/Templates/images/designs/2/amis/online.png"' in line:
                online = True
            elif '<img src="/Templates/images/designs/2/amis/offline.png"' in line:
                online = False
            elif '</div>' in line:
                stage += 0.5
        elif stage == 2 and '<h3 id="activite">' in line:
            stage = 3
        elif stage == 3:
            matched = regexp_activity.search(line)
            if matched is not None:
                block = Empty()
                block.name, block.value = matched.group('name'), matched.group('value')
                activity.append(block)
            elif '</div>' in line:
                break
    return HttpResponse(render_template('sdz/members/profile.html', request,
                                        {'basic_infos': basic_infos,
                                         'pseudo': pseudo,
                                         'online': online,
                                         'activity': activity}))

