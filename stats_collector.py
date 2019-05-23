import time


class StatsCollector(object):
    """Base class for all stats collector classes."""

    def __init__(self, start_time):
        self.start_time = start_time
        self.stats = []

    def get(self):
        return self.stats

    def peek(self):
        return self.stats[-1]

    @staticmethod
    def _get_drop_percentage(drop_pkts, total_pkts):
        return float(drop_pkts * 100) / total_pkts

    @staticmethod
    def _get_rx_pps(tx_pps, drop_percentage):
        return (tx_pps * (100 - drop_percentage)) / 100

    def _get_current_time_diff(self):
        return int((time.time() - self.start_time) * 1000)


class IntervalCollector(StatsCollector):
    """Collects stats while traffic is running. Frequency is specified by 'interval_sec' setting."""

    last_tx_pkts = 0
    last_rx_pkts = 0
    last_time = 0

    def __init__(self, start_time):
        StatsCollector.__init__(self, start_time)
        self.notifier = None

    def attach_notifier(self, notifier):
        self.notifier = notifier

    def add(self, stats):
        pass

    def reset(self):
        # don't reset time!
        self.last_rx_pkts = 0
        self.last_tx_pkts = 0

    def add_ndr_pdr(self, tag, stats):
        pass


class IterationCollector(StatsCollector):
    """Collects stats after traffic is stopped. Frequency is specified by 'duration_sec' setting."""

    def __init__(self, start_time):
        StatsCollector.__init__(self, start_time)

    def add(self, stats, tx_pps):
        drop_percentage = self._get_drop_percentage(stats['overall']['rx']['dropped_pkts'],
                                                    stats['overall']['tx']['total_pkts'])

        record = {
            'total_tx_pps': int(stats['total_tx_rate']),
            'tx_pps': tx_pps,
            'tx_pkts': stats['overall']['tx']['total_pkts'],
            'rx_pps': self._get_rx_pps(tx_pps, drop_percentage),
            'rx_pkts': stats['overall']['rx']['total_pkts'],
            'drop_pct': stats['overall']['rx']['dropped_pkts'],
            'drop_percentage': drop_percentage,
            'time_ms': int(time.time() * 1000)
        }

        if 'warning' in stats:
            record['warning'] = stats['warning']

        self.stats.append(record)

    def add_ndr_pdr(self, tag, rate):
        last_stats = self.peek()
        last_stats['{}_pps'.format(tag)] = rate
