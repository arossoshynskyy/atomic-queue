import threading
import time
import unittest

from atomicqueue import (
    AtomicQueue,
    EventHandler,
    BUSY_SPIN_WAIT_STRATEGY,
)


class Publisher(threading.Thread):
    def __init__(self, queue, name, num_events):
        super(Publisher, self).__init__()
        self.queue = queue
        self.name = name
        self.num_events = num_events

    def run(self):
        for idx in range(self.num_events):
            event = {
                "id": f"{self.name}_{idx}",
                "price": 10,
                "size": 10,
                "side": "buy",
            }

            print(f"Publishing event {event}")

            self.queue.publish_event(event)


class NoOpEventHandler(EventHandler):
    """ No Op event handler for testing """

    def handle(self, event):
        print(f"{self.id} handling event: {event}")


class TestAtomicQueue(unittest.TestCase):
    @unittest.skip
    def test_one_publisher_one_consumer(self):
        queue = AtomicQueue(12, wait_strategy=BUSY_SPIN_WAIT_STRATEGY)

        queue.handle_events_with(NoOpEventHandler("h_one"))

        queue.start()

        publisher = Publisher(queue, "pub1", 100)
        print("STARTED")
        publisher.start()

    @unittest.skip
    def test_one_publisher_multiple_consumers(self):
        queue = AtomicQueue(128, wait_strategy=BUSY_SPIN_WAIT_STRATEGY)

        queue.handle_events_with(NoOpEventHandler("h_one")).then(
            NoOpEventHandler("h_two")
        )

        queue.start()

        publisher = Publisher(queue, "pub1", 100)
        print("STARTED")
        publisher.start()

    # @unittest.skip
    def test_multiple_publishers_multiple_consumers(self):
        queue = AtomicQueue(4096, wait_strategy=BUSY_SPIN_WAIT_STRATEGY)

        queue.handle_events_with(NoOpEventHandler("h_one")).then(
            NoOpEventHandler("h_two")
        )

        queue.start()

        publisher1 = Publisher(queue, "pub1", 1000)
        publisher2 = Publisher(queue, "pub2", 1000)
        print("STARTED")
        publisher1.start()
        publisher2.start()

        # time.sleep(2)
        # queue.stop()


if __name__ == "__main__":
    unittest.main()
