import importlib
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import asyncio
from memory import run
from memory import memory
from memory import llm
from memory import think
from memory import prompts

logging.basicConfig(level=logging.INFO)


def reload():
    importlib.reload(run)
    importlib.reload(memory)
    importlib.reload(llm)
    importlib.reload(think)
    importlib.reload(prompts)


class Handler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.py'):
            logging.warning(f'File {event.src_path} has been modified.')
            reload()
            asyncio.run(main())

async def main():
    try:
        await run.run()
    except Exception as e:
        logging.warning(e)


if __name__ == "__main__":
    time.sleep(1)
    asyncio.run(main())

    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
