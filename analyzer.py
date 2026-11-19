import pandas as pd
import numpy as np

def get_dashboard_data(mad_threshold=2.5):
    try:
        # 1. 读取三个文件
        df_events = pd.read_csv("gait_events.csv")
        df_trial = pd.read_csv("trial_metrics.csv")
        try:
            df_subject = pd.read_csv("subject_metrics.csv")
        except:
            df_subject = pd.DataFrame()

        # 2. 清理列名两端的空格
        df_events.columns = df_events.columns.str.strip()
        df_trial.columns = df_trial.columns.str.strip()

        # 3. 寻找步时列
        step_time_cols = [col for col in df_trial.columns if 'step' in col.lower() and 'time' in col.lower()]
        
        if step_time_cols:
            target_col = step_time_cols[0]
            step_data = df_trial[target_col].dropna()
            
            # 4. 计算中位数和 MAD
            median_val = np.median(step_data)
            mad_val = np.median(np.abs(step_data - median_val))
            
            # 5. 根据传入的滑块参数计算阈值并标记异常
            threshold = mad_threshold * mad_val if mad_val > 0 else 0.1
            df_trial['是否异常'] = np.abs(df_trial[target_col] - median_val) > threshold
        else:
            df_trial['是否异常'] = False

        return {
            "status": "success",
            "events": df_events,
            "trial": df_trial,
            "subject": df_subject
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}