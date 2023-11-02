async def main():
    async for msg in kafka.queue():
        if not is_valid(msg):
            continue
        if not interesting(msg):
            continue
        leegality_send(msg)



def leegaglity_sender():
    buffer = []

    def sender(msg):
        nonlocal buffer

        buffer.append(msg)
        if buffer > config('MAX_BUFFER'):
            await socket.send(buffers)
            buffer = []
    
    return sender


legalilty_send = leegality_sender()

asyncio.run(main())
