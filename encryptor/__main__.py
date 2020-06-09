from argparse import ArgumentParser
from encryptor import app

parser = ArgumentParser()

parser.add_argument(
    "-p", "--port", dest="port", help="port for network server", type=int
)

if __name__ == "__main__":
    args = parser.parse_args()
    app.run(args.port)
