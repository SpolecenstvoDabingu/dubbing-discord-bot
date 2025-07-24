import os
import importlib.util
import inspect

async def load_events(bot, events_dir="events"):
    for filename in os.listdir(events_dir):
        if filename.endswith(".py"):
            filepath = os.path.join(events_dir, filename)
            modulename = f"{events_dir}.{filename[:-3]}"

            spec = importlib.util.spec_from_file_location(modulename, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            for name, func in inspect.getmembers(module, inspect.iscoroutinefunction):
                if name.startswith("on_"):
                    print(f"Registering event handler: {name} from {filename}")
                    bot.add_listener(func, name)
