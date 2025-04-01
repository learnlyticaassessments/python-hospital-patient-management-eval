
# Placeholder solution.py
# solution.py

import pandas as pd
import numpy as np

class PatientManager:
    def __init__(self):
        self.df = pd.DataFrame()

    def create_patient_df(self, patient_data: list):
        self.df = pd.DataFrame(patient_data, columns=['patient_id', 'department', 'check_in', 'discharge', 'bill_amount'])
        self.df['check_in'] = pd.to_datetime(self.df['check_in'])
        self.df['discharge'] = pd.to_datetime(self.df['discharge'])
        return self.df

    def top_n_bills(self, n: int):
        return self.df.sort_values(by='bill_amount', ascending=False).head(n)

    def categorize_stay_duration(self):
        # Ensure 'check_in' and 'discharge' are datetime
        self.df['check_in'] = pd.to_datetime(self.df['check_in'], errors='coerce')
        self.df['discharge'] = pd.to_datetime(self.df['discharge'], errors='coerce')

        # Calculate stay length
        stay_length = (self.df['discharge'] - self.df['check_in']).dt.days

        # Handle invalid or missing dates
        stay_length = stay_length.fillna(-1)  # Assign -1 for invalid dates

        # Define conditions and choices
        conditions = [
            stay_length <= 3,
            (stay_length > 3) & (stay_length <= 7),
            stay_length > 7
        ]
        choices = ['Short Stay', 'Normal Stay', 'Extended Stay']

        # Assign categories with a default for invalid cases
        self.df['Stay Category'] = np.select(conditions, choices, default='Invalid Stay')

        return self.df

    def get_high_billing_patients(self, t: int):
        return self.df[self.df['bill_amount'] > t]['patient_id'].tolist()