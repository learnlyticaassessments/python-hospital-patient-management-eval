# run.py

import importlib.util
import os

# Use relative paths
driver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "secret_tests", "driver.py"))
solution_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "solution.py"))  # Corrected path

spec = importlib.util.spec_from_file_location("driver", driver_path)
driver_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(driver_module)

if __name__ == "__main__":
    driver_module.test_student_code(solution_path)  # Pass the relative solution path
