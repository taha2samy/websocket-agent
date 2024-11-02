import asyncio

async def background_task(event):
    while True:
        print("Background task is running...")
        await asyncio.sleep(1)  # Simulate doing some work
        if event.is_set():
            print("Event is set! Executing task.")
            event.clear()  # Clear the event after processing

async def send_signal(event):
    event.set()  
    await asyncio.sleep(5)  # Wait before setting the event
    event.reset()  
async def main():
    event = asyncio.Event()

    # Start the background task
    bg_task = asyncio.create_task(background_task(event))

    # Send a signal after a delay
    await send_signal(event)

    # Let the program run for a bit to see the background task respond to the event
    await asyncio.sleep(300)

    # Cancel the background task
    bg_task.cancel()
    try:
        await bg_task
    except asyncio.CancelledError:
        print("Background task cancelled.")

# Run the main coroutine
asyncio.run(main())
