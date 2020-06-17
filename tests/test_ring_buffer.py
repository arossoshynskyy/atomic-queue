import unittest

from atomicqueue.sequencer import Sequencer
from atomicqueue.ring_buffer import RingBuffer
from atomicqueue.wait_strategy import BUSY_SPIN_WAIT_STRATEGY

"""
class TestRingBuffer(unittest.TestCase):
    def test_ring_buffer(self):
        capacity = 32

        sequencer = Sequencer()
        wait_strategy = WaitStrategy()
        ring_buffer = RingBuffer(sequencer, wait_strategy, capacity)


if __name__ == '__main__':
    unittest.main()
"""
