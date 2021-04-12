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
                agent.send_to(RECEIVER, interval)
            agent.send_to(OBSERVER, NEND)
            agent.finish()
    except NotWorkingError:
        agent.send_to(OBSERVER, ABEND)
    return None


async def recv(agent: Agent):
    try:
        while agent.working():
            mail = await agent.try_recv(0.5)
            if mail is None:
                continue
            _, mess = mail
            print(f"receive {mess} from {RECEIVER}")
    except NotWorkingError:
        pass
    return None


async def heavy_work(agent: Agent):
    from time import sleep
    try:
        while agent.working():
            sleep(1 / 30)
            await agent.sleep(0.001)
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
        .assign_task(heavy_work) \
        .assign_task(_self_terminate)

    observer = Observer()

    agents = [sender, observer, receiver]
    rgst = Register(agents)
    env_send = Environment(agents[0:-1])
    env_recv = Environment([agents[-1]])

    try:
        env_recv.parallelize()
        env_send.run()
        env_recv.join()
    except KeyboardInterrupt:
        observer.send_all(ABEND)
