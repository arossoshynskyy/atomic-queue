import unittest
import threading
import time

from atomicqueue import (
    AtomicQueue,
    EventHandler,
    Translator,
    BUSY_SPIN_WAIT_STRATEGY,
)


class TestTranslator(Translator):
    def translate(self, event, **kwargs):
        event.id = kwargs["id"]
        event.price = kwargs["price"]
        event.size = kwargs["size"]
        event.side = kwargs["side"]


class Publisher(threading.Thread):
    def __init__(self, queue, name, num_events):
        super(Publisher, self).__init__()
        self.queue = queue
        self.name = name
        self.num_events = num_events
        self.translator = TestTranslator()

    def run(self):
        for idx in range(self.num_events):
            data = {
                "id": f"{self.name}_{idx}",
                "price": 100 + idx,
                "size": 10 * idx,
                "side": "buy",
            }

            print(f"Publishing data {data}")

            self.queue.publish_event(self.translator, **data)


class Event:
    __slots__ = ("id", "price", "size", "side")

    def __init__(self):
        self.id = ""
        self.price = 0
        self.size = 0
        self.side = ""

    def __str__(self):
        return f"id={self.id}, price={self.price}, size={self.size}, side={self.side}"


class NoOpEventHandler(EventHandler):
    """ No Op event handler for testing """

    def handle(self, event):
        print(f"{self.id} handling event: {event}")


class TestAtomicQueue(unittest.TestCase):
    @unittest.skip
    def test_one_publisher_one_consumer(self):
        queue = AtomicQueue(Event, BUSY_SPIN_WAIT_STRATEGY, 12)

        queue.handle_events_with(NoOpEventHandler("h_one"))

        queue.start()

        publisher = Publisher(queue, "pub1", 100)
        print("STARTED")
        publisher.start()

    @unittest.skip
    def test_one_publisher_multiple_consumers(self):
        queue = AtomicQueue(Event, BUSY_SPIN_WAIT_STRATEGY, 128)

        queue.handle_events_with(NoOpEventHandler("h_one")).then(
            NoOpEventHandler("h_two")
        )

        queue.start()

        publisher = Publisher(queue, "pub1", 100)
        print("STARTED")
        publisher.start()

    # @unittest.skip
    def test_multiple_publishers_multiple_consumers(self):
        queue = AtomicQueue(Event, BUSY_SPIN_WAIT_STRATEGY, 4096)

        queue.handle_events_with(NoOpEventHandler("h_one")).then(
            NoOpEventHandler("h_two")
        )

        queue.start()

        publisher1 = Publisher(queue, "pub1", 1000)
        publisher2 = Publisher(queue, "pub2", 1000)
        print("STARTED")
        publisher1.start()
        publisher2.start()

        time.sleep(2)
        queue.stop()


if __name__ == "__main__":
    unittest.main()
