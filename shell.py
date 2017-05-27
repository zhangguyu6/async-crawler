import aiohttp
import asyncio
import argparse
import sys
import io
import traceback
import contextlib
from bs4 import BeautifulSoup
from pyquery import PyQuery


@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = io.StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def chooseparse():
    sys.stdout.write(">>> choose a parse bs(BeautifulSoup) or py(pyquery) ? ")
    sys.stdout.flush()
    line = sys.stdin.readline()
    line = line.strip()
    return line

async def main(url, loop):

    async with aiohttp.ClientSession(loop=loop) as client:
        async with client.get(url) as resp:
            text = await resp.text()
            try:
                line = chooseparse()
                while line not in ("bs", "py"):
                    line = chooseparse()
                if line == "bs":
                    soup = BeautifulSoup(text, "lxml")
                    sys.stdout.write("soup=BeautifulSoup(text,\"lxml\")\n")
                elif line == "py":
                    d = PyQuery(text)
                    sys.stdout.write("d=PyQuery(text)\n")
                while True:
                    sys.stdout.write(str(">>>"))
                    sys.stdout.flush()
                    line = sys.stdin.readline()
                    line = line.strip()
                    if line == "exit":
                        break

                    with stdoutIO() as s:
                        try:
                            exec("print({})".format(line))
                        except Exception as e:
                            sys.stdout.write(
                                str(traceback.format_exc()) + '\n')
                    sys.stdout.write(s.getvalue())
                    sys.stdout.flush()
                    sys.stdout.flush()

            except KeyboardInterrupt:
                sys.stdout.write("\n byebye \n")
                sys.stdout.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type=str, help='URL to parse')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    url = parser.parse_args().url
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(url, loop))
