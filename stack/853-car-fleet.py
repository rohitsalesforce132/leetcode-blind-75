'''
LEETCODE #853: Car Fleet
DIFFICULTY: Medium
TOPIC: Stack / Sorting

=== PROBLEM STATEMENT ===
There are n cars at given starting positions (position[i]) going to the same
destination at target miles away, each travelling at a specific speed
(speed[i], miles per hour). A car can never pass another car ahead of it, but it
can catch up and drive at the slower car's speed (forming a fleet). One car fleet
is some non-empty set of cars driving at the position and speed of the lead car.
Return the number of car fleets that will arrive at the destination.

=== INTUITION ===
1. The car CLOSEST to the destination acts as a "wall". If a faster car behind it
   would catch up before the destination, they merge into one fleet.
2. Sort cars by starting position DESCENDING (closest-to-target first).
3. For each car compute time-to-arrive = (target - position) / speed. If a car's
   arrival time is <= the arrival time of the fleet ahead, it merges in (caught
   up). Otherwise it forms a new fleet.
4. A monotonic-ish stack: push arrival times; if a new time <= stack top, pop and
   merge; else it's a new fleet.

=== APPROACHES ===
Approach 1: Sort by position desc + stack of arrival times
- Idea: Process cars from closest to farthest. Maintain a list of fleet arrival
  times. If current car's time <= top fleet's time, it merges; else new fleet.
- Time: O(n log n) for sort, Space: O(n)

Approach 2: No stack — just count
- Sort by position descending; keep track of the current slowest (max) arrival
  time. A car forms a new fleet only if its time strictly exceeds the running max.

=== DRY RUN ===
target = 12, position = [10,8,0,5,3], speed = [2,4,1,1,3]

Sort by position desc: (10,2) (8,4) (5,1) (3,3) (0,1)
Arrival times:        (12-10)/2=1.0
                      (12-8)/4=1.0
                      (12-5)/1=7.0
                      (12-3)/3=3.0
                      (12-0)/1=12.0

Process:
  (10,2) t=1.0   stack=[]      -> push  [1.0]    fleets=1
  (8,4)  t=1.0   1.0<=1.0 merge-> pop   []        (car behind catches up, no new fleet)
                                          stack=[1.0] -> actually push current [1.0]
  (5,1)  t=7.0   7.0 > 1.0     -> push  [1.0,7.0] fleets=2
  (3,3)  t=3.0   3.0<=7.0 merge-> pop   [1.0]     (catches fleet at 7.0? No! 3<7 means
                                                    it arrives earlier so it CAN catch it)
                                    push  [1.0,3.0]
  (0,1)  t=12.0  12.0 > 3.0    -> push  [1.0,3.0,12.0] fleets=3

Answer: 3

=== COMPLEXITY ANALYSIS ===
Time: O(n log n) — dominated by sorting.
Space: O(n) for stack/sorted pairs.

=== EDGE CASES ===
- Single car -> 1 fleet.
- Two cars same position (problem says positions are distinct, but be aware).
- All cars arrive at exactly the same time -> 1 fleet.
- A super-fast car far behind catches everything -> 1 fleet.

=== INTERVIEW TIPS ===
- Sorting by CLOSEST-to-target first is the key structural insight.
- Define "fleet" precisely: cars that arrive at the same time because the back
  car slows to match the lead.
- The stack-free counter (track running max arrival time) is the cleanest code.
- Watch float vs int division; using floats is fine here.
'''

# === SOLUTION ===
def carFleet(target: int, position: list[int], speed: list[int]) -> int:
    # Pair up and sort by position descending (closest to target first).
    cars = sorted(zip(position, speed), reverse=True)
    stack = []  # stores arrival times of fleets, strictly increasing

    for pos, spd in cars:
        arrival_time = (target - pos) / spd
        # If this car arrives no later than the fleet ahead, it merges in (we drop
        # the old fleet time and keep this car's time as the new fleet front).
        # Otherwise it's a new, later fleet.
        if stack and arrival_time <= stack[-1]:
            continue  # merges with the fleet ahead; no new fleet
        else:
            stack.append(arrival_time)  # new fleet

    return len(stack)


# === TEST CASES ===
if __name__ == "__main__":
    assert carFleet(12, [10,8,0,5,3], [2,4,1,1,3]) == 3
    assert carFleet(10, [3], [3]) == 1
    assert carFleet(100, [0,2,4], [4,2,1]) == 1
    assert carFleet(10, [0,4,2], [2,1,3]) == 1
    assert carFleet(20, [6,2,17], [3,9,2]) == 2
    print("All test cases passed.")
