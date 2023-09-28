import heapq

"""
Huntington-Hill Method:
(1) First compute the qualification threshold, which is sum(weights)/max_slots.
    Queues with weight >= threshold will be assigned an initial slot.
(2) For each of the remaining slots:
    - Compute the priority number of each queue: A_{n} = P / sqrt(n*(n+1)), where n is the number
      of slots the queue currently has, P is the weight of the queue.
    - Assign the slot to the highest-priority queue and adjust its priority number accordingly.
      The recursive formula for the priority number is A_{n} = sqrt((n-1)/(n+1)) * A_{n-1}
      A_{1} is explicitly defined nonrecursively as A_{1} = P / sqrt(2)
"""

def huntington_hill(max_slots, queue_weights, should_be):
    if max_slots == 0:
        return

    # Compute qualification threshold
    # sum_weights = sum([w if queues[i] > 0 else 0 for i, w in enumerate(queue_weights)])
    sum_weights = sum(queue_weights)
    threshold = sum_weights / max_slots

    # Assign one slot to every queue that meets the threshold; compute A_{1}
    priority_queue = []
    for queue_id, weight in enumerate(queue_weights):
        if weight >= threshold:
            should_be[queue_id] = 1
            max_slots -= 1

            # Compute priority
            priority = weight**2 / 2
            priority_queue.append((-priority, queue_id))
        else:
            should_be[queue_id] = 0

    heapq.heapify(priority_queue)

    # Assign the remaining slots
    if priority_queue:
        for slot in range(max_slots):
            priority, queue_id = heapq.heappop(priority_queue)
            should_be[queue_id] += 1

            # Recompute priority
            n = should_be[queue_id]
            priority *= (n-1) / (n+1)

            heapq.heappush(priority_queue, (priority, queue_id))

def huntington_hill_consider_queue_size(max_slots, queues, queue_weights, should_be):
    if max_slots == 0:
        return

    # Compute qualification threshold (only consider non-empty queues)
    sum_weights = sum([w if queues[i] > 0 else 0 for i, w in enumerate(queue_weights)])
    threshold = sum_weights / max_slots

    # Assign one slot to every queue that meets the threshold; compute A_{1}
    priority_queue = []
    for queue_id, weight in enumerate(queue_weights):
        if queues[queue_id] > 0 and weight >= threshold:
            should_be[queue_id] = 1
            max_slots -= 1

            # Compute priority
            priority = weight**2 / 2
            priority_queue.append((-priority, queue_id))
        else:
            should_be[queue_id] = 0

    heapq.heapify(priority_queue)

    # Assign the remaining slots:
    # only assign slot to a queue if the queue has remaining tasks
    queue_sizes = [q for q in queues]

    for slot in range(max_slots):
        if not priority_queue:
            break

        priority, queue_id = heapq.heappop(priority_queue)
        should_be[queue_id] += 1
        queue_sizes[queue_id] -= 1
        
        if queue_sizes[queue_id] > 0:
            # Recompute priority
            n = should_be[queue_id]
            priority *= (n-1) / (n+1)
            heapq.heappush(priority_queue, (priority, queue_id))

def huntington_hill_consider_queue_size_and_active_count(max_slots, queues, actives, queue_weights, should_be):
    if max_slots == 0:
        return
    
    # Find queues that have pending tasks or have active slots
    queue_sizes = []
    for queue_id in range(len(queues)):
        queue_sizes.append(queues[queue_id] + actives[queue_id])

    # Compute qualification threshold (only consider non-empty queues or queues with active slots)
    sum_weights = 0
    for queue_id in range(len(queues)):
        if queue_sizes[queue_id] > 0:
            sum_weights += queue_weights[queue_id]
    threshold = sum_weights / max_slots

    # Assign one slot to every queue that meets the threshold; compute A_{1}
    priority_queue = []
    for queue_id, weight in enumerate(queue_weights):
        if queue_sizes[queue_id] > 0 and weight >= threshold:
            should_be[queue_id] = 1
            max_slots -= 1

            # Compute priority
            priority = weight**2 / 2
            priority_queue.append((-priority, queue_id))
        else:
            should_be[queue_id] = 0

    heapq.heapify(priority_queue)

    # Assign the remaining slots:
    # only assign slot to a queue if the queue is nonempty or has active slots
    for slot in range(max_slots):
        if not priority_queue:
            break

        priority, queue_id = heapq.heappop(priority_queue)
        should_be[queue_id] += 1
        queue_sizes[queue_id] -= 1
        
        if queue_sizes[queue_id] > 0:
            # Recompute priority
            n = should_be[queue_id]
            priority *= (n-1) / (n+1)
            heapq.heappush(priority_queue, (priority, queue_id))

def allocate(max_slots, queues, queue_weights, should_be, actives):
    # huntington_hill(max_slots, queue_weights, should_be)
    # huntington_hill_consider_queue_size(max_slots, queues, queue_weights, should_be)
    huntington_hill_consider_queue_size_and_active_count(max_slots, queues, actives, queue_weights, should_be)