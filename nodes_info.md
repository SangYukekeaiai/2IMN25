## Info
### node info
|   Node Attributes   |                Possible Value                 |
| :-----------------: | :-------------------------------------------: |
|       status        |        infected, dead, healthy, immune        |
|       future        |        infected, dead, healthy, immune        |
| day_to_change_state | number of the day till recover from the virus |
|     is_symptom      |                 true or false                 |
|    is_essential     |                 true or false                 |
|     is_blocked      |                 true or false                 |

### state changing graph
* Death: Death
* Infected: Immune, Death
* Immune: Healthy
* Healthy: Healthy, Infected

## events(natrual form)
### update time
* iterate all nodes to check:
  * if node[status] != death && node[day_to_change_state] != 0, node[day_to_change_state]--


### death from the infection status
* iteration from the node to find node[status] = infected && node[future] = death && state change day = 0
* change the status to dead

### recover
* iteration from the node to find node[status] = infected && node[future] = immune && state change day = 0
* change the status to immune (node[status] = immune)
* change the future to healthy (node[future] = healthy)
* change the state change day to immune day(node[day_to_change_state] = immune time)


### infaction
* iteration from the node to find node[status] = infected
  * iterate from that node to find the neighbor whose state is healthy
    * give a probability (check if it is is_symptom or not, give different rate) to choose the neighbor to:
      * change the future of the infected neighbor(node[future] = infacted)
      * change the state change time(node[day_to_change_state] = infaction time)

### quit_immune
* iteration from the node to find node[status] = immune && node[future] = healthy && state change day = 0
* assign the node[status] = healthy, node[future] = healthy, state change day = 0(node[day_to_change_state] = 0)

## function
### dayrun
* updatetime()
* death_event()
* recovery()
* be_infacted()
* quit_immue()
* infaction()


