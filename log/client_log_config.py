import logging
import sys

client_log = logging.getLogger('client_log_config')
client_log.setLevel(logging.INFO)

my_file_handler = logging.FileHandler('log/client.log')
client_formatter = logging.Formatter("%(asctime)s - %(levelname)-10s - %(module)-8s - %(message)s ")
my_file_handler.setFormatter(client_formatter)
my_file_handler.setLevel(logging.INFO)
client_log.addHandler(my_file_handler)

my_stream_handler = logging.StreamHandler(sys.stderr)
stream_formatter = logging.Formatter("%(asctime)s - %(levelname)-10s - %(module)-8s - %(message)s ")
my_stream_handler.setFormatter(stream_formatter)
my_stream_handler.setLevel(logging.WARNING)
client_log.addHandler(my_stream_handler)
