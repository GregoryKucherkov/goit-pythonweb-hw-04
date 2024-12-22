import asyncio
import argparse
from aiopath import AsyncPath
from aioshutil import copyfile
import logging


parser = argparse.ArgumentParser(description="Copy files")
parser.add_argument("--source", "-s", help="source folder", required=True)
parser.add_argument("--output", "-o", help="output folder", default="copied_dir")
args = parser.parse_args()

source = AsyncPath(args.source)
output = AsyncPath(args.output)


async def read_folder(path: AsyncPath):
    coroutines = []
    async for el in path.iterdir():
        if await el.is_dir():
            coroutines.append(read_folder(el))
        else:
            coroutines.append(copy_file(el))
    await asyncio.gather(*coroutines)


async def copy_file(file: AsyncPath):
    target_dir = output / file.suffix
    try:
        await target_dir.mkdir(exist_ok=True, parents=True)
        await copyfile(file, target_dir / file.name)
    except OSError as error:
        logging.error(error)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    logging.info("Starting file sorting...")
    try:
        await read_folder(source)
        logging.info("File sorting completed successfully.")
        logging.info(f"You can delete {source}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
