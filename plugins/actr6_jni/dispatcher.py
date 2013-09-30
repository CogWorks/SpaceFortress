# -*- coding:    utf-8 -*-
#===============================================================================
# This file is part of ACTR6_JNI.
# Copyright (C) 2012-2013 Ryan Hope <rmh3093@gmail.com>
#
# ACTR6_JNI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ACTR6_JNI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ACTR6_JNI.  If not, see <http://www.gnu.org/licenses/>.
#===============================================================================

from panglery import Pangler

class Dispatcher(Pangler):

    def listen(self, event):
        def decorator(target):
            @self.subscribe(e=event, needs=['model', 'params'])
            def wrapper(*args, **kwargs):
                newargs = tuple([arg for arg in args if not isinstance(arg, Pangler)])
                return target(*newargs, **kwargs)
            return wrapper
        return decorator
