"""One-file runner for PythonAnywhere.

Purpose
-------
Make deployment easy by running everything from ONE Python file.
It still uses your existing project code (main.py, etc.), but this file
lets you avoid editing config secrets and avoids extra shell glue.

How to use on PythonAnywhere
-------------------------------
1) Ensure code is uploaded, and you have installed requirements.
2) Run this script with env vars:

   export BOT_TOKEN='...'
   export DB_PATH='/home/<you>/parking_bot/parking.db'

   python pythonanywhere_onefile_runner.py

You can also inline env vars in the Scheduled Task command.

"""

from __future__ import annotations

import os
import sys


def main() -> None:
    project_dir = os.path.dirname(os.path.abspath(__file__))

    # Ensure local imports work regardless of working directory.
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    # Validate required secrets.
    bot_token = os.environ.get("BOT_TOKEN")
    if not bot_token:
        raise RuntimeError(
            "BOT_TOKEN is not set. Set environment variable BOT_TOKEN before running."
        )

    # DB_PATH is optional (defaults inside config.py to 'parking.db').
    # But for PythonAnywhere it is strongly recommended to set DB_PATH to a writable path.
    db_path = os.environ.get("DB_PATH")
    if not db_path:
        # Let config.py default, but warn clearly.
        print(
            "[WARN] DB_PATH is not set. config.py will default to 'parking.db' in the project directory."
        )

    # Import and execute the real bot.
    # main.py already calls init_db() and starts polling.
    from main import main as bot_main  # type: ignore

    import asyncio

    asyncio.run(bot_main())


if __name__ == "__main__":
    main()

