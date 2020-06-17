from atomicqueue.barrier import SequenceBarrier


class RingBuffer:
    def __init__(self, event_type, sequencer, wait_strategy, capacity):
        assert capacity % 2 == 0, f"Ring buffer capacity must be base 2"

        self.sequencer = sequencer
        self.wait_strategy = wait_strategy
        self.capacity = capacity
        self.buffer = []

        self.fill(event_type)

    def fill(self, event_type):
        """ Pre-allocate memory in the ring buffer """
        for _ in range(self.capacity):
            self.buffer.append(event_type())

    def add_gating_sequences(self, sequences):
        """ The sequence barrier that the publishers wait on """
        self.sequencer.add_gating_sequences(sequences)

    def get_new_barrier(self, sequences=None):
        """ Get a new barrier to be tracked by event processors """
        return self.sequencer.get_new_barrier(sequences)

    def publish_event(self, translator, **kwargs):
        """ Claim the next slot in the buffer and spin until it can be written to"""
        sequence = self.sequencer.next()

        event = self.buffer[sequence % self.capacity]

        translator.translate(event, **kwargs)

        self.sequencer.publish(sequence)

    def get(self, sequence):
        return self.buffer[sequence % self.capacity]
