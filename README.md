# atomic-queue
A thread-safe, lock-free queue implementation based on the LMAX Disruptor, with crititcal parts written in C++.

This queue supports multiple producers and consumers. Producers are responsible for managing their own threads,
while consumer threads are managed by the queue and are required to implement the EventHandler interface.

## Example

Initialise an atomic queue instance with the Event type, a wait strategy, and buffer capacity. The buffer capacity must be a base 2 integer.

```
from atomicqueue import AtomicQueue, BUSY_SPIN_WAIT_STRATEGY

queue = AtomicQueue(256, wait_strategy=BUSY_SPIN_WAIT_STRATEGY)
```

Define how the events will be consumed. In the example below event handler "h_one" and "h_two" can overrun each other but can not overrun the publishers, while event handler "h_three" can only consume events after "h_one" and "h_two" have finished consuming them.

```
queue.handle_events_with(NoOpEventHandler("h_one"), NoOpEventHandler("h_two")).then(NoOpEventHandler("h_three"))
```

Once configured the queue can be started with the following command.

```
queue.start()
```

To publish to the queue, simply call publish_event on the queue.

```
queue.publish_event(event)
```