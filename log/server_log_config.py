import logging
import sys

server_log = logging.getLogger('server_log_config')
server_log.setLevel(logging.INFO)

my_file_handler = logging.FileHandler('log/server.log')
client_formatter = logging.Formatter("%(asctime)s - %(levelname)-10s - %(module)-8s - %(message)s ")
my_file_handler.setFormatter(client_formatter)
my_file_handler.setLevel(logging.INFO)
server_log.addHandler(my_file_handler)

my_stream_handler = logging.StreamHandler(sys.stderr)
stream_formatter = logging.Formatter("%(asctime)s - %(levelname)-10s - %(module)-8s - %(message)s ")
my_stream_handler.setFormatter(stream_formatter)
my_stream_handler.setLevel(logging.WARNING)
server_log.addHandler(my_stream_handler)
