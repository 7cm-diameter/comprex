from random import randrange

from amas.agent import OBSERVER, Agent, NotWorkingError
from comprex.agent import ABEND, NEND

SENDER = "SENDER"
RECEIVER = "RECEIVER"


async def send(agent: Agent, n: int):
    try:
        while agent.working():
            for i in range(n):
                interval = randrange(1, 10) / 5.
                await agent.sleep(interval)
                agent.send_to(RECEIVER, i)
            agent.send_to(OBSERVER, NEND)
            agent.finish()
    except NotWorkingError:
        agent.send_to(OBSERVER, ABEND)
    return None


async def recv(agent: Agent):
    try:
        while agent.working():
            _, mess = await agent.recv()
            print(f"receive {mess} from {RECEIVER}")
    except NotWorkingError:
        pass
    return None


if __name__ == '__main__':
    from amas.connection import Register
    from amas.env import Environment
    from comprex.agent import Observer, _self_terminate

    sender = Agent(SENDER) \
        .assign_task(send, n=5) \
        .assign_task(_self_terminate)

    receiver = Agent(RECEIVER) \
        .assign_task(recv) \
        .assign_task(_self_terminate)

    observer = Observer()

    agents = [sender, receiver, observer]
    rgst = Register(agents)
    env = Environment(agents)

    try:
        env.run()
    except KeyboardInterrupt:
        observer.send_all(ABEND)
