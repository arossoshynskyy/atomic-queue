import threading

from atomicsequence import AtomicSequence


class EventProcessor(threading.Thread):
    stop_thread = False

    def __init__(self, ring_buffer, sequence_barrier, event_handler):
        super(EventProcessor, self).__init__()
        self.sequence = AtomicSequence(-1)
        self.ring_buffer = ring_buffer
        self.sequence_barrier = sequence_barrier
        self.event_handler = event_handler

    def get_sequence(self):
        return self.sequence

    def run(self):
        self.stop_thread = False

        next_sequence = self.sequence.get() + 1

        while not self.stop_thread:
            available_sequence = self.sequence_barrier.wait_for(next_sequence)

            while next_sequence <= available_sequence:
                event = self.ring_buffer.get(next_sequence)
                self.event_handler.handle(event)
                next_sequence += 1

            self.sequence.set(available_sequence)

    def stop(self):
        self.stop_thread = True


class EventHandler:
    """ Extend this class to register an event processor """

    def __init__(self, id):
        self.id = id

    def handle(self, event):
        """ Override this to process events"""
        raise NotImplementedError()
