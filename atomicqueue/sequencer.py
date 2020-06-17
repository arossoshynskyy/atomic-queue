import math

from atomicsequence import AtomicSequence
from atomicqueue.barrier import SequenceBarrier


class Sequencer:
    """ Track sequence for smallest index number being published to 
    sequence: tracks sequence to be written to
    dependent_barriers: barriers to keep track of to prevent wrapping
    wait_strategy: #TODO"""

    def __init__(self, wait_strategy, buffer_size):
        self.sequence = AtomicSequence(-1)
        self.dependent_sequences = []
        self.buffer_size = buffer_size
        self.available_buffer = [-1] * buffer_size
        self.index_shift = int(math.log2(buffer_size))
        self.index_mask = buffer_size - 1
        self.wait_strategy = wait_strategy

    def add_gating_sequences(self, sequences):
        """ Set gating sequences for sequencer to watch """
        self.dependent_sequences.extend(sequences)

    def get_new_barrier(self, sequences):
        if sequences is None:
            return SequenceBarrier(self, [self.sequence], self.wait_strategy)

        return SequenceBarrier(self, sequences, self.wait_strategy)

    def next(self):
        """ Claim next slot to be written to and block until it becomes available for writing"""
        sequence = self.sequence.increment_and_get(1)

        while True:
            # TODO lazy fetch with cached sequence number
            gating_sequence = min(map(lambda s: s.get(), self.dependent_sequences))
            wrap_point = sequence - self.buffer_size

            if wrap_point < gating_sequence:  # sequence > gating_sequence and
                break

        return sequence

    def publish(self, sequence):
        """ Free up the slot at sequence number and make available to consumers """
        self.set_available(sequence)
        self.wait_strategy.notify_all()

    def set_available(self, sequence):
        """ Make this sequence number available for consumption """
        index = self.calculate_index(sequence)
        flag = self.calculate_availability_flag(sequence)

        self.available_buffer[index] = flag

    def is_available(self, sequence):
        """ Check if given sequence is available for processing """
        index = self.calculate_index(sequence)
        flag = self.calculate_availability_flag(sequence)

        return self.available_buffer[index] == flag

    def get_highest_published(self, start, available_sequence):
        """ Determine the highest sequence that can be read """
        sequence = start
        while sequence <= available_sequence:
            if not self.is_available(sequence):
                return sequence - 1

            sequence += 1

        return available_sequence

    def calculate_availability_flag(self, sequence):
        return sequence >> self.index_shift

    def calculate_index(self, sequence):
        return sequence & self.index_mask
