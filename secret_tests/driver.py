import importlib.util
import datetime
import os
import inspect
import pandas as pd
import numpy as np

def test_student_code(solution_path):
    report_dir = os.path.join(os.path.dirname(__file__), "..", "student_workspace")
    report_path = os.path.join(report_dir, "report.txt")
    os.makedirs(report_dir, exist_ok=True)

    spec = importlib.util.spec_from_file_location("student_module", solution_path)
    student_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(student_module)

    PatientManager = student_module.PatientManager
    manager = PatientManager()

    report_lines = [f"\n=== Patient Manager Test Run at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="]

    # Define test cases
    test_cases = [
        {
            "desc": "Create Patient DataFrame",
            "func": "create_patient_df",
            "input": [[101, 'Cardiology', '2023-01-10', '2023-01-13', 450], [102, 'Neurology', '2023-01-11', '2023-01-18', 300]],
            "expected_shape": (2, 5)
        },
        {
            "desc": "Fetch Top 1 Bill",
            "func": "top_n_bills",
            "input": 1,
            "expected_first_id": 101
        },
        {
            "desc": "Stay Duration Categorization",
            "func": "categorize_stay_duration",
            "input": None,
            "expected_col": "Stay Category"
        },
        {
            "desc": "High Billing Patients (Hidden)",
            "func": "get_high_billing_patients",
            "input": 300,
            "expected": [101]
        },
        {
            "desc": "Edge Stay Duration Categorization (Hidden)",
            "func": "categorize_stay_duration",
            "input": None,
            "expected_categories": ["Short Stay", "Normal Stay", "Extended Stay"]
        }
    ]

    edge_cases = [
        {"func": "create_patient_df", "desc": "Function contains only pass"},
        {"func": "top_n_bills", "desc": "Function contains only pass"},
        {"func": "categorize_stay_duration", "desc": "Function contains only pass"},
        {"func": "get_high_billing_patients", "desc": "Function contains only pass"},
        {"func": "create_patient_df", "desc": "Hardcoded return", "input": [[101, 'Cardiology', '2023-01-10', '2023-01-13', 450]], "expected_shape": (1, 5)},
    ]

    # Execute test cases
    for i, case in enumerate(test_cases, 1):
        try:
            edge_case_failed = False
            failing_reason = None

            for edge in edge_cases:
                if edge["func"] != case["func"]:
                    continue
                src = inspect.getsource(getattr(PatientManager, edge["func"])).replace(" ", "").replace("\n", "").lower()
                if "pass" in src and len(src) < 80:
                    edge_case_failed = True
                    failing_reason = "Function contains only pass"
                    break
                if "expected_shape" in edge:
                    manager.create_patient_df(edge["input"])
                    if manager.df.shape == edge["expected_shape"]:
                        if all(k not in src for k in ["dataframe", "columns", "pd."]):
                            edge_case_failed = True
                            failing_reason = "Hardcoded return shape"
                            break

            # Run actual test logic
            if case["func"] == "create_patient_df":
                manager.create_patient_df(case["input"])
                passed = manager.df.shape == case["expected_shape"]
                result = f"Shape={manager.df.shape}"
            elif case["func"] == "top_n_bills":
                result_df = manager.df.sort_values(by='bill_amount', ascending=False).head(case["input"])
                first_id = result_df.iloc[0]['patient_id']
                passed = first_id == case["expected_first_id"]
                result = f"First patient_id={first_id}"
            elif case["func"] == "categorize_stay_duration":
                manager.categorize_stay_duration()
                if "expected_col" in case:
                    passed = "Stay Category" in manager.df.columns
                    result = "Stay Category present" if passed else "Column missing"
                else:
                    unique_cats = manager.df["Stay Category"].unique().tolist()
                    passed = all(cat in unique_cats for cat in case["expected_categories"])
                    result = unique_cats
            elif case["func"] == "get_high_billing_patients":
                result = manager.get_high_billing_patients(case["input"])
                passed = result == case["expected"]

            # Decide final verdict
            if edge_case_failed:
                msg = f"❌ Test Case {i} Failed: {case['desc']} | Reason: Edge case validation failed - {failing_reason}"
            elif passed:
                msg = f"✅ Test Case {i} Passed: {case['desc']} | Result={result}"
            else:
                msg = f"❌ Test Case {i} Failed: {case['desc']} | Result={result}"

            print(msg)
            report_lines.append(msg)

        except Exception as e:
            msg = f"❌ Test Case {i} Crashed: {case['desc']} | Error={str(e)}"
            print(msg)
            report_lines.append(msg)

    with open(report_path, "a", encoding="utf-8") as f:
        f.write("\n".join(report_lines) + "\n")

if __name__ == "__main__":
    solution_file = os.path.join(os.path.dirname(__file__), "..", "student_workspace", "solution.py")
    test_student_code(solution_file)

class PatientManager:
    def __init__(self):
        self.df = pd.DataFrame()

    def create_patient_df(self, data):
        self.df = pd.DataFrame(data, columns=['patient_id', 'department', 'admission_date', 'discharge_date', 'bill_amount'])

    def categorize_stay_duration(self):
        self.df['admission_date'] = pd.to_datetime(self.df['admission_date'])
        self.df['discharge_date'] = pd.to_datetime(self.df['discharge_date'])
        stay_length = (self.df['discharge_date'] - self.df['admission_date']).dt.days
        print(self.df[['check_in', 'discharge']])
        print(stay_length)
        conditions = [
            stay_length <= 3,
            (stay_length > 3) & (stay_length <= 7),
            stay_length > 7
        ]
        choices = ['Short Stay', 'Normal Stay', 'Extended Stay']
        self.df['Stay Category'] = np.select(conditions, choices)