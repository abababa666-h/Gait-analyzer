import pandas as pd
import numpy as np

def get_dashboard_data(mad_threshold=2.5, uploaded_files=None):
    try:
        # 1. 如果用户上传了文件，优先读取上传的文件
        if uploaded_files:
            df_events = None
            df_trial = None
            df_subject = pd.DataFrame()
            
            for file in uploaded_files:
                if "event" in file.name.lower():
                    df_events = pd.read_csv(file)
                elif "trial" in file.name.lower() or "metric" in file.name.lower():
                    df_trial = pd.read_csv(file)
                elif "subject" in file.name.lower():
                    df_subject = pd.read_csv(file)
            
            if df_events is None or df_trial is None:
                return {"status": "error", "message": "上传的文件名不包含 'event' 或 'trial'，请检查。"}
        
        # 2. 如果没上传，就读取文件夹里默认的本地文件
        else:
            df_events = pd.read_csv("gait_events.csv")
            df_trial = pd.read_csv("trial_metrics.csv")
            try:
                df_subject = pd.read_csv("subject_metrics.csv")
            except:
                df_subject = pd.DataFrame()

        # 3. 清理列名空格
        df_events.columns = df_events.columns.str.strip()
        df_trial.columns = df_trial.columns.str.strip()

        # 4. 寻找步时列并计算异常
        step_time_cols = [col for col in df_trial.columns if 'step' in col.lower() and 'time' in col.lower()]
        
        if step_time_cols:
            target_col = step_time_cols[0]
            step_data = df_trial[target_col].dropna()
            
            median_val = np.median(step_data)
            mad_val = np.median(np.abs(step_data - median_val))
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
