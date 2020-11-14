import net
import math

delay = [
    [0,.1],
    [.1,0]
]
speed = [
    [0,1024],
    [1024,0]
]
routing = [
    [0,1],
    [0,1]
]

def main():
    sim = net.init(speed, delay, routing)
    print(sim)
    net.step(sim)

if __name__ == "__main__":
    main()
