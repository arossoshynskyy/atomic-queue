from atomicqueue.barrier import SequenceBarrier


class RingBuffer:
    def __init__(self, sequencer, wait_strategy, capacity):
        assert capacity % 2 == 0, f"Ring buffer capacity must be a power of 2"

        self.sequencer = sequencer
        self.wait_strategy = wait_strategy
        self.capacity = capacity
        self.buffer = [None] * capacity

    def add_gating_sequences(self, sequences):
        """ The sequence barrier that the publishers wait on """
        self.sequencer.add_gating_sequences(sequences)

    def get_new_barrier(self, sequences=None):
        """ Get a new barrier to be tracked by event processors """
        return self.sequencer.get_new_barrier(sequences)

    def publish_event(self, event):
        """ Claim the next slot in the buffer and spin until it can be written to"""
        sequence = self.sequencer.next()

        self.buffer[sequence % self.capacity] = event

        self.sequencer.publish(sequence)

    def get(self, sequence):
        return self.buffer[sequence % self.capacity]
