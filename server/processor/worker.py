from __future__ import annotations

import time


def main() -> None:
    """
    Dev scaffold worker loop.

    The production processor will read validated ingest batches from the queue,
    normalize/index them, and write to the storage layer.
    """
    print("OVPO processor (dev scaffold) starting...")
    while True:
        time.sleep(5)
        print("processor: idle (queue not wired yet)")


if __name__ == "__main__":
    main()
