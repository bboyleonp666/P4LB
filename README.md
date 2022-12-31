# P4 load balancer
- P4: a domain-specific language for data plane manipulation

This practice is to implement a P4 packet forwarding idea with self-defined protocol, which is source routing strategy, with load balance.  
The main goal of this practice is to complete a self-adjust packet forwarding strategy using P4.

## How to start
1. The environment configuration follows the [official P4 tutorial](https://github.com/p4lang/tutorials), installed using VirtualBox and Vagrant
2. Clone this repository to `tutorials/exercises/` by
```
git clone https://github.com/bboyleonp666/P4LB.git
```
3. Generate topology and start the mininet
```
make myrun
```
4. In mininet, start hosts terminals
```
# in mininet terminal
xterm h11 h21
```
5. Set `h11` as a receiver
```
# in h11 terminal
./receive
```
6. Send packet from `h21`
```
# in h21 terminal
./send -t h11
```
7. Exit from mininet
```
# in mininet terminal
exit
```
8. To clean all the files generated
```
make myclean
```