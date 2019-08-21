#!/usr/bin/env python

import sys
import radical.utils as ru
import radical.pilot as rp
import radical.analytics as ra


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "\n\tusage: %s <session>\n" % sys.argv[0]
        sys.exit(1)

    src = sys.argv[1]
    stype = 'radical.pilot'

    session = ra.Session(src, stype)
    units = session.filter(etype='unit', inplace=False)
    unit_0 = units.get()[0]

    print
    print 'session: %s' % session.uid
    print 'units:   %d' % len(units.get())

    # collect all events for some unit which relate to prte
    nevents = list()
    for e in unit_0.events:
        if 'prte' in e[1]:
            nevents.append(e)

    # for that sample unit, print the events and timestamps (ordered)
    print
    print 'PRTE events for unit %s' % unit_0.uid
    for e in nevents:
        if 'prte' in e[1]:
            print '%14.7f : %s' % (e[0], e[1])

    # for all event pairs (neighbors), compute the duration for (a) the sample
    # unit, and (b) the full session
    print
    print 'PRTE durations for unit %s and session' % unit_0.uid
    idx = 0
    while idx < len(nevents) - 1:

        this = nevents[idx    ][1]
        that = nevents[idx + 1][1]
        duru = unit_0.duration(
                event=[{ru.STATE:rp.AGENT_EXECUTING, ru.EVENT:this},
                       {ru.STATE:rp.AGENT_EXECUTING, ru.EVENT:that}])
        durs = units.duration(
                event=[{ru.STATE:rp.AGENT_EXECUTING, ru.EVENT:this},
                       {ru.STATE:rp.AGENT_EXECUTING, ru.EVENT:that}])
        print '%3d: %-30s to %-30s = %14.7f [%14.7f]' \
            % (idx,  this,    that,    duru,   durs)
        idx += 1

    print
