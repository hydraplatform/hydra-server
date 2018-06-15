#!/usr/local/bin/python
#
# (c) Copyright 2013, 2014, University of Manchester
#
# HydraPlatform is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HydraPlatform is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HydraPlatform.  If not, see <http://www.gnu.org/licenses/>
#
import sys
from hydra_server import s

#To kill this process, use this command:
#ps -ef | grep 'server.py' | grep 'python' | awk '{print $2}' | xargs kill
if __name__ == '__main__':

    args = sys.argv
    
    print(args)

    if len(args) > 1:
        port = int(args[1])
    else:
        port = None

    s.run_server(port=port)
