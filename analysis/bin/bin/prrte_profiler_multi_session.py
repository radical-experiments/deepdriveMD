#!/usr/bin/env python

import sys

import radical.utils as ru
import radical.pilot as rp
import radical.analytics as ra


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "\n\tusage: %s <session> [...]\n" % sys.argv[0]
        sys.exit(1)

    session_csv = open('sessions_prte.csv', 'w')
    unit_csv    = open('units_prte.csv', 'w')

    prte_events = list()

    for src in sys.argv[1:]:

        stype   = 'radical.pilot'
        session = ra.Session(src, stype)
        units   = session.filter(etype='unit', inplace=False)
        unit_0  = units.get()[0]

        print
        print 'session: %s' % session.uid
        print 'units:   %d' % len(units.get())

        # collect all events for some unit which relate to prte - if we don't
        # have them yet
        if not prte_events:
            for e in unit_0.events:
                if 'prte' in e[1]:
                    prte_events.append(e[1])
            idx = 0
            s_row = ['sid']
            u_row = ['uid', 'sid']
            while idx < len(prte_events) - 1:

                this = prte_events[idx]
                that = prte_events[idx + 1]
                u_row.append('%s_to_%s' % (this, that))
                s_row.append('%s_to_%s' % (this, that))
                idx += 1
            unit_csv.write('%s\n' % ','.join(u_row))
            session_csv.write('%s\n' % ','.join(s_row))

        # for all event pairs (neighbors), compute the duration for (a) the
        # sample unit, and (b) the full session
        print
        idx = 0
        s_row = [session.uid]
        while idx < len(prte_events) - 1:

            this = prte_events[idx]
            that = prte_events[idx + 1]
            duru = unit_0.duration(
                event=[{ru.STATE: rp.AGENT_EXECUTING, ru.EVENT: this},
                       {ru.STATE: rp.AGENT_EXECUTING, ru.EVENT: that}])
            dur  = units.duration(
                event=[{ru.STATE: rp.AGENT_EXECUTING, ru.EVENT: this},
                       {ru.STATE: rp.AGENT_EXECUTING, ru.EVENT: that}])

            s_row.append('%.5f' % dur)
            idx += 1
            print '%3d: %-30s to %-30s = %14.7f [%14.7f]' \
                % (idx, this, that, duru, dur)

        session_csv.write('%s\n' % ','.join(s_row))

        for unit in units.get():
            u_row = [unit.uid, session.uid]
            idx = 0
            s_row = [session.uid]
            while idx < len(prte_events) - 1:

                this = prte_events[idx]
                that = prte_events[idx + 1]
                dur  = unit_0.duration(
                    event=[{ru.STATE: rp.AGENT_EXECUTING, ru.EVENT: this},
                           {ru.STATE: rp.AGENT_EXECUTING, ru.EVENT: that}])
                u_row.append('%.5f' % dur)
                idx += 1

            unit_csv.write('%s\n' % ','.join(u_row))

    session_csv.close()
    unit_csv.close()
