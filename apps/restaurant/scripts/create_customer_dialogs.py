import asyncio

from asgiref.sync import sync_to_async

from apps.restaurant.fsm.machine import DialogStateMachine
from apps.restaurant.models import CustomerProfile
from apps.restaurant.models import DialogSession
from core.auth.utils.factories import UserFactory


async def run_one():
    user = await sync_to_async(UserFactory.create)()
    customer = await CustomerProfile.objects.aget(user=user)
    session = await DialogSession.objects.acreate(
        messages=[],
        analysis_result={},
        customer=customer,
    )
    print(
        f"session created: id={session.id}  customer_id={getattr(customer, 'id', None)}"
    )
    machine = DialogStateMachine.from_session(session)
    triggers = [
        "start_greeting",
        "receive_day_reply",
        "proceed_to_ask_favorites",
        "receive_favorites_reply",
        "proceed_to_ask_order",
        "receive_order_reply",
        "run_analysis",
    ]
    for t in triggers:
        print(f"trigger start: {t} session={session.id}")
        ok = await asyncio.to_thread(machine.safe_trigger, t)
        if not ok:
            print(
                f"trigger failed: {t} from_state={machine.current_state} session={session.id}"
            )
            break
        print(f"trigger ok: {t} -> state={machine.current_state} session={session.id}")
    await sync_to_async(session.refresh_from_db)()
    print(f"session finalized: id={session.id} state={session.state}")
    await asyncio.sleep(3)
    return session


async def run_many(count: int):
    print(f"run_many start: count={count}")
    sem = asyncio.Semaphore(5)

    async def _runner():
        async with sem:
            return await run_one()

    tasks = [asyncio.create_task(_runner()) for _ in range(count)]
    sessions = await asyncio.gather(*tasks)
    print(f"run_many done: count={count}")
    return sessions


def run(*args):
    count = int(args[0]) if args else 1
    asyncio.run(run_many(count))
