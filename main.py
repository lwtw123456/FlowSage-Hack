import os
import time
import threading
import subprocess

from memoryeditor import MemoryEditor


PROCESS_NAME = "flowsage-gui-pro.vmp.exe"

PATTERN = "4C 8D A4 24 60 FF FF FF 4D 3B 66 10 0F 86 6D 06"

REPLACEMENT = "31 C0 31 DB 31 C9 C3 90 4D 3B 66 10 0F 86 6D 06"

SCAN_INTERVAL = 0.1


def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    exe_path = os.path.join(current_dir, PROCESS_NAME)

    if not os.path.isfile(exe_path):
        print(f"[X] 找不到程序: {exe_path}")
        return False

    first_output_event = threading.Event()

    print(f"[+] 启动: {exe_path}")

    process = subprocess.Popen(
        [exe_path],
        cwd=current_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        errors="replace"
    )
    
    def console_reader():
        try:
            for line in process.stdout:
                message = line.rstrip("\r\n")
                
                if (
                    not first_output_event.is_set()
                    and message.strip()
                ):
                    first_output_event.set()

        except Exception as e:
            print(f"[!] 控制台读取线程异常: {e}")

    reader_thread = threading.Thread(
        target=console_reader,
        daemon=True,
        name="ConsoleReader"
    )

    reader_thread.start()

    editor = MemoryEditor(
        PROCESS_NAME,
        verbose=False
    )

    try:

        while True:
            if process.poll() is not None:
                print(
                    f"[X] FlowSage 已提前退出 "
                    f"(ExitCode={process.returncode})"
                )
                return False

            if editor.connect_by_pid(process.pid):
                break

            time.sleep(0.1)

        match = None
        start_time = time.perf_counter()

        print("[*] 开始扫描特征码...")

        while True:
            if process.poll() is not None:
                print(
                    f"[X] FlowSage 已退出 "
                    f"(ExitCode={process.returncode})"
                )
                return False

            if match is None:
                matches = editor.search(
                    pattern_hex=PATTERN,
                    find_all=False,
                    base_only=True
                )

                if matches:
                    match = matches[0]
                    elapsed = (
                        time.perf_counter()
                        - start_time
                    )
                    print("[+] 找到特征码！")

                    if not first_output_event.is_set():
                        print(
                            "[*] 特征码已找到，"
                            "等待 VMProtect 完整性检查结束..."
                        )

            if (
                match is not None
                and first_output_event.is_set()
            ):
                break

            time.sleep(SCAN_INTERVAL)

        print("[*] VMProtect 完整性检查已结束，开始 Patch...")

        address = match["address"]
        patch_result = editor.replace(
            address,
            REPLACEMENT
        )

        if not patch_result.get("new"):
            print("[X] Patch 失败")
            return False

        print("[+] Patch 完成！")
        print("[+] 懒得构造许可证信息了，但已经可以使用 FlowSage 所有功能！")
        input("[+] Enjoy reverse engineering!\n\nPress ENTER to exit...")
        
        
        return True

    finally:

        if editor.pm:
            try:
                editor.disconnect()
            except Exception:
                pass


if __name__ == "__main__":
    success = main()

    raise SystemExit(
        0 if success else 1
    )