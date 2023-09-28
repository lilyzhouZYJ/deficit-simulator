import random
import heapq
import logging
import allocation_policy

# Constants:
MIN_SLOTS = 200 # minimum number of slots given to a link as determined by Optimizer
MAX_SLOTS = 300 # maximum number of slots given to a link as determined by Optimizer

MIN_WEIGHT = 1  # minimum weight of a queue
MAX_WEIGHT = 10 # maximum weight of a queue

MIN_NEW_JOB = 0  # minimum number of new jobs arriving at a given time
MAX_NEW_JOB = 10 # maximum number of new jobs arriving at a given time

class Simulator:
    def __init__(self, queue_count = 2):
        # Number of tasks in each queue
        self.queues = [0] * queue_count
        self.queue_count = queue_count

        # Generate weights for each queue
        weights = []
        for i in range(queue_count):
            weights.append(random.randint(MIN_WEIGHT, MAX_WEIGHT))
        weight_sum = sum(weights)
        self.queue_weights = []
        for i in range(queue_count):
            self.queue_weights.append(weights[i] / weight_sum)

        self.max_slots = 0                  # max slots (as determined by OptimizerService)
        self.should_be = [0] * queue_count  # number of should-be-allocated slots
        self.actives = [0] * queue_count    # number of active slots
        self.deficits = [0] * queue_count   # deficit

        # Track deficit over time for each queue
        # deficit_tracker[i]: all deficits for queue[i]
        self.deficit_tracker = [[] for i in range(queue_count)]

    def process_queue_jobs(self):
        """
        Process all queues at a given time interval, determine whether jobs arrived or finished.
        """
        logging.info("(1) Process queue jobs (whether jobs arrived or completed):")
        for i, q in enumerate(self.queues):
            logging.info(f"  Queue[{i}]:")

            # How many new jobs arrived for this queue at t
            new_job_count = random.randint(MIN_NEW_JOB, MAX_NEW_JOB)
            self.queues[i] += new_job_count
            logging.info(f"    {q} old jobs and {new_job_count} new jobs; total: {self.queues[i]} jobs")

            # How many active jobs got completed => remaining active slots
            completed_jobs = random.randint(0, self.actives[i] // 3)
            self.actives[i] -= completed_jobs
            logging.info(f"    {completed_jobs} jobs were completed, with {self.actives[i]} remaining active jobs")
        
        logging.info("")

    def determine_slots(self):
        """
        Based on whether there are jobs in the queues, compute the should-be-allocated number of slots.
        """
        logging.info("(2) Determine number of slots, assign to queues:")

        self.max_slots = random.randrange(MIN_SLOTS, MAX_SLOTS + 1, step = 10)
        logging.info(f"  Max number of slots: {self.max_slots}")

        # Compute the number of should-be-allocated slots based on weight
        allocation_policy.allocate(self.max_slots, self.queues, self.queue_weights, self.should_be, self.actives)
        
        logging.info("  Weights for each queue: " + str(self.queue_weights))
        logging.info("  Should-be-allocated slots for each queue: " + str(self.should_be))
        logging.info("")

    def compute_deficits(self):
        """
        Compute the deficits of all queues
        """
        logging.info("(3) Compute deficits:")
        for i, q in enumerate(self.queues):
            logging.info(f"  Queue[{i}]:")
            logging.info(f"    should-be-allocated: {self.should_be[i]}, actives: {self.actives[i]}")

            if self.queues[i] > 0:
                new_deficit = self.should_be[i] - self.actives[i]
                self.deficits[i] += new_deficit
            else:
                # Queue is empty: set deficit to 0
                self.deficits[i] = 0
            self.deficit_tracker[i].append(self.deficits[i]) # append to deficit_tracker
            logging.info(f"    Deficit: {self.deficits[i]}")

    def assign_slots_to_queues_based_on_deficit(self):
        logging.info("(4) Assign slots to queues based on their deficits:")

        # Construct priority queue of deficits
        priority_queue = []
        for queue_id, deficit in enumerate(self.deficits):
            if self.queues[queue_id] > 0:
                priority_queue.append((-deficit, queue_id))
        heapq.heapify(priority_queue)

        # Assign slots to queues based on priority
        avail_slots = self.max_slots - sum(self.actives)
        logging.info(f"  Actual available to-be-assigned slots: {avail_slots}")
        logging.info("")

        for slot in range(avail_slots):
            if priority_queue:
                deficit, queue_id = heapq.heappop(priority_queue)

                # Schedule a job from the queue
                self.queues[queue_id] -= 1
                self.actives[queue_id] += 1
                self.deficits[queue_id] -= 1 # TODO: do we want to penalize a queue if other queues simply don't have enough tasks?

                logging.info(f"    Assign slot {slot} to queue {queue_id}, new queue size is {self.queues[queue_id]}")

                if self.queues[queue_id] > 0:
                    # Only push back to priority_queue if queue is non-empty
                    heapq.heappush(priority_queue, (deficit+1, queue_id))
                else:
                    # Reset deficit if queue becomes empty
                    self.deficits[queue_id] = 0

        logging.info(f"  Queue sizes after assignment: \t" + "\t".join([str(i) for i in self.queues]))

    def run(self, intervals = 10):
        for t in range(intervals):
            logging.info(f"==== At time interval {t} ====")        

            # Process queues: whether jobs arrived or completed
            self.process_queue_jobs()

            # Determine max number of slots and assign to queues based on weights
            self.determine_slots()

            # Compute deficits
            self.compute_deficits()

            logging.info("")
            logging.info("Queue_id: \t" + "\t".join([str(i) for i in range(self.queue_count)]))
            logging.info("Queue_count: \t" + "\t".join([str(i) for i in self.queues]))
            logging.info("Should: \t" + "\t".join([str(i) for i in self.should_be]))
            logging.info("Actives: \t" + "\t".join([str(i) for i in self.actives]))
            logging.info("Deficits: \t" + "\t".join([str(i) for i in self.deficits]))
            logging.info("")

            # Assign slots to queues based on deficits
            self.assign_slots_to_queues_based_on_deficit()
            logging.info("")

        # Print deficit changes over time
        for queue_id, queue_deficits in enumerate(self.deficit_tracker):
            queue_deficits = [str(d) for d in queue_deficits]
            logging.info(f"Queue[{queue_id}]: \t" + "\t".join(queue_deficits))

