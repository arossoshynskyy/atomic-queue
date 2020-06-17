from atomicqueue.sequencer import Sequencer
from atomicqueue.barrier import SequenceBarrier
from atomicqueue.ring_buffer import RingBuffer
from atomicqueue.event_processor import EventProcessor
from atomicqueue.wait_strategy import get_strategy


class AtomicQueue:
    """ 
    Used to wire together all the event processors
    producer_type: Enum - SINGLE or MULTI
    wait_strategy: WaitStrategy - wait strategy to use
    capacity: int - must be base 2 
    """

    def __init__(self, event_type, wait_strategy, capacity):
        self.wait_strategy = get_strategy(wait_strategy)

        sequencer = Sequencer(self.wait_strategy, capacity)
        self.ring_buffer = RingBuffer(
            event_type, sequencer, self.wait_strategy, capacity
        )

        self.processors = []
        self.event_handler_groups = []

    def handle_events_with(self, *handlers):
        """ Define which handlers consume events on the ring buffer. These handlers
        can overrun each other during consumption, but cannot overrun the publishers. """

        barrier = self.ring_buffer.get_new_barrier()

        event_handler_group = EventHandlerGroup(
            self.ring_buffer, self.wait_strategy, barrier, handlers
        )

        self.event_handler_groups.append(event_handler_group)

        self.ring_buffer.add_gating_sequences(event_handler_group.get_sequences())

        return self

    def then(self, *handlers):
        """ Defined which handlers can consume events after previously defined handlers
        have finished consuming them. These handlers cannot overrun previously defined
        handlers. """

        sequences = self.event_handler_groups[-1].get_sequences()
        barrier = self.ring_buffer.get_new_barrier(sequences)

        event_handler_group = EventHandlerGroup(
            self.ring_buffer, self.wait_strategy, barrier, handlers
        )

        self.event_handler_groups.append(event_handler_group)

        self.ring_buffer.add_gating_sequences(event_handler_group.get_sequences())

        return self

    def start(self):
        # TODO check gating barrier exists
        for group in self.event_handler_groups:
            group.start()

    def publish_event(self, translator, **kwargs):
        self.ring_buffer.publish_event(translator, **kwargs)

    def stop(self):
        for group in self.event_handler_groups:
            group.stop()


class EventHandlerGroup:
    """ Define a group of handlers on the ring buffer. These handlers can 
        overrun each other during consumption, but cannot overrun publishers. """

    def __init__(self, ring_buffer, wait_strategy, barrier, handlers):
        self.ring_buffer = ring_buffer
        self.wait_strategy = wait_strategy
        self.handlers = handlers

        processors = []
        for handler in handlers:
            processor = EventProcessor(ring_buffer, barrier, handler)
            processors.append(processor)

        self.processors = processors

    def get_processors(self):
        return self.processors

    def get_sequences(self):
        return list(map(lambda p: p.get_sequence(), self.processors))

    def start(self):
        for processor in self.processors:
            processor.start()

    def stop(self):
        for processor in self.processors:
            processor.stop()
            processor.join()
