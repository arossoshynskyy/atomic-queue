# atomic-queue
A thread-safe, lock-free queue implementation based on the LMAX Disruptor, with crititcal parts written in C++.

This queue supports multiple producers and consumers. Producers are responsible for managing their own threads,
while consumer threads are managed by the queue, and are required to implement the EventHandler interface.

## Example

Initialise an atomic queue instance with the Event type, a wait strategy, and buffer capacity. The buffer capacity must be a base 2 integer.

```
class Event:
    __slots__ = ("id", "price", "size", "side")

    def __init__(self):
        self.id = ""
        self.price = 0
        self.size = 0
        self.side = ""

    def __str__(self):
        return f"id={self.id}, price={self.price}, size={self.size}, side={self.side}"


capacity = 256
wait_strategy = WaitStrategy()
queue = AtomicQueue(Event, wait_strategy, capacity)
```

Define how the events will be consumed. In the example below event handler "h_one" and "h_two" can overrun each other but can not overrun the publishers, while event handler "h_three" can only consume events after "h_one" and "h_two" have finished consuming them.

```
queue.handle_events_with(NoOpEventHandler("h_one"), NoOpEventHandler("h_two")).then(NoOpEventHandler("h_three"))
```

Once configured the queue can be started with the following command.

```
queue.start()
```

To publish to the queue, publishers must implement the Translator interface and pass an instance of the translator to the publish_event method of the queue.


```
class ExampleTranslator(Translator):
    def translate(self, event, **kwargs):
        event.id = kwargs["id"]
        event.price = kwargs["price"]
        event.size = kwargs["size"]
        event.side = kwargs["side"]

class ExamplePublisher(threading.Thread):
    def __init__(self, queue, num_events):
        super(Publisher, self).__init__()
        self.queue = queue
        self.num_events = num_events
        self.translator = ExampleTranslator()

    def run(self):
        for idx in range(self.num_events):
            self.queue.publish_event(
                self.translator,
                id=f"{self.name}_{idx}",
                price=100 + idx,
                size=10 * idx,
                side="buy",
            )

publisher.start()
```