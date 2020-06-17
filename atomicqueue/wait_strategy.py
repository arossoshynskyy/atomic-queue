from atomicqueue.exceptions import InvalidWaitStrategyException

BUSY_SPIN_WAIT_STRATEGY = "BUSY_SPIN_WAIT_STRATEGY"


class BusySpinWaitStrategy:
    """ Busy spin wait strategy for queue """

    def wait_for(self, dependent_sequences, sequence):
        """ Wait for the given sequence to become available """
        while True:
            min_available = min(map(lambda s: s.get(), dependent_sequences))

            if min_available >= sequence:
                return min_available

    def notify_all(self):
        """ Notify all listeners that the cursor has advanced and
        the need to check the new sequence number"""
        pass


def get_strategy(_type, *args):
    strategies = {BUSY_SPIN_WAIT_STRATEGY: BusySpinWaitStrategy(*args)}

    if _type not in strategies:
        raise InvalidWaitStrategyException

    return strategies[_type]
