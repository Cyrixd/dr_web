import subprocess
import time
import datetime

from dataclasses import dataclass
from typing import IO


CMD = "ps aux"
CMD_TIMEOUT_SEC = 60
RAW_CMD_OUTPUT_FILENAME = "ps_aux_{timestamp}.txt"
FILTERED_CMD_OUTPUT_FILENAME = "ps_aux_filtered_{timestamp}.txt"


@dataclass
class CommandResult:
    return_code: int
    stdout: list[str]
    stderr: list[str]

    def is_success(self) -> bool:
        return self.return_code == 0


def get_output_from_io(input_io: IO[bytes], output_encoding: str = "utf8") -> list[str]:
    output = []
    for line in iter(lambda: input_io.readline(), b''):
        output.append(line.decode(output_encoding))
        # print(output)
    return output


def run_cmd(command: str, cwd: str | None = None, timeout: int = CMD_TIMEOUT_SEC) -> CommandResult:
    p = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        cwd=cwd,
    )
    p.wait(timeout=timeout)

    result = CommandResult(
        return_code=p.returncode,
        stdout=get_output_from_io(input_io=p.stdout),
        stderr=get_output_from_io(input_io=p.stderr)
    )
    return result


def get_timestamp() -> int:
    now = datetime.datetime.now()
    unix_sec = time.mktime(now.timetuple())
    return int(unix_sec)


def write_cmd_out_to_file(filename: str, cmd_out: list[str]) -> str:
    with open(file=filename, mode="w") as file:
        file.writelines(cmd_out)
    return filename


def read_cmd_out_from_file(filename: str) -> list[str]:
    with open(file=filename, mode="r") as file:
        cmd_out = file.readlines()

    return cmd_out


def get_filtered_processes(raw_data: list[str], parameter: str, value: str) -> list[str]:
    output = []

    headers_line = raw_data[0]
    output.append(headers_line)
    headers = headers_line.strip().split()
    assert parameter in headers, "No such parameter in cmd output headers"

    for process_raw_line in raw_data[1:]:
        process_dict = dict(zip(headers, process_raw_line.strip().split(maxsplit=len(headers) - 1)))
        if process_dict.get(parameter) == value:
            output.append(process_raw_line)

    return output


def print_cmd_output(output: str):
    for line in output:
        print(line, end='')


if __name__ == '__main__':
    timestamp = get_timestamp()
    cmd_result = run_cmd(command=CMD)
    assert cmd_result.is_success()

    raw_cmd_output_filename = RAW_CMD_OUTPUT_FILENAME.format(timestamp=timestamp)
    write_cmd_out_to_file(filename=raw_cmd_output_filename, cmd_out=cmd_result.stdout)

    cmd_out_data = read_cmd_out_from_file(filename=raw_cmd_output_filename)

    filtered_processes = get_filtered_processes(raw_data=cmd_out_data, parameter="USER", value="dbotsman")

    filtered_cmd_ouput_filename = FILTERED_CMD_OUTPUT_FILENAME.format(timestamp=timestamp)
    write_cmd_out_to_file(filename=filtered_cmd_ouput_filename, cmd_out=filtered_processes)

    print_cmd_output(filtered_processes)
