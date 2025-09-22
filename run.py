#!/usr/bin/env python3
import argparse
import subprocess
import os
import sys
from datetime import datetime

class RunPytest:
    def __init__(self, args):
        self.args = args
        self.output_dir = f"reports/report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        os.makedirs(self.output_dir, exist_ok=True)
        self.report_file = os.path.join(self.output_dir, "report.html")


    def build_cmd(self):
        cmd = ["pytest"]

        # Nếu có file test thì chỉ chạy file đó, ngược lại chạy thư mục tests/ui          
           
        if self.args.file:
            cmd.extend(self.args.file)

        # include/exclude testcase theo tên (dùng -k trong pytest)
        if self.args.include:
            include_expr = " or ".join(self.args.include)  # list -> string
            cmd.extend(["-m", include_expr])

        if self.args.exclude:
            exclude_expr = " or ".join(self.args.exclude)
            cmd.extend(["-m", f"not ({exclude_expr})"])

        # rerun failed testcase (cần plugin pytest-rerunfailures)
        # if self.args.rerun:
        #     cmd.extend(["--reruns", str(self.args.rerun)])

        # allure report
        # cmd.extend(["--alluredir", self.results_dir])
        
        # pytest-html report
        cmd.extend(["--html", self.report_file, "--self-contained-html"])

        if self.args.headless:
            cmd.append("--headless")

        return cmd

    def run(self):
        cmd = self.build_cmd()
        print("🚀 Running command:", " ".join(cmd))
        process = subprocess.Popen(cmd)
        process.communicate()
        sys.exit(process.returncode)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Pytest with Playwright")
    parser.add_argument("file", nargs="*", help="Test file(s) to run")
    parser.add_argument("-i", "--include", nargs="+",  help="Run only tests with these markers (-m)")
    parser.add_argument("-e", "--exclude", nargs="+", help="Exclude tests with these markers (-m)")
    parser.add_argument('--headless', help='Run browser in headless mode', action='store_true')
    # parser.add_argument("--rerun", type=int, help="Number of times to rerun failed tests")

    args = parser.parse_args()
    RunPytest(args).run()   





# chạy hết trong thư mục tests/ui
# python run.py

# chạy tất cả test case trong test_login.py
# python run.py test_login.py

# chạy test case có mark đươc include
# python run.py -i login smoke

# chạy tất cả trừ testcase có mard được exclude
# python run.py -e slow
