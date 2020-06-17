class SequenceBarrier:
    """ 
    Track sequence for smallest index number being processed by event processor or
    group of event processors  
    """

    def __init__(self, sequencer, dependent_sequences, wait_strategy):
        self.sequencer = sequencer
        self.dependent_sequences = dependent_sequences
        self.wait_strategy = wait_strategy

    def wait_for(self, sequence):
        """ Return the next highest available number in the
        buffer after the consumer asks for the next event"""

        available_sequence = self.wait_strategy.wait_for(
            self.dependent_sequences, sequence
        )

        return self.sequencer.get_highest_published(sequence, available_sequence)
